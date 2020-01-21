# -*- coding: utf-8 -*-


"""Classes for S3 Buckets."""
import boto3

from pathlib import Path
import mimetypes
from functools import reduce

from botocore.exceptions import ClientError
from hashlib import md5
from util import UtilManager


class BucketManager:
    """Manage an S3 Bucket."""

    CHUNK_SIZE = 8388608

    def __init__(self, session):
        """Create a BucketManager object."""
        self.session = session
        self.s3 = self.session.resource('s3')
        self.util_manager = UtilManager()
        self.transfer_config = boto3.s3.transfer.TransferConfig(
            multipart_chunksize=self.CHUNK_SIZE,
            multipart_threshold=self.CHUNK_SIZE
        )
        self.manifest = {}

    def get_bucket(self, bucket_name):
        """Get bucket name."""
        return self.s3.Bucket(bucket_name)

    def get_region_name(self, bucket):
        """Get the bucket's region name."""
        client = self.s3.meta.client
        bucket_location = client.get_bucket_location(Bucket=bucket.name)
        return bucket_location["LocationConstraint"] or 'us-east-1'

    def get_bucket_url(self, bucket):
        """Get bucket url given region."""
        return "http://{}.{}".format(
            bucket.name,
            self.util_manager.get_endpoint(self.get_region_name(bucket)).host
            )

    def all_buckets(self):
        """Get an interator for all buckets."""
        return self.s3.buckets.all()

    def all_objects(self, bucket):
        """Get an interator for all objects in a bucket."""
        return self.s3.Bucket(bucket).objects.all()

    def init_bucket(self, bucket_name):
        """Create new bucket, or return existing S3 Bucket based on name."""
        s3_bucket = None
        try:
            s3_bucket = self.s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': self.session.region_name
                })
        except ClientError as error:
            if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                print('Bucket already created')
                s3_bucket = self.s3.Bucket(bucket_name)
            else:
                raise error
        return s3_bucket

    @staticmethod
    def set_policy(bucket):
        """Set bucket policy to be readable by everyone."""
        policy = """
        {
          "Version":"2012-10-17",
          "Statement":[
            {
              "Sid":"PublicRead",
              "Effect":"Allow",
              "Principal": "*",
              "Action":["s3:GetObject"],
              "Resource":["arn:aws:s3:::%s/*"]
            }
          ]
        }
        """ % bucket.name
        policy = policy.strip()

        pol = bucket.Policy()
        pol.put(Policy=policy)

    @staticmethod
    def configure_website(bucket):
        """Configure S3 bucket for static website hosting."""
        bucket.Website().put(WebsiteConfiguration={
            'ErrorDocument': {
                'Key': 'error.html'
            },
            'IndexDocument': {
                'Suffix': 'index.html'
            }
        })

    def load_manifest(self, bucket):
        """Load manifest for caching purposes from s3 bucket."""
        paginator = self.s3.meta.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket.name):
            for obj in page.get('Contents', []):
                self.manifest[obj['Key']] = obj['ETag']

    @staticmethod
    def hash_data(data):
        """Generate md5 for data."""
        hash = md5()
        hash.update(data)
        return hash

    def generate_etag(self, path):
        """Generate etag for file."""
        hashes = []

        with open(path, 'rb') as file:
            while True:
                data = file.read(self.CHUNK_SIZE)

                if not data:
                    break

                hashes.append(self.hash_data(data))

        if not hashes:
            return
        elif len(hashes) == 1:
            return '"{}"'.format(hashes[0].hexdigest())
        else:
            # append the hashes from list of hashes and then hash those together
            hash = self.hash_data(reduce(lambda x, y: x + y, (h.digest() for h in hashes)))
            return '"{}-{}"'.format(hash.hexdigest(), len(hashes))

    # Since this is not dependent on bucket_manager
    def upload_file(self, bucket, path, key):
        """Upload file (provided a key:path) to an s3 bucket."""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'

        # check to see if current version of file has already been uploaded
        etag = self.generate_etag(path)
        if self.manifest.get(key, '') == etag:
            return

        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
            },
            Config=self.transfer_config
        )

    def sync(self, pathname, bucket_name):
        """Upload files from from specified path to S3 bucket."""
        bucket = self.s3.Bucket(bucket_name)
        self.load_manifest(bucket)

        root = Path(pathname).expanduser().resolve()

        def handle_directory(target):
            for path in target.iterdir():
                if path.is_dir():
                    handle_directory(path)
                if path.is_file():
                    self.upload_file(bucket,
                                     str(path),
                                     str(path.relative_to(root)))

        handle_directory(root)
