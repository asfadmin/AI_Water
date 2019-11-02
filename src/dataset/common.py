"""
Contains functions that work regardless of dataset type.
"""

import os

import numpy as np

from ..config import DATASETS_DIR

# from ..model import ModelType


def dataset_dir(dataset: str) -> str:
    return os.path.join(DATASETS_DIR, dataset)


def valid_image(img: np.ndarray) -> bool:
    if np.any(np.isnan(img)):
        return False
    if 0 in img:
        return False
    return True
