import os
import re
import shutil
from datetime import datetime
from subprocess import call
from zipfile import ZipFile

from src.api_functions import download_products, grab_subscription
from src.user_class import User


class Mask:
    def __init__(self, user: User, mask_name):
        self.ZIP_REGEX = re.compile(r'(.*).zip')  # Move these?
        self.SAR_REGEX = re.compile(r'(.*)_(VH|VV).tif')  # Move these?

        self.user = user
        self.mask_name = mask_name
        self.products = []
        subscription = grab_subscription(self.user.api)
        self.subscription_id = subscription["id"]

    def mask_subscription(self):
        count = 0
        while True:
            print(f"Page: {count + 1}")
            self.products = self.user.api.get_products(
                sub_id=self.subscription_id, page=count, page_size=500
            )

            self.products = triage_products(self.products)

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
        call(f"python scripts/create_mask.py {self.user.model_path} {vv_img} {vh_img} {output}".split())
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
    PRODUCT_REGEX = re.compile(
        r'S.*1SDV_(?P<start_year>\d{4})(?P<start_month>\d{2})(?P<start_day>\d{2})T(?P<start_hour>\d{2})(?P<start_minute>\d{2})(?P<start_second>\d{2})_(?P<end_year>\d{4})(?P<end_month>\d{2})(?P<end_day>\d{2})T(?P<end_hour>\d{2})(?P<end_minute>\d{2})(?P<end_second>\d{2})_[0-9]*_.*.zip')

    m = re.match(PRODUCT_REGEX, product_name)
    dt = m.groupdict()

    # converts all dates/times values in dictionary from int to string
    for k, v in dt.items(): dt[k] = int(v)

    start = datetime(dt["start_year"], dt["start_month"], dt["start_day"],
                     dt["start_hour"], dt["start_minute"], dt["start_second"])

    end = datetime(dt["end_year"], dt["end_month"], dt["end_day"],
                   dt["end_hour"], dt["end_minute"], dt["end_second"])

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
