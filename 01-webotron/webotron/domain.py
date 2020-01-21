# -*- coding: utf-8 -*-

"""Classes for Route 53 domains."""

import uuid
from pprint import pprint

from util import UtilManager

class DomainManager:
    """Manage a Route 53 domain."""

    def __init__(self, session):
        """Create DomainManger object."""
        self.session = session
        self.route53_client = self.session.client('route53')
        self.util_manager = UtilManager()
    def find_hosted_zone(self, domain_name):
        print(domain_name)
        """Return list of hosted zones."""
        paginator = self.route53_client.get_paginator('list_hosted_zones')
        for page in paginator.paginate():
            for zone in page['HostedZones']:
                if domain_name.endswith(zone['Name'][:-1]):
                    pprint(zone)
                    return zone
        return None

    def create_hosted_zone(self, domain_name):
        """Return a newly created hosted zone given domain name."""
        # domain_name = subdomain.domain.zone.net
        # zone_name = zone.net.
        zone_name = '.'.join(domain_name.split('.')[-2:]) + '.'
        return self.route53_client.create_hosted_zone(
            Name=zone_name,
            CallerReference=str(uuid.uuid4())
        )

    def create_s3_doamin_record(self, zone, domain_name, endpoint):
        return self.route53_client.change_resource_record_sets(
            HostedZoneId=zone['Id'],
            ChangeBatch={
                'Comment': 'Created by webotron.',
                'Changes': [{
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': domain_name,
                        'Type': 'A',
                        'AliasTarget': {
                            'HostedZoneId': endpoint.zone,
                            'DNSName': endpoint.host,
                            'EvaluateTargetHealth': False
                        }
                    }
                }]
            }
        )



        response = client.change_resource_record_sets(

    ChangeBatch={
        'Comment': 'string',
        'Changes': [
            {
                'Action': 'CREATE'|'DELETE'|'UPSERT',
                'ResourceRecordSet': {
                    'Name': 'string',
                    'Type': 'SOA'|'A'|'TXT'|'NS'|'CNAME'|'MX'|'NAPTR'|'PTR'|'SRV'|'SPF'|'AAAA'|'CAA',
                    'SetIdentifier': 'string',
                    'Weight': 123,
                    'Region': 'us-east-1'|'us-east-2'|'us-west-1'|'us-west-2'|'ca-central-1'|'eu-west-1'|'eu-west-2'|'eu-west-3'|'eu-central-1'|'ap-southeast-1'|'ap-southeast-2'|'ap-northeast-1'|'ap-northeast-2'|'ap-northeast-3'|'eu-north-1'|'sa-east-1'|'cn-north-1'|'cn-northwest-1'|'ap-east-1'|'me-south-1'|'ap-south-1',
                    'GeoLocation': {
                        'ContinentCode': 'string',
                        'CountryCode': 'string',
                        'SubdivisionCode': 'string'
                    },
                    'Failover': 'PRIMARY'|'SECONDARY',
                    'MultiValueAnswer': True|False,
                    'TTL': 123,
                    'ResourceRecords': [
                        {
                            'Value': 'string'
                        },
                    ],
                    'AliasTarget': {
                        'HostedZoneId': 'string',
                        'DNSName': 'string',
                        'EvaluateTargetHealth': True|False
                    },
                    'HealthCheckId': 'string',
                    'TrafficPolicyInstanceId': 'string'
                }
            },
        ]
    }
)
