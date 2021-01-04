"""
 Created By:   Jason Herning
 Date Created: 12-16-2020
 File Name:    test_metadata_class.py
 Description:  class to hold product metadata
"""

import json
from typing import List

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

    def time_bounds(self, start, end):
        return self.start > start and self.end < end

    def intersects(self, aoi: Polygon):
        # if aoi is None:
        #     return False
        return self.shape.intersects(aoi)

    def get_shape_cmr(self):
        payload = {'provider': 'ASF',
                   'producer_granule_id': self.granule,
                   'page_size': 100}

        response = requests.post(CMR_URL, data=payload)

        entrys = response.json()['feed']['entry']
        if len(entrys) == 0:
            return None

        entry = entrys[0]
        self.shape = Polygon(format_points(entry['polygons'][0][0]))

    def to_json(self):
        metadata = asdict(self)
        metadata['start'] = self.start.isoformat()
        metadata['end'] = self.end.isoformat()
        metadata['shape'] = str(self.shape)

        return json.dumps(metadata)


# @dc.dataclass()
# class MaskMetadata:
#     """Designed to hold product metadata"""
#
#     name: str
#     model: str
#     products: list = None
#     aoi: Polygon = None
#     start: datetime = None
#     end: datetime = None
#     description: str = None
#
#
#
#     def to_json(self):
#         metadata = asdict(self)
#         return json.dumps(metadata)


def triage_products_newest(products: List[Product]):
    """Takes list of products, and then orders them from
    least to most recent based on their start time"""
    return sorted(products, key=lambda product: product.start)


def format_points(point_string):
    converted_to_float = [float(x) for x in point_string.split(' ')]
    points = [list(t) for t in zip(converted_to_float[1::2], converted_to_float[::2])]
    return points


def get_sub_products(api, sub_id):
    """returns all products in subscription as Product objects """
    response = api.get_products(sub_id=sub_id)

    products = []
    for product in response:
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
    sorted_products = reversed(triage_products_newest(products))


    for product in sorted_products:

        percent_exposed = round(percentage(dif.area, aoi.area))
        print(f"{percent_exposed} area percentage uncovered")
        if percent_exposed == 0:
            return min_products

        intersect_dif = product.shape.intersection(dif)

        print(f"intersection area = {intersect_dif.area}")
        if product.shape.intersects(dif):
            print(f"inserted percent covered = {percent_exposed}")
            min_products.insert(0, product)
            dif = dif - intersect_dif

        # min_products.insert(0, product)
        # intersect_aoi = product.shape.intersection(aoi)





    return min_products


# def populate_cmr_product_shape(*products: Product):
#     for product in products:
#         payload = {'provider': 'ASF',
#                    'producer_granule_id': product.granule,
#                    'page_size': 100}
#
#         response = requests.post(CMR_URL, data=payload)
#
#         entrys = response.json()['feed']['entry']
#         if len(entrys) == 0:
#             return None
#
#         entry = entrys[0]
#         shape = Polygon(format_points(entry['polygons'][0][0]))
#
#         yield shape

def populate_cmr_product_shape(product: Product):
    payload = {'provider': 'ASF',
               'producer_granule_id': product.granule,
               'page_size': 100}

    response = requests.post(CMR_URL, data=payload)

    entrys = response.json()['feed']['entry']
    if len(entrys) == 0:
        return None

    entry = entrys[0]
    shape = Polygon(format_points(entry['polygons'][0][0]))
    product.shape = shape
    return shape

