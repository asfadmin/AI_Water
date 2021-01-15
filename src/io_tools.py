"""
 Created By:   Jason Herning
 File Name:    io_tools.py
 Description:  Various functions for i/o handling
"""

import random
import re
import shutil
import zipfile
import json
from osgeo import ogr
from itertools import groupby
from pathlib import Path
from shapely.geometry import Polygon
from tempfile import TemporaryDirectory

from src.asf_typing import sar_set
from src.config import PRODUCTS_DIR, AOI_DIR, DATASETS_DIR, MODEL_DIR, MASK_DIR, TENSORBOARD_DIR, TYPE_REGEX


def polygon_from_shapefile(shp_path: Path) -> Polygon:
    """Take Path to shapefile and return shapely Polygon"""
    file = ogr.Open(str(shp_path))
    layer = file.GetLayer(0)
    feature = layer.GetFeature(0)
    first = feature.ExportToJson()
    first = json.loads(first)
    shp_geom = Polygon([tuple(coords) for coords in first['geometry']['coordinates'][0]])
    return shp_geom


def extract_from_product(product_path, output_dir):
    """Extract vv and vh tifs from product.
       returns VV & VH file paths"""

    sar_regex = re.compile(r"(S1[A|B])_(.{2})_(.*)_(VV|VH)(.tif)")

    with zipfile.ZipFile(product_path, "r") as zip_ref:
        with TemporaryDirectory() as tmpdir_name:
            for archive_name in zip_ref.namelist():
                file_name = archive_name.split('/')[1]
                if m := re.fullmatch(sar_regex, file_name):
                    if m.group(4) == 'VV':
                        vv = output_dir / file_name
                    if m.group(4) == 'VH':
                        vh = output_dir / file_name
                    zip_ref.extract(archive_name, path=tmpdir_name)
                    shutil.move(f"{tmpdir_name}/{archive_name}", output_dir)
    return vv, vh


def list_products(dir_path: Path) -> list:
    product_glob = Path(dir_path).glob('*.zip')
    return [product for product in product_glob]


# TODO: check that directories exist
def create_directories() -> None:
    """Creates the directories for storing our data"""
    directories = [PRODUCTS_DIR, AOI_DIR, DATASETS_DIR, MODEL_DIR, MASK_DIR, TENSORBOARD_DIR]
    for directory in directories:
        directory.mkdir(parents=True)


def list_sar_directory(directory_path: str) -> list:
    """Generates list of all mask, vh, vv .tif files."""
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
