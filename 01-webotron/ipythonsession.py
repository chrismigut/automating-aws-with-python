# coding: utf-8

"""Loads session information for aws cli to be used in terminal."""

import boto3
session = boto3.Session(profile_name='pythonAutomation')
s3 = session.resource('s3')
# for bucket in s3.buckets.all():
#     print(bucket)
#
# ec2_client = session.client('ec2')
# type(ec2_client)
