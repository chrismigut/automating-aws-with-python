"""Common Resources."""

# https://stackoverflow.com/questions/2970608/what-are-named-tuples-in-python

from pathlib import Path
from collections import namedtuple

import re
import pandas as pd


class UtilManager:
    """Helper class with common tasks."""

    def __init__(self):
        """Init UtilManager."""
        self.region_to_endpoints = {}
        self.load__regions_supported_by_s3()

    @staticmethod
    def load_csv_file(file):
        """Return records from csv file as a panda dataframe."""
        path = Path(file).absolute()
        return pd.read_csv(path)

    @staticmethod
    def find_regions_supported_by_s3_pattern():
        """Regx pattern to find region in url given by s3 hostname."""
        pattern = r's3-website[\.|\-](.*)[\.|\-]amazonaws'
        return re.compile(pattern)

    def load__regions_supported_by_s3(self):
        """Parse the s3 dataframe into name, host, zone as Endpoint obj."""
        dataframe = self.load_csv_file('.\webotron\s3_bucket_endpoints.csv')
        pattern = self.find_regions_supported_by_s3_pattern()

        Endpoint = namedtuple('Endpoint', ['name', 'host', 'zone'])

        for row in dataframe.itertuples():
            match = pattern.match(row[2])
            if match:
                region_name = match.group(1)
                self.region_to_endpoints[region_name] = Endpoint(row[1], row[2], row[3])
            else:
                print(f'Error, unable to parse row.\n\t{row}')

    def know_region(self, region):
        """Return true if this is a known region."""
        return region in self.region_to_endpoints

    def get_endpoint(self, region):
        """Return hosted endpoint of s3 bucket given region name."""
        return self.region_to_endpoints[region]
