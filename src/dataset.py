import json
import os
from typing import Iterator, Optional, Set, Tuple, Union

import numpy as np
from keras.preprocessing.image import ImageDataGenerator
from osgeo import gdal

from .config import DATASET_DIR
from .typing import DatasetMetadata


def generate_from_metadata(
    metadata: DatasetMetadata,
    rescale: float = 1.0,
    clip_range: Optional[Tuple[float, float]] = None
):
    label_to_num = {'water': 1, 'not_water': 0}
    for file_name, label in metadata:
        tif = gdal.Open(file_name)
        tif_array = tif.ReadAsArray()

        if np.any(np.isnan(tif_array)):
            continue
        if 0 in tif_array:
            continue

        x = np.array(tif_array).astype('float32') * rescale
        # Clip all values to a fixed range
        if clip_range:
            l, h = clip_range
            np.clip(x, l, h, out=x)

        yield (x.reshape((512, 512, 1)), np.array(label_to_num[label]))


def dataset_dir(dataset: str) -> str:
    return os.path.join(DATASET_DIR, dataset)


def load_dataset(
    dataset: str, get_metadata: bool = False
) -> Union[Tuple[Iterator, Iterator],
           Tuple[Iterator, Iterator, DatasetMetadata, DatasetMetadata]]:
    train_gen = ImageDataGenerator(
        rescale=1. / 512, shear_range=0.2, zoom_range=0.2, horizontal_flip=True
    )
    test_gen = ImageDataGenerator(rescale=1. / 512)

    train_metadata, test_metadata = make_metadata(
        dataset, {'water', 'not_water'}
    )

    # Load the entire dataset into memory
    x_train = []
    y_train = []
    for img, label in generate_from_metadata(train_metadata):
        x_train.append(img)
        y_train.append(label)
    x_test = []
    y_test = []
    for img, label in generate_from_metadata(test_metadata):
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
                  ) -> Tuple[DatasetMetadata, DatasetMetadata]:
    with open(os.path.join(dataset_dir(dataset), 'labels.json')) as f:
        labels = json.load(f)

        train_metadata = []
        test_metadata = []
        for dirpath, dirnames, filenames in os.walk(dataset_dir(dataset)):
            for name in filenames:
                if name not in labels:
                    continue

                label = labels[name]
                if classes and label not in classes:
                    continue

                data = (os.path.join(dirpath, name), label)
                if 'train' in dirpath:
                    train_metadata.append(data)
                elif 'test' in dirpath:
                    test_metadata.append(data)
    return train_metadata, test_metadata
