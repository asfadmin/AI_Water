import os
import re
import shutil
from datetime import datetime
from subprocess import call
from zipfile import ZipFile
from src.geo_utility import create_water_mask

from src.api_functions import download_products, grab_subscription
from src.user_class import User


class Mask:
    def __init__(self, user: User, mask_name, start_time, end_time):
        self.ZIP_REGEX = re.compile(r'(.*).zip')  # Move these?
        self.SAR_REGEX = re.compile(r'(.*)_(VH|VV).tif')  # Move these?
        self.start_time = start_time
        self.end_time = end_time

        self.user = user
        self.mask_name = mask_name
        self.products = []
        subscription = grab_subscription(self.user.api)
        self.subscription_id = subscription["id"]

    def mask_subscription(self):
        count = 0
        while True:
            print(f"Page: {count + 1}")
            response = self.user.api.get_products(
                sub_id=self.subscription_id, page=count, page_size=500
            )

            for product in response:
                if product_in_time_bounds(product['granule'], self.start_time, self.end_time):
                    self.products.append(product)


            # self.products = triage_products(self.products)

            self._mask_products()
            count += 1

            if not self.products:
                break

    def _get_product_metadata(self, product):
        m = re.match(self.ZIP_REGEX, product)
        product_name = m.groups()[0]

        for file in os.listdir(product_name):
            img = os.path.join(product_name, file)
            m = re.match(self.SAR_REGEX, file)

            if not m or file.endswith('.xml'):
                remove_img(img)
                continue

            _, band = m.groups()

            if band == "VH":
                vh_img = img
                continue
            vv_img = img

        return vv_img, vh_img, product_name

    def _mask_product(self, product_zip_name, product_count):
        vv_img, vh_img, product_name = self._get_product_metadata(product_zip_name)
        output = os.path.join(self.user.mask_path, f"{product_name}_{product_count}.tif")
        # Creating mask
        # call(f"python scripts/create_mask.py {self.user.model_path} {vv_img} {vh_img} {output}".split())
        create_water_mask(self.user.model_path, vv_img, vh_img, output)
        shutil.rmtree(product_name)
        os.remove(f"{product_name}.zip")

    def _mask_products(self) -> None:
        for product_count, product in enumerate(self.products):
            download_products(self.products, product_count, product)
            product_zip_name = product["name"]
            if not extract_zip(product_zip_name):
                continue

            self._mask_product(product_zip_name, product_count)


def product_middle_time(product_name):
    """takes in product time; uses regex to take out the date/time of the file name
    then returns a date time object of middle time between the start and end times"""
    product_time_regex = re.compile(
        r"S.*1SDV_(?P<start_year>\d{4})(?P<start_month>\d{2})(?P<start_day>\d{2})T(?P<start_hour>\d{2})("
        r"?P<start_minute>\d{2})(?P<start_second>\d{2})_(?P<end_year>\d{4})(?P<end_month>\d{2})(?P<end_day>\d{2})T("
        r"?P<end_hour>\d{2})(?P<end_minute>\d{2})(?P<end_second>\d{2})_[0-9]*_.*.zip")

    regex_match = re.match(product_time_regex, product_name)
    time_dict = regex_match.groupdict()

    # converts all dates/times values in dictionary from int to string
    for k, v in time_dict.items(): time_dict[k] = int(v)

    start = datetime(time_dict["start_year"], time_dict["start_month"], time_dict["start_day"],
                     time_dict["start_hour"], time_dict["start_minute"], time_dict["start_second"])

    end = datetime(time_dict["end_year"], time_dict["end_month"], time_dict["end_day"],
                   time_dict["end_hour"], time_dict["end_minute"], time_dict["end_second"])

    # calculates middle datetime
    middle = start + (end - start) / 2

    return middle


def triage_products(products):
    """Takes list of dictionary (products), and then orders them from
    least to most recent based on their start time"""
    return sorted(products, key=lambda product: product_middle_time(product['name']))


def extract_zip(product_zip_name):
    try:
        with ZipFile(product_zip_name, 'r') as zf:
            zf.extractall()
        zf.close()
        return True
    except FileNotFoundError:
        return False


def remove_img(img_path):
    try:
        os.remove(img_path)
        return True
    except FileNotFoundError and IsADirectoryError:
        return False

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