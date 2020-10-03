"""
 Created By:   ???
 Date Started: ???
 Last Updated: 07-21-2020
 File Name:    make_data.py
 Description:  scripts for creating and compressing datasets
"""

import os
import random
import re
import shutil
from argparse import ArgumentParser, Namespace
from datetime import date

from scripts.etl_water_mark import main as etl_wm
from scripts.prepare_data import move_imgs, prepare_data
from src.asf_cnn import test_model_masked
from src.model import load_model
from src.plots import edit_predictions
from scripts.water_mark import setup_data


# TODO: does the exact same thing as prepare_mask_data in prepare_data!!!; STAY DRY
def div_imgs(dir_path: str, holdout: int) -> None:
    """ Creates a test and train folder. The image names need
    to be cleaned up unlike the prepare_data function in prepare_data.py """
    VH_REGEX = re.compile(r'(.*)_([0-9]+).vh.tif')

    for file in os.listdir(dir_path):
        m = re.match(VH_REGEX, file)
        if not m:
            continue

        pre, num = m.groups()
        vv = f'{pre}_{num}.vv.tif'
        mask = f'{pre}_{num}.mask.tif'

        if not os.path.isfile(os.path.join(dir_path, mask)):
            print(f"Tile: {file} is missing a mask {mask}!")

        if not os.path.isfile(os.path.join(dir_path, vv)):
            print(f"Tile: {file} is missing a mask {vv}!")

        test_or_train = 'train' if random.random() > holdout else 'test'

        folder = os.path.join(dir_path, test_or_train)
        if not os.path.isdir(folder):
            os.makedirs(folder)

        os.rename(
            os.path.join(dir_path, file), os.path.join(folder, file)
        )
        os.rename(
            os.path.join(dir_path, vv),
            os.path.join(folder, vv)
        )
        os.rename(
            os.path.join(dir_path, mask),
            os.path.join(folder, mask)
        )


def mkdata_wrapper(args: Namespace) -> None:
    etl_wm()
    setup_data(args.size)
    dataset_fpath = f"syntheticTriainingData{date.isoformat(date.today())}"
    dataset_dir = os.path.join('datasets', args.directory)
    model_name = args.model
    model = load_model(model_name)

    if args.environment:
        final_dataset_fpath = os.path.join(
            dataset_dir, f'{args.dataset}_{args.environment}'
        )
        dataset = os.path.join(
            args.directory, f'{args.dataset}_{args.environment}'
        )
    else:
        final_dataset_fpath = os.path.join('datasets', args.dataset)
        dataset = args.dataset

    if not os.path.isdir(dataset_dir):
        os.mkdir(dataset_dir)

    if not os.path.isdir(final_dataset_fpath):
        os.mkdir(final_dataset_fpath)

    for folder in os.listdir(dataset_fpath):
        for img in os.listdir(os.path.join(dataset_fpath, folder)):
            os.rename(
                os.path.join(dataset_fpath, folder, img),
                os.path.join(final_dataset_fpath, img)
            )
    shutil.rmtree(dataset_fpath)
    move_imgs(final_dataset_fpath)
    prepare_data(final_dataset_fpath, 0.2)

    predictions, data_iter, metadata = test_model_masked(
        model, dataset, edit=True
    )
    edit_predictions(
        predictions, data_iter, metadata
    )




if __name__ == '__main__':
    p = ArgumentParser()
    sp = p.add_subparsers()

    mk_data = sp.add_parser('mkdata', help='Make data')
    mk_data.add_argument('model', help='Neural network for generating masks')
    mk_data.add_argument('dataset', help='Name of dataset')
    mk_data.add_argument('directory', help='Directory to store dataset in')
    mk_data.add_argument('size', type=int, help='side of images')
    mk_data.add_argument(
        '-e',
        '--environment',
        help='One word describing the environment'
    )
    mk_data.set_defaults(func=mkdata_wrapper)

    args = p.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        p.print_help()
