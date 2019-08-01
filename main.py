"""
Train or test a neural network.

To train a network:
    '$ python3 main.py train name_of_net name_of_dataset --epochs 10'
To test a trained network:
    '$ python3 main.py test name_of_net name_of_dataset'
For more information see README.md
"""

import os
import shutil
from argparse import ArgumentParser, Namespace

from src.asf_cnn import test_model_binary, test_model_masked, train_model
from src.dataset.common import dataset_type
from src.model import (
    ModelType, create_model, load_model, model_type, path_from_model_name
)
from src.plots import plot_confusion_chart, plot_predictions
from src.plots_masked import plot_predictions as plot_masked_predictions
from src.reports import write_dict_to_csv

import numpy as np
from osgeo import gdal
from src.dataset.masked import make_metadata
from tifffile import imsave
import subprocess
from keras.preprocessing.image import ImageDataGenerator, Iterator
from typing import List, Tuple
from src.dataset.masked import generate_from_metadata
from pathlib import Path
import re
from natsort import natsorted


def train_wrapper(args: Namespace) -> None:
    """Function for training a network"""
    data_type = dataset_type(args.dataset)
    model_name = args.model
    if args.cont:
        model = load_model(model_name)
        history = model.__asf_model_history
    else:
        model_path = path_from_model_name(model_name)
        if not args.overwrite and os.path.isfile(model_path):
            print(f"File {model_name} already exists!")
            return

        model = create_model(model_name, data_type)
        history = {"loss": [], "acc": [], "val_loss": [], "val_acc": []}

    if model_type(model) != data_type:
        print("ERROR: This dataset is not compatible with your model")
        return

    train_model(model, history, args.dataset, args.epochs)


def test_wrapper(args: Namespace) -> None:
    model_name = args.model
    model = load_model(model_name)

    if model_type(model) != dataset_type(args.dataset):
        print("ERROR: This dataset is not compatible with your model")
        return
    if dataset_type(args.dataset) == ModelType.MASKED:
        predictions, test_iter = test_model_masked(model, args.dataset)
        plot_masked_predictions(predictions, test_iter, args.dataset)
    else:

        details, confusion_matrix = test_model_binary(model, args.dataset)

        model_dir = os.path.dirname(path_from_model_name(model_name))
        with open(os.path.join(model_dir, 'results.csv'), 'w') as f:
            write_dict_to_csv(details, f)

        plot_confusion_chart(confusion_matrix)
        plot_predictions(details['Percent'], args.dataset)


def make_predict_metadata(tile_path: str) -> List[Tuple[str, str]]:
    predict_metadata = []
    vh_vv_list = os.listdir(tile_path)
    vh_vv_list=sorted(vh_vv_list)
    midpoint = int(len(vh_vv_list)/2)
    vh_list = vh_vv_list[0:midpoint]
    for i in range(midpoint):
        vh_list[i] = os.path.join(tile_path, vh_list[i])
    vv_list = vh_vv_list[midpoint:]
    for i in range(midpoint):
        vv_list[i] = os.path.join(tile_path, vv_list[i])
    predict_metadata = tuple(zip(vh_list, vv_list))
    return predict_metadata


def prediction_wrapper(args: Namespace) -> None:
    # local vars
    mxm_tile_size = 512
    sar_tiles_path = os.path.join('datasets', args.dataset, 'sar_tiles')
    prediction_tiles_path = os.path.join('datasets', args.dataset,
                                         'prediction_tiles')
    sar_name = 'temp'
    for sar in os.listdir(prediction_path):
        sar_name = sar[:-7]

    # make sar_tiles, prediction_tiles dir
    if not os.path.exists(sar_tiles_path):
        os.mkdir(sar_tiles_path)
    if not os.path.exists(prediction_tiles_path):
        os.mkdir(prediction_tiles_path)

    # tile vv vh and mv to tiles dir
    for sar in os.listdir(prediction_path):
        if not os.path.isdir(os.path.join(prediction_path, sar)):
            tif = os.path.join(prediction_path, sar)
            tifData = gdal.Open(tif)
            xStep, yStep = mxm_tile_size, mxm_tile_size
            xSize, ySize = tifData.RasterXSize, tifData.RasterYSize
            count = 0
            for x in range(0, xSize, xStep):
                for y in range(0, ySize, yStep):
                    # fileName = '<Image|Mask>_<sar>_<0-9+>.tif'
                    fileName = f"Image_{sar[:-4]}_{count}.tif"
                    output_file = os.path.join(sar_tiles_path, fileName)
                    input_file = tif
                    gdal.Translate(
                        output_file,
                        input_file,
                        srcWin=[x, y, xStep, yStep],
                        format="GTiff"
                    )
                    count += 1

    # make prediction with cnn
    model = load_model(args.model)
    predict_metadata = make_predict_metadata(sar_tiles_path)
    input_array = []
    projection = []
    geotransform = []
    names = []
    for vh, vv in predict_metadata:
        vh_tif_array = gdal.Open(vh).ReadAsArray()
        projection.append(gdal.Open(vh).GetProjection())
        geotransform.append(gdal.Open(vh).GetGeoTransform())
        vv_tif_array = gdal.Open(vv).ReadAsArray()
        input_array.append(np.stack((vh_tif_array, vv_tif_array), axis=2))
        name = f"Prediction_{os.path.basename(vh)[6:]}"
        names.append(os.path.join(prediction_tiles_path ,name))
    input_array = np.array(input_array)
    prediction_array = model.predict(input_array, verbose=1)

    for i in range(len(names)):
        (width, height, _) = prediction_array[i].shape
        out_image = gdal.GetDriverByName('GTiff').Create(
            names[i], height, width, bands=1
        )
        out_image.SetProjection(projection[i])
        out_image.SetGeoTransform(geotransform[i])
        out_image.GetRasterBand(1).WriteArray(prediction_array[i].reshape(width, height)) # ???
        out_image.FlushCache()

    #mosaic prediction_tiles
    with open(os.path.join(prediction_tiles_path, 'prediction_tiles_list.txt'), 'w') as txt_file:
        tiles = []
        for tile in os.listdir(prediction_tiles_path):
            if tile.endswith('.tif'):
                tiles.append(tile)
        tiles = natsorted(tiles)
        for i in range(len(tiles)):
            txt_file.write(f"{os.path.join(prediction_tiles_path, tiles[i])}\n")
    prediction_tiles_list = os.path.join(prediction_tiles_path,
                                         'prediction_tiles_list.txt')
    name = os.path.basename
    vrt = f"{os.path.join(prediction_tiles_path, sar_name)}.vrt"
    tif = f"{os.path.join(prediction_tiles_path, sar_name)}.prediction.tif"
    subprocess.call(
        f"gdalbuildvrt -input_file_list {prediction_tiles_list} {vrt}",
        shell=True
    )
    subprocess.call(
        f"gdal_translate -of GTiff {vrt} {tif}",
        shell=True
    )
    shutil.copy(tif, prediction_path)
    # clean up
    shutil.rmtree(prediction_tiles_path)
    shutil.rmtree(sar_tiles_path)


if __name__ == '__main__':
    p = ArgumentParser()
    sp = p.add_subparsers()

    # Arguments for train mode
    train = sp.add_parser('train', help='Train a new model')
    train.add_argument('model', help='Name of the model to save: example_net')
    train.add_argument('dataset', nargs='?', default='dataset_calibrated')
    train.add_argument(
        '--overwrite',
        '-o',
        action='store_true',
        help='Replace the file if it exists'
    )
    train.add_argument(
        '--continue',
        '-c',
        action='store_true',
        dest='cont',
        help='Continue training from existing model'
    )
    train.add_argument('--epochs', '-e', type=int, default=10)
    train.set_defaults(func=train_wrapper)

    # Arguments for test mode
    test = sp.add_parser('test', help='Test an existing model')
    test.add_argument('model', help='Name of the trained model')
    test.add_argument('dataset', nargs='?', default='dataset_calibrated')
    test.set_defaults(func=test_wrapper)

    # Arguments for prediction mode
    prediction = sp.add_parser(
        'prediction',
        help='Generate predicted mask using an existing model.'
    )
    prediction.add_argument(
        'model',
        help='name of trained model'
    )
    prediction.add_argument(
        'dataset', nargs='?',
        help='Path to dir containing a vh vv sar granule pair'
    )
    # prediction.add_argument('outDir', help = 'path to output mask')
    prediction.set_defaults(func=prediction_wrapper)

    # Parse and execute selected function
    args = p.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        p.print_help()
