"""
 Created By:   Jason Herning
 Date Started: 10-01-2020
 File Name:    io_tools.py
 Description:  Various functions for i/o handling
"""

import os
import random
import re
import shutil
from itertools import groupby
from pathlib import Path

from src.asf_typing import sar_set
from src.config import SENTINEL_DIR, SHAPEFILE_DIR, MODEL_WEIGHTS_DIR, TILES_DIR, WATER_MASKS_DIR, LABELS_DIR, \
    TENSORBOARD_DIR, TYPE_REGEX, DATASETS_DIR



# TODO: check that directories exist
def create_directories() -> None:
    """Creates the directories for storing our data"""
    directories = [SENTINEL_DIR, SHAPEFILE_DIR, MODEL_WEIGHTS_DIR, TILES_DIR, WATER_MASKS_DIR, LABELS_DIR, TENSORBOARD_DIR]
    for directory in directories:
        directory.mkdir(parents=True)



def list_sar_directory(directory_path: str) -> list:
    """Recursively generates list of all mask, vh, vv .tif files."""
    path_generator = Path(directory_path).rglob('*.tif')
    return sorted([path.name for path in path_generator if path.is_file()])


def get_sar_paths(directory_path: str) -> list:
    """returns a list of namedTuples (sar_sets) that store vv, vh, and mask paths"""
    dataset_path = Path(directory_path)

    path_generator = dataset_path.rglob('*.tif')
    paths = sorted([path for path in path_generator if path.is_file()])
    return [sar_set(*g) for k, g in groupby(paths, key=lambda path: re.match(TYPE_REGEX, path.name)[2])]


def remove_subdirectories(root_directory: str) -> None:
    """removes sub directories """
    root_path = Path(root_directory)
    subdirectories = [path for path in root_path.iterdir() if path.is_dir()]
    for subdirectory in subdirectories:
        if subdirectory.name not in ['test', 'train']:
            try:
                shutil.rmtree(subdirectory)
            except OSError as e:
                print(f"Error: {subdirectory} : {e.strerror}")


def make_directory_dataset(directory_path: str) -> None:
    """Creates a new dataset directory along with the test and train folders.
       If directory already exist then only the test and train folders will be created."""
    dataset_path = Path(directory_path)
    test_path = dataset_path / 'test'
    train_path = dataset_path / 'train'

    if not dataset_path.is_dir():
        dataset_path.mkdir()

    if not test_path.is_dir():
        test_path.mkdir()

    if not train_path.is_dir():
        train_path.mkdir()


def divide_sar_files(dataset_path: Path, sar_sets: list, holdout: float) -> None:
    for sar in sar_sets:
        test_or_train = 'train' if random.random() > holdout else 'test'

        mask_path_new = dataset_path.joinpath(test_or_train, sar.mask.name)
        vh_path_new = dataset_path.joinpath(test_or_train, sar.vh.name)
        vv_path_new = dataset_path.joinpath(test_or_train, sar.vv.name)

        if not mask_path_new.exists():
            sar.mask.replace(mask_path_new)

        if not vh_path_new.exists():
            sar.vh.replace(vh_path_new)

        if not vv_path_new.exists():
            sar.vv.replace(vv_path_new)


def compress_datasets(directory_path: str, holdout: float) -> None:
    """compresses all datasets into the input parent directory.
       Sar files are divided into the test and train folders"""

    dataset_path = Path(directory_path)
    sar_sets = get_sar_paths(directory_path)
    make_directory_dataset(directory_path)
    divide_sar_files(dataset_path, sar_sets, holdout)
    remove_subdirectories(directory_path)
