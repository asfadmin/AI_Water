"""
 McKade Sorensen
 8-20-19
 mask_subscription.py
 This script creates a mask from an ASF HYP3 subscription. The user must
 already have a subscription in HYP3 with finished products.
"""
import time
from argparse import ArgumentParser, Namespace

from asf_hyp3 import API

from scripts.make_vrt import main as vrt
from src.api_functions import hyp3_login
from src.user_class import User
from src.mask_class import Mask


def create_mask(args: Namespace, api: API) -> None:
    start_time = time.time()

    user = User(args.name, args.model, api)
    mask = Mask(user, args.name)

    mask.mask_subscription()
    vrt(mask.user.mask_path, f"{mask.mask_name}.vrt")

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
