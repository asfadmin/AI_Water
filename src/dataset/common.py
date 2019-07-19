"""
    Contains functions that work regardless of dataset type.
"""

import os
import pathlib
from contextlib import contextmanager
from typing import Iterator, Union

import numpy as np
from osgeo import gdal

from ..config import DATASETS_DIR
from ..model import ModelType


def dataset_dir(dataset: str) -> str:
    return os.path.join(DATASETS_DIR, dataset)


def valid_image(img: np.ndarray) -> bool:
    if np.any(np.isnan(img)):
        return False
    if 0 in img:
        return False
    return True


def dataset_type(dataset: str) -> ModelType:
    """ Returns the model type for a given dataset. """
    if os.path.isfile(os.path.join(dataset_dir(dataset), 'labels.json')):
        return ModelType.BINARY
    return ModelType.MASKED


@contextmanager
def gdal_open(file_name: Union[str, pathlib.Path]) -> Iterator[gdal.Dataset]:
    file_name = str(file_name)
    f = gdal.Open(file_name)
    if not f:
        raise FileNotFoundError(file_name)
    yield f
