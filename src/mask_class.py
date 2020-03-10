import os
import re
from zipfile import ZipFile
import shutil
from subprocess import call

from .api_functions import download_prouducts, grab_subscription
from .user_class import User


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

        output = os.path.join(self.user.users_path, f"{product_name}_{product_count}.tif")
        # Creating mask
        call(f"python scripts/create_mask.py {self.user.model_path} {vv_img} {vh_img} {output}".split())
        shutil.rmtree(product_name)
        os.remove(f"{product_name}.zip")

    def _mask_products(self) -> None:
        for product_count, product in enumerate(self.products):
            download_prouducts(self.products, product_count, product)
            product_zip_name = product["name"]

            if not extract_zip(product_zip_name):
                continue

            self._mask_product(product_zip_name, product_count)


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
