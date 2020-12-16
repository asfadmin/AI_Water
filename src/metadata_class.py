"""
 Created By:   Jason Herning
 Date Created: 12-16-2020
 File Name:    test_metadata_class.py
 Description:  class to hold product metadata
"""


import json
import requests
import re
from copy import copy
from datetime import datetime

import dataclasses as dc
from dataclasses import asdict
from shapely.geometry import Polygon

CMR_URL = 'https://cmr.earthdata.nasa.gov/search/granules.json'


@dc.dataclass()
class Product:
    """Designed to hold product metadata"""

    name: str
    granule: str = None
    url: str = None
    shape: Polygon = None
    start: datetime = None
    end: datetime = None

    def __post_init__(self):
        self.start = self.__make_start()
        self.end = self.__make_end()

    def __make_start(self):
        start_time = re.findall(r"[0-9]{8}T[0-9]{6}", self.granule)[0]
        return datetime.strptime(start_time, "%Y%m%dT%H%M%S")

    def __make_end(self):
        end_time = re.findall(r"[0-9]{8}T[0-9]{6}", self.granule)[1]
        return datetime.strptime(end_time, "%Y%m%dT%H%M%S")

    def to_json(self):
        metadata = asdict(self)
        metadata['start'] = self.start.isoformat()
        metadata['end'] = self.end.isoformat()
        metadata['shape'] = str(self.shape)

        return json.dumps(metadata)


def format_points(point_string):
    converted_to_float = [float(x) for x in point_string.split(' ')]
    points = [list(t) for t in zip(converted_to_float[1::2], converted_to_float[::2])]
    return points


def product_time(product_name):
    product_time_regex = re.compile(
        r"S.*1SDV_(?P<start_year>\d{4})(?P<start_month>\d{2})(?P<start_day>\d{2})T(?P<start_hour>\d{2})("
        r"?P<start_minute>\d{2})(?P<start_second>\d{2})_(?P<end_year>\d{4})(?P<end_month>\d{2})(?P<end_day>\d{2})T("
        r"?P<end_hour>\d{2})(?P<end_minute>\d{2})(?P<end_second>\d{2})_*")

    regex_match = re.match(product_time_regex, product_name)
    time_dict = regex_match.groupdict()

    # converts all dates/times values in dictionary from int to string
    for k, v in time_dict.items():
        time_dict[k] = int(v)

    start = datetime(time_dict["start_year"], time_dict["start_month"], time_dict["start_day"],
                     time_dict["start_hour"], time_dict["start_minute"], time_dict["start_second"])

    end = datetime(time_dict["end_year"], time_dict["end_month"], time_dict["end_day"],
                   time_dict["end_hour"], time_dict["end_minute"], time_dict["end_second"])

    return start, end


def product_in_time_bounds(product_name, start, end):
    prod_start, prod_end = product_time(product_name)

    return prod_start > start and prod_end < end


def get_sub_products(api, sub_id, start, end):
    response = api.get_products(sub_id=sub_id)

    products = []
    for product in response:
        if product_in_time_bounds(product['granule'], start, end):
            products.append(Product(product['name'],
                                    product['granule'],
                                    product['url']
                                    )
                            )
    return products


def percentage(part, whole):
    return 100 * float(part) / float(whole)


def get_min_granule_coverage(products: list, aoi: Polygon) -> list:
    """Input list of Product objects and a target Polygon.
       returns the minimum prodcuts needed to cover the AOI.
       Gives prefereance to the most recently created Products."""

    dif = copy(aoi)
    min_products = []

    for current in reversed(products):
        #         print(current.name)
        print(dif.area)

        if round(percentage(dif.area, aoi.area)) == 1:
            return min_products

        current_shape = current.shape
        intersect = current_shape.intersection(aoi)
        min_products.insert(0, current)
        dif = dif - intersect

    return min_products


def get_cmr_granule_shape(name: str):
    payload = {'provider': 'ASF',
               'producer_granule_id': name,
               'page_size': 100}

    response = requests.post(CMR_URL, data=payload)

    entrys = response.json()['feed']['entry']
    if len(entrys) == 0:
        return None

    entry = entrys[0]
    shape = Polygon(format_points(entry['polygons'][0][0]))

    return shape

