"""
    binary.py contains the code for preparing a binary data set, then loading
the prepared data set for use.
"""

import json
import os
from typing import Dict, Generator, Optional, Set, Tuple, Union, overload

import numpy as np
from keras.preprocessing.image import ImageDataGenerator, Iterator
from osgeo import gdal
from typing_extensions import Literal

from ..typing import BinaryDatasetMetadata
from .common import dataset_dir, valid_image


@overload
def load_dataset(dataset: str) -> Tuple[Iterator, Iterator]:
    ...


@overload
def load_dataset(
    dataset: str, get_metadata: Literal[True]
) -> Tuple[Iterator, Iterator, BinaryDatasetMetadata, BinaryDatasetMetadata]:
    ...


def load_dataset(dataset: str, get_metadata: bool = False) -> Union[
    Tuple[Iterator, Iterator],
    Tuple[Iterator, Iterator, BinaryDatasetMetadata, BinaryDatasetMetadata]
]:
    """ Creates two iterator yielding tuples for training and testing data.
    If `get_metadata = true`, it will also return two list
    (train_metadata and test_metadata) with the values being 'water' or
    'not_water'.
    """
    classes = {'water', 'not_water'}

    train_gen = ImageDataGenerator(
        shear_range=0.2, zoom_range=0.2, horizontal_flip=True
    )
    test_gen = ImageDataGenerator()

    train_metadata, test_metadata = make_metadata(dataset, classes)
    label_to_num, _ = make_label_conversions(dataset, classes)

    # Load the entire dataset into memory
    x_train = []
    y_train = []
    for img, label in generate_from_metadata(
        train_metadata, label_to_num, clip_range=(0, 2)
    ):
        x_train.append(img)
        y_train.append(label)
    x_test = []
    y_test = []
    for img, label in generate_from_metadata(
        test_metadata, label_to_num, clip_range=(0, 2)
    ):
        x_test.append(img)
        y_test.append(label)

    train_iter = train_gen.flow(
        np.array(x_train), y=np.array(y_train), batch_size=16
    )
    test_iter = test_gen.flow(
        np.array(x_test), y=np.array(y_test), batch_size=1, shuffle=False
    )

    if get_metadata:
        return train_iter, test_iter, train_metadata, test_metadata

    return train_iter, test_iter


def make_metadata(dataset: str, classes: Optional[Set[str]] = None
                  ) -> Tuple[BinaryDatasetMetadata, BinaryDatasetMetadata]:
    """ Creates metadata marking images as 'water' or 'not_water'. """
    labels = load_labels(dataset)
    train_metadata = []
    test_metadata = []
    for dirpath, dirnames, filenames in os.walk(dataset_dir(dataset)):
        for name in sorted(filenames):
            if name not in labels:
                continue

            label = labels[name]
            if classes is not None and label not in classes:
                continue

            data = (os.path.join(dirpath, name), label)
            folder = os.path.basename(dirpath)
            if folder == 'train':
                train_metadata.append(data)
            elif folder == 'test':
                test_metadata.append(data)
    return train_metadata, test_metadata


def make_label_conversions(dataset: str, classes: Optional[Set[str]] = None
                           ) -> Tuple[Dict[str, int], Dict[int, str]]:
    """ Creates two separate dictionaries. One the key is binary and the other
    the value is binary. """
    labels = load_labels(dataset)
    categories = sorted(
        list(filter(lambda x: classes and x in classes, set(labels.values())))
    )

    label_to_num = {}
    num_to_label = {}
    for i, category in enumerate(categories):
        label_to_num[category] = i
        num_to_label[i] = category

    return label_to_num, num_to_label


def generate_from_metadata(
    metadata: BinaryDatasetMetadata,
    label_to_num: Dict[str, int],
    clip_range: Optional[Tuple[float, float]] = None
) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
    """ Converts images into an array, clips the value of the pixels into a
    specific range and reshapes the array to the correct format. """
    for file_name, label in metadata:
        tif = gdal.Open(file_name)
        tif_array = tif.ReadAsArray()

        if not valid_image(tif_array):
            continue

        x = np.array(tif_array).astype('float32')
        # Clip all values to a fixed range
        if clip_range:
            l, h = clip_range
            np.clip(x, l, h, out=x)

        yield (x.reshape((512, 512, 1)), np.array(label_to_num[label]))


def load_labels(dataset: str) -> Dict[str, str]:
    with open(os.path.join(dataset_dir(dataset), 'labels.json')) as f:
        labels = json.load(f)
    if not isinstance(labels, dict):
        raise ValueError("Labels file appears to be corrupted")
    return labels
