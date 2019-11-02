"""
make_data.py allows a user to make a new dataset. To use make_data go to
your finished products at http://hyp3.asf.alaska.edu, select the granule(s)
you'd like to turn into a dataset and then download its python script.
Leave the script in downloads. After that run make_data.py

* Note: These commands assume you are in the projects root directory
Command layout:
    python scripts/make_data.py ai_model_folder dataset_name dir_dataset_sits 512
Example:
    python scripts/make_data.py ai_model_7 Fairbanks Alaska 512
"""
import os
import random
import re
import shutil
from argparse import ArgumentParser, Namespace
from datetime import date

from etl_water_mark import main as etl_wm
from prepare_data import move_imgs, prepare_data
from src.asf_cnn import test_model_masked
from src.model import load_model
from src.plots import edit_predictions
from water_mark import setup_data


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


def compress_wrapper(args: Namespace) -> None:
    ENV_REG_EX = re.compile(r'(.*)_([0-9]+)_(.*)_Groomed/train')
    env = ''
    f_path = os.path.join('datasets', args.directory)
    for root, dirs, files in os.walk(f_path, topdown=False):
        m = re.match(ENV_REG_EX, root)
        if not m:
            continue
        _, _, env = m.groups()
        print(env)
        for img in files:
            os.rename(
                os.path.join(root, img),
                os.path.join(f_path, f'{env}_{img}')
            )

    for file in os.listdir(f_path):
        path = os.path.join(f_path, file)
        if os.path.isdir(path):
            shutil.rmtree(path)
    div_imgs(f_path, .2)


if __name__ == '__main__':
    p = ArgumentParser()
    sp = p.add_subparsers()

    mk_data = sp.add_parser('mkdata', help='Make data')
    mk_data.add_argument('model', help='Neural network for generating masks')
    mk_data.add_argument('dataset', help='Name of dataset')
    mk_data.add_argument('directory', help='Directory to store dataset in')
    mk_data.add_argument('size', type=int, help='side of imgaes')
    mk_data.add_argument(
        '-e',
        '--environment',
        help='One word describing the environment'
    )
    mk_data.set_defaults(func=mkdata_wrapper)

    compress = sp.add_parser(
        'compress', help='Compress all datasets in directory into one'
    )
    compress.add_argument('directory', help='Name of directory')
    compress.set_defaults(func=compress_wrapper)

    args = p.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        p.print_help()
