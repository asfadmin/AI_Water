import os
import shutil
from argparse import ArgumentParser, Namespace
from datetime import date

from etl_water_mark import main as etl_wm
from src.asf_cnn import test_model_masked
from src.model import load_model
from src.plots_masked import edit_predictions
from tile_geotiff import move_imgs, prepare_data
from water_mark import setup_data


def mkdata_wrapper(args: Namespace) -> None:

    etl_wm()
    setup_data(args.size)
    dataset_fpath = f"syntheticTriainingData{date.isoformat(date.today())}"

    if args.environment:
        final_dataset_fpath = os.path.join(
            'datasets', f'{args.dataset}_{args.environment}'
        )
        dataset = f'{args.dataset}_{args.environment}'
    else:
        final_dataset_fpath = os.path.join('datasets', args.dataset)
        dataset = args.dataset

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
        load_model(args.model), dataset, edit=True
    )
    edit_predictions(
        predictions, data_iter, metadata
    )


if __name__ == '__main__':
    p = ArgumentParser()
    sp = p.add_subparsers()
    # TODO: Come up with a better help description
    mk_data = sp.add_parser('mkdata', help='Make data')
    mk_data.add_argument('size', type=int, help='side of imgaes')
    mk_data.add_argument('dataset', help='Name of dataset')
    mk_data.add_argument('model', help='Neural network for generating masks')
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
