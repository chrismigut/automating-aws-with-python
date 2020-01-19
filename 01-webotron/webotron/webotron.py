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

session = None
bucket_manager = None

@click.group()
@click.option('--profile', default=None, help="Use a given AWS profile.")
def cli(profile):
    """Webotron deploys websites to AWS."""
    global session, bucket_manager
    session_cfg = {}
    if profile:
        session_cfg['profile_name'] = profile
    else:
        session_cfg['profile_name'] = 'pythonAutomation'
    session = boto3.Session(**session_cfg) # glob that will un wrap to fit func
    bucket_manager = BucketManager(session)


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


@cli.command('setup-bucket')
@click.argument('bucket', nargs=1)
def setup_bucket(bucket):
    """Create and configure s3 bucket."""
    s3_bucket = bucket_manager.init_bucket(bucket)
    bucket_manager.set_policy(s3_bucket)
    bucket_manager.configure_website(s3_bucket)


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket', nargs=1)
def sync(pathname, bucket):
    """Sync contents of PATHNAME to BUCKET."""
    bucket_manager.sync(pathname, bucket)


# Need if __name__ == '__main__: if we are running code as a script'
if __name__ == '__main__':
    cli()


# Grouping commands under cli
# click.group
#   -> cli.command(list-buckets)

# orginal profile was pythonAutomation
