"""
mask.py contains the code for preparing a maseked data set,
then loading the prepared data set for use.
"""

import os
import re
from typing import Optional, Tuple

import numpy as np
from keras.preprocessing.image import ImageDataGenerator, Iterator
from osgeo import gdal

from ..typing import DatasetMetadata
from .common import dataset_dir, valid_image

TILE_REGEX = re.compile(r"(.*)\.tile\.(tiff|tif|TIFF|TIF)")


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
    """Sets up masked metadata into two lists, one for training and one for
    testing data. Returns both lists."""
    train_metadata = []
    test_metadata = []

    for dirpath, dirnames, filenames in os.walk(dataset_dir(dataset)):
        for name in sorted(filenames):
            m = re.match(TILE_REGEX, name)
            if not m:
                continue

            pre, ext = m.groups()
            mask = f"{pre}.mask.{ext}"

            data = (os.path.join(dirpath, name), os.path.join(dirpath, mask))
            folder = os.path.basename(dirpath)
            if folder == 'train':
                train_metadata.append(data)
            elif folder == 'test':
                test_metadata.append(data)

    return train_metadata, test_metadata


def generate_from_metadata(
    metadata: DatasetMetadata, clip_range: Optional[Tuple[float, float]] = None
):

    output_shape = (512, 512, 1)
    for tile_name, mask_name in metadata:
        tile = gdal.Open(tile_name)
        if tile is None:
            continue
        tile_array = tile.ReadAsArray()

        mask = gdal.Open(mask_name)
        if mask is None:
            print(mask_name)
            continue
        mask_array = mask.ReadAsArray()

        if not valid_image(tile_array):
            continue

        x = np.array(tile_array).astype('float32')
        y = np.array(mask_array).astype('float32')
        # Clip all x values to a fixed range
        if clip_range:
            min_, max_ = clip_range
            np.clip(x, min_, max_, out=x)

        yield (x.reshape(output_shape), y.reshape(output_shape))
