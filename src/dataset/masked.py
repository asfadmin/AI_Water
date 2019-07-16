"""
    masked.py contains the code for preparing a masked data set, and loading
the prepared data set for use.
"""

import os
import re
from typing import Optional, Tuple

import numpy as np
from keras.preprocessing.image import ImageDataGenerator, Iterator
from osgeo import gdal

from ..typing import DatasetMetadata
from .common import dataset_dir, gdal_open, valid_image

TILE_REGEX = re.compile(r"(.*)\.tile\.vh\.(tiff|tif|TIFF|TIF)")


def load_dataset(dataset: str) -> Tuple[Iterator, Iterator]:

    train_gen = ImageDataGenerator(rescale=10)
    test_gen = ImageDataGenerator(rescale=10)

    train_metadata, test_metadata = make_metadata(dataset)
    # Load the entire dataset into memory
    x_train = []
    y_train = []
    for img, mask in generate_from_metadata(train_metadata, clip_range=(0, 2)):
        x_train.append(img)
        y_train.append(mask)

    x_test = []
    y_test = []

    for img, mask in generate_from_metadata(test_metadata, clip_range=(0, 2)):
        x_test.append(img)
        y_test.append(mask)

    train_iter = train_gen.flow(
        np.array(x_train), y=np.array(y_train), batch_size=16
    )
    test_iter = test_gen.flow(
        np.array(x_test), y=np.array(y_test), batch_size=1, shuffle=False
    )

    return train_iter, test_iter


def make_metadata(dataset: str) -> Tuple[DatasetMetadata, DatasetMetadata]:
    """ Returns two lists of metadata. One for the training data and one for the
    testing data. """
    train_metadata = []
    test_metadata = []

    for dirpath, dirnames, filenames in os.walk(dataset_dir(dataset)):
        for name in sorted(filenames):
            m = re.match(TILE_REGEX, name)
            if not m:
                continue

            pre, ext = m.groups()
            mask = f"{pre}.mask.{ext}"
            vh_name = f"{pre}.tile.vh.{ext}"
            vv_name = f"{pre}.tile.vv.{ext}"

            data = (os.path.join(dirpath, vh_name),
                    os.path.join(dirpath, vv_name),
                    os.path.join(dirpath, mask))
            folder = os.path.basename(dirpath)

            if folder == 'train':
                train_metadata.append(data)
            elif folder == 'test':
                test_metadata.append(data)
    return train_metadata, test_metadata


def generate_from_metadata(
    metadata: DatasetMetadata, clip_range: Optional[Tuple[float, float]] = None
):
    """ Yield training images and masks from the given metadata. """
    output_shape = (512, 512, 2)
    mask_output_shape = (512, 512, 1)
    for tile_vh, tile_vv, mask_name in metadata:

        with gdal_open(tile_vh) as f:
            tile_vh_array = f.ReadAsArray()
        with gdal_open(tile_vv) as f:
            tile_vv_array = f.ReadAsArray()

        tile_array = np.stack((tile_vh_array, tile_vv_array), axis=2)
        if not valid_image(tile_array):
            continue

        with gdal_open(mask_name) as f:
            mask_array = f.ReadAsArray()

        x = np.array(tile_array).astype('float32')
        y = np.array(mask_array).astype('float32')
        # Clip all x values to a fixed range
        if clip_range:
            min_, max_ = clip_range
            np.clip(x, min_, max_, out=x)
        yield (x.reshape(output_shape), y.reshape(mask_output_shape))
