"""
masked.py contains the code for preparing a masked data set, and loading
the prepared data set for use.
"""

import os
import re
from typing import Generator, Optional, Tuple

import numpy as np
from keras.preprocessing.image import ImageDataGenerator, Iterator

import src.config as config

from ..gdal_wrapper import gdal_open
from ..typing import MaskedDatasetMetadata
from .common import dataset_dir, valid_image, check_dependencies

TILE_REGEX = re.compile(r"(.*)\.vh\.(tiff|tif|TIFF|TIF)")


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


def load_replace_data(
    dataset: str,
) -> Tuple[Iterator, MaskedDatasetMetadata]:

    replace_gen = ImageDataGenerator(rescale=10)
    metadata, _ = make_metadata(dataset, edit=True)

    # Load the entire dataset into memory
    x_replace = []
    y_replace = []
    for img, mask in generate_from_metadata(
        metadata,
        edit=True,
        clip_range=(0, 2)
    ):
        x_replace.append(img)
        y_replace.append(mask)

    replace_iter = replace_gen.flow(
        np.array(x_replace), y=np.array(y_replace), batch_size=1, shuffle=False
    )

    return replace_iter, metadata


def make_metadata(
    dataset: str,
    edit: bool = False
) -> Tuple[MaskedDatasetMetadata, MaskedDatasetMetadata]:
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
            vh_name = f"{pre}.vh.{ext}"
            vv_name = f"{pre}.vv.{ext}"

            data = (
                os.path.join(dirpath, vh_name), os.path.join(dirpath, vv_name),
                os.path.join(dirpath, mask)
            )
            folder = os.path.basename(dirpath)

            if edit:
                if folder == 'test' or folder == 'train':
                    train_metadata.append(data)
            else:
                if folder == 'train':
                    train_metadata.append(data)
                elif folder == 'test':
                    test_metadata.append(data)

    return train_metadata, test_metadata


def generate_from_metadata(
    metadata: MaskedDatasetMetadata,
    clip_range: Optional[Tuple[float, float]] = None,
    edit: bool = False
) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
    """ Yield training images and masks from the given metadata. """
    output_shape = (64, 64, 2)
    mask_output_shape = (64, 64, 1)
    for tile_vh, tile_vv, mask_name in metadata:

        with gdal_open(tile_vh) as f:
            tile_vh_array = f.ReadAsArray()
        with gdal_open(tile_vv) as f:
            tile_vv_array = f.ReadAsArray()

        tile_array = np.stack((tile_vh_array, tile_vv_array), axis=2)

        if not edit:
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


def make_tiles(ifname: str, tile_size: Tuple[int, int], folder='prep_tiles') -> None:
    """ Takes a .tiff file and breaks it into smaller .tiff files. """
    if folder == "prep_tiles":
        img_fpath = os.path.join(config.PROJECT_DIR, folder, ifname)
    else:
        img_fpath = os.path.join(config.PROJECT_DIR, ifname, folder)
    if not check_dependencies(('gdal', )):
        return

    datafile = gdal.Open(img_fpath)
    iftitle, ifext = re.match(r'(.*)\.(tiff|tif)', img_fpath).groups()
    step_x, step_y = tile_size

    xsize = datafile.RasterXSize
    ysize = datafile.RasterYSize

    for x in range(0, xsize, step_x):
        for y in range(0, ysize, step_y):
            gdal.Translate(
                f'{iftitle}_ulx_{x}_uly_{y}.{ifext}',
                img_fpath,
                srcWin=[x, y, step_x, step_y],
                format="GTiff"
            )


def split_imgs(dir: str) -> None:
    """ Breaks an image down to 64 x 64 """
    dir_fpath = os.path.join(config.PROJECT_DIR, dir)
    IMG_FOLDER = re.compile(f'(.*)/{dir}/(.*)')
    for root, dirs, imgs in os.walk(dir_fpath):
        for img in imgs:
            m = re.match(IMG_FOLDER, root)
            if not m:
                continue

            if img.endswith('.xml'):
                try:
                    os.remove(img)
                except FileNotFoundError:
                    continue

            _, folder = m.groups()
            try:
                img_path = os.path.join(folder, img)
                make_tiles(dir, (64, 64), img_path)
            except FileNotFoundError as e:
                print(e)


def stitch_images() -> None:
    pass
