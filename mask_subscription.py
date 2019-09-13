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
import zipfile
from argparse import ArgumentParser, Namespace
from typing import List

from asf_hyp3 import API
from create_mask import main as mask_product
from scripts.make_vrt import main as vrt
from src.api_functions import download_prouducts, grab_subscription, hyp3_login


def make_dirs(dir: str) -> str:
    """ If not already created this function creates the mask directory,
        and the directory the user inputs. The mask directory will contain
        subdirectories containing all the masks within
        individual subdirectories. Subdirectories are created each time
        the script is ran. """

    users_dir = os.path.join('mask', dir)
    if not os.path.isdir('mask'):
        os.mkdir('mask')
    if not os.path.isdir(users_dir):
        os.mkdir(users_dir)
    return users_dir


def mask_products(products: List, users_path: str, model_path: str) -> None:
    """ Takes a list of products generated from the HYP3 API,
        the path to save the masks, and the path to a model (.h5 file).
        The function then creates a mask for each product contained in
        the product list. """

    ZIP_REGEX = re.compile(r'(.*).zip')
    SAR_REGEX = re.compile(r'(.*)_(VH|VV).tif')
    for i, product in enumerate(products):
        download_prouducts(products, i, product)
        try:
            zf = zipfile.ZipFile(product['name'], 'r')
            zf.extractall()
            zf.close()
        except FileNotFoundError:
            continue

        m = re.match(ZIP_REGEX, product['name'])
        folder = m.groups()

        for file in os.listdir(folder[0]):
            img = os.path.join(folder[0], file)
            m = re.match(SAR_REGEX, file)

            if not m or file.endswith('.xml'):
                try:
                    os.remove(img)
                    continue
                except FileNotFoundError and IsADirectoryError:
                    continue

            _, band = m.groups()

            if band == "VH":
                vh_img = img
                continue
            vv_img = img

        output = os.path.join(users_path, f"{folder[0]}_{i}.tif")
        mask_product(model_path, vv_img, vh_img, output)
        shutil.rmtree(folder[0])
        os.remove(f"{folder[0]}.zip")


def mask_sub(sub_id: str, dir: str, model: str,  api: API) -> None:
    """ mask_sub masks a given subscription  """
    count = 0
    while True:
        print(f"Page: {count + 1}")
        products = api.get_products(
            sub_id=sub_id, page=count, page_size=500
        )
        mask_products(products, dir, model)
        count += 1

        if not products:
            break


def main(args: Namespace, api: API) -> None:
    """ main creates a vrt from a users subscription. """
    subscription = grab_subscription(api)
    dir = make_dirs(args.name)
    mask_sub(subscription['id'], dir, args.model, api)
    vrt(dir, f"{args.name}.vrt")


if __name__ == '__main__':
    p = ArgumentParser()
    sp = p.add_subparsers()

    create = sp.add_parser('create', help='Create a mask')
    create.add_argument('name', help='Name of mask')
    create.add_argument('model', help='Path to model')
    create.set_defaults(func=main)

    args = p.parse_args()
    if hasattr(args, 'func'):
        api = hyp3_login()
        args.func(args, api)
    else:
        p.print_help()
