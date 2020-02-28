"""
 McKade Sorensen
 8-20-19
 mask_subscription.py
 This script creates a mask from an ASF HYP3 subscription. The user must
 already have a subscription in HYP3 with finished products.
"""
import os
import re
import shutil
import time
from argparse import ArgumentParser, Namespace
from subprocess import call
from zipfile import ZipFile

from asf_hyp3 import API

from scripts.make_vrt import main as vrt
from src.api_functions import download_prouducts, grab_subscription, hyp3_login


class User:

    def __init__(self, mask_path: str, model_path: str, api: API):
        self.mask_path = mask_path
        self.model_path = model_path

        self._make_dirs(mask_path)
        self.api = api

    def _make_dirs(self) -> str:
        self.mask_path = os.path.join('mask', self.mask_path)
        if not os.path.isdir('mask'):
            os.mkdir('mask')
        if not os.path.isdir(self.mask_path):
            os.mkdir(self.mask_path)


class Mask:

    def __init__(self, user: User):
        self.ZIP_REGEX = re.compile(r'(.*).zip')  # Move these?
        self.SAR_REGEX = re.compile(r'(.*)_(VH|VV).tif')  # Move these?

        self.user = user
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

    def _mask_products(self) -> None:
        for i, product in enumerate(self.products):
            download_prouducts(self.products, i, product)

            if not extract_zip(product["name"]):
                continue

            vv_img, vh_img, product_name = self._get_product_metadata(product['name'])

            output = os.path.join(self.user.users_path, f"{product_name}_{i}.tif")
            # Creating mask
            call(f"python scripts/create_mask.py {self.user.model_path} {vv_img} {vh_img} {output}".split())
            shutil.rmtree(product_name)
            os.remove(f"{product_name}.zip")


def extract_zip(product_name):
    try:
        with ZipFile(product_name, 'r') as zf:
            zf.extractall()
        zf.close()
        return True
    except FileNotFoundError:
        return False


def remove_img(img_path):
    try:
        os.remove(img_path)
    except FileNotFoundError and IsADirectoryError:
        pass


def create_mask(args: Namespace, api: API) -> None:
    start_time = time.time()
    user = User(args.name, args.model, api)
    mask = Mask(user)
    mask.mask_subscription()
    vrt(mask.user.mask_path, f"{args.name}.vrt")
    end_time = time.time()
    print(end_time - start_time)


if __name__ == '__main__':
    p = ArgumentParser()

    p.add_argument('model', help='Path to model')
    p.add_argument('name', help='Name of mask')
    p.set_defaults(func=create_mask)

    args = p.parse_args()
    if hasattr(args, 'func'):
        api = hyp3_login()
        args.func(args, api)
    else:
        p.print_help()
