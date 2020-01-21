#!/usr/bin/python
# -*- coding: utf-8 -*-

# doc string: what is the goal of this script
"""
Webotron: Deploy websites with AWS.

Webotron automates the process of deploying static websites to aws.
- Configure AWS S3 buckets
    - Creating them
    - Set them up for static website hosting
    - Deploy local files to them
- Configure DNS with AWS Route53
- Configure a Content Delivery Network and SSL with AWS
"""

import boto3
import click

from bucket import BucketManager
from domain import DomainManager
from util import UtilManager

from pprint import pprint


from botocore.exceptions import ClientError

session = None
bucket_manager = None
domain_manager = None
util_manager = None


@click.group()
@click.option('--profile', default=None, help="Use a given AWS profile.")
def cli(profile):
    """Webotron deploys websites to AWS."""
    global session, bucket_manager, domain_manager, util_manager
    session_cfg = {}
    if profile:
        session_cfg['profile_name'] = profile
    else:
        session_cfg['profile_name'] = 'pythonAutomation'
    session = boto3.Session(**session_cfg)  # glob that will unwrap to fit func
    bucket_manager = BucketManager(session)
    domain_manager = DomainManager(session)
    util_manager = UtilManager()


@cli.command('list-buckets')
def list_buckets():
    """List all s3 buckets."""
    for bucket in bucket_manager.all_buckets():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket', nargs=1)
def list_bucket_objects(bucket):
    """List objects in an s3 bucket."""
    for obj in bucket_manager.all_objects(bucket):
        print(obj)

def _setup_bucket(bucket):
    """Create and configure s3 bucket."""
    s3_bucket = bucket_manager.init_bucket(bucket)
    bucket_manager.set_policy(s3_bucket)
    bucket_manager.configure_website(s3_bucket)

@cli.command('setup-bucket')
@click.argument('bucket', nargs=1)
def setup_bucket(bucket):
    """Create and configure s3 bucket."""
    _setup_bucket(bucket)




@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket', nargs=1)
def sync(pathname, bucket):
    """Sync contents of PATHNAME to BUCKET."""
    bucket_manager.sync(pathname, bucket)
    print(bucket_manager.get_bucket_url(bucket_manager.s3.Bucket(bucket)))

def _setup_domain(domain):
    """Configure DOMAIN to point to BUCKET."""
    try:
        bucket = bucket_manager.get_bucket(domain)
        bucket_name = bucket_manager.get_bucket(bucket).name

        zone = domain_manager.find_hosted_zone(domain) \
            or domain_manager.create_hosted_zone(domain)

        endpoint = util_manager.get_endpoint(bucket_manager.get_region_name(bucket_name))

        a_record = domain_manager.create_s3_doamin_record(zone, domain, endpoint)
    except ClientError as error:
        if error.response['Error']['Code'] == 'NoSuchBucket':
            _setup_bucket(domain)
            _setup_domain(domain)
    print("Domain configured: http://{}".format(domain))


@cli.command('setup-domain')
@click.argument('domain')
def setup_domain(domain):
    """Configure DOMAIN to point to BUCKET."""
    _setup_domain(domain)

# Need if __name__ == '__main__: if we are running code as a script'
if __name__ == '__main__':
    cli()


# Grouping commands under cli
# click.group
#   -> cli.command(list-buckets)

# orginal profile was pythonAutomation
