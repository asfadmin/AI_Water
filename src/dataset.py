import json
import os
from typing import Optional, Set, Tuple

import numpy as np
from keras.preprocessing.image import ImageDataGenerator
from osgeo import gdal

from .config import PROJECT_DIR


class DataGenerator(object):
    def __init__(
        self,
        metadata,
        rescale: int = 1,
        clip_range: Optional[Tuple[float, float]] = None
    ):
        self.metadata = metadata
        self.rescale = rescale
        self.clip_range = clip_range
        self.label_to_num = {'water': 1, 'not_water': 0}

    def generate(self):
        for file_name, label in self.metadata:
            tif = gdal.Open(file_name)
            tif_array = tif.ReadAsArray()

            if np.any(np.isnan(tif_array)):
                continue
            if 0 in tif_array:
                continue

            x = np.array(tif_array).astype('float32') * self.rescale
            # Clip all values to a fixed range
            if self.clip_range:
                l, h = self.clip_range
                np.clip(x, l, h, out=x)
            yield x.reshape((512, 512, 1)), np.array(self.label_to_num[label])


def dataset_dir(dataset: str):
    return os.path.join(PROJECT_DIR, 'dataset', dataset)


def load_dataset(dataset: str):
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
    for img, label in DataGenerator(train_metadata).generate():
        x_train.append(img)
        y_train.append(label)
    x_test = []
    y_test = []
    for img, label in DataGenerator(test_metadata).generate():
        x_test.append(img)
        y_test.append(label)

    train_iter = train_gen.flow(
        np.array(x_train), y=np.array(y_train), batch_size=16
    )
    test_iter = test_gen.flow(
        np.array(x_test), y=np.array(y_test), batch_size=1, shuffle=False
    )

    return train_iter, test_iter


def make_metadata(dataset: str, classes: Optional[Set[str]] = None):
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
