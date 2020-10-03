"""
 Created By:   Jason Herning
 Date Started: 09-20-2020
 File Name:    geo_utility.py
 Description:  Toolbox of functions to help process GeoTIFFs.
"""

import os
import itertools
from typing import Generator, Tuple, Any

from src.config import NETWORK_DEMS as dems
from osgeo import gdal
from src.model import load_model
from src.config import NETWORK_DEMS as dems
from pathlib import Path
import numpy as np


# TODO: sepearte translate as sperate function that can be tested. (maybe)
def write_tiles(input_tif: str, output_directory: str, tile_size: int, name: str):
    """TODO: Add description"""
    input_image = gdal.Open(input_tif)

    array = input_image.ReadAsArray()

    rows, cols = array.shape

    tile_indexes = itertools.product(
        range(0, rows, tile_size), range(0, cols, tile_size))

    for (row, col) in tile_indexes:
        in_bounds = row + tile_size < rows and col + tile_size < cols
        if in_bounds:
            gdal.Translate(
                f'{output_directory}{name}_x{row / tile_size}y{col / tile_size}.tif',
                input_tif,
                srcWin=[row, col, tile_size, tile_size],
                format="GTiff"
            )


def stride_tile_image(

        image: np.ndarray, width: int = dems, height: int = dems
) -> np.ndarray:
    _nrows, _ncols = image.shape
    _strides = image.strides

    nrows, _m = divmod(_nrows, height)
    ncols, _n = divmod(_ncols, width)

    assert _m == 0, "Image must be evenly tileable. Please pad it first"
    assert _n == 0, "Image must be evenly tileable. Please pad it first"

    return np.lib.stride_tricks.as_strided(
        np.ravel(image),
        shape=(nrows, ncols, height, width),
        strides=(height * _strides[0], width * _strides[1], *_strides),
        writeable=False
    ).reshape(nrows * ncols, height, width)


def get_tile_dimensions(height: int, width: int, tile_size: int):
    return int(np.ceil(height / tile_size)), int(np.ceil(width / tile_size))


def write_mask_to_file(
        mask: np.ndarray, file_name: str, projection: str, geo_transform: str
) -> None:
    (width, height) = mask.shape
    out_image = gdal.GetDriverByName('GTiff').Create(
        file_name, height, width, bands=1
    )
    out_image.SetProjection(projection)
    out_image.SetGeoTransform(geo_transform)
    out_image.GetRasterBand(1).WriteArray(mask)
    out_image.GetRasterBand(1).SetNoDataValue(0)
    out_image.FlushCache()


def pad_image(image: np.ndarray, to: int) -> np.ndarray:
    height, width = image.shape

    n_rows, n_cols = get_tile_dimensions(height, width, to)
    new_height = n_rows * to
    new_width = n_cols * to

    padded = np.zeros((new_height, new_width))
    padded[:image.shape[0], :image.shape[1]] = image
    return padded


# TODO: Cut edge fill on final mask (make it more pretty!
# TODO: FIX VV/VH ISSUE. ONLY WORKS WITH VV RIGHT NOW!
# TODO: Split get vv/vh tiles into functions
# TODO: Try differnt tiling method (not strided)
def create_water_mask(
        model_path: str, vv_path: str, vh_path: str, outfile: str, verbose: int = 0
):
    if not os.path.isfile(vv_path):
        raise FileNotFoundError(f"Tiff '{vv_path}' does not exist")

    if not os.path.isfile(vh_path):
        raise FileNotFoundError(f"Tiff '{vh_path}' does not exist")

    def get_tiles(img_path):
        f = gdal.Open(img_path)
        img_array = f.ReadAsArray()
        original_shape = img_array.shape
        n_rows, n_cols = get_tile_dimensions(*original_shape, tile_size=dems)
        padded_img_array = pad_image(img_array, dems)
        invalid_pixels = np.nonzero(padded_img_array == 0.0)
        img_tiles = stride_tile_image(padded_img_array)
        return img_tiles, n_rows, n_cols, invalid_pixels, f.GetProjection(), f.GetGeoTransform()

    # Get vv tiles
    vv_tiles, vv_rows, vv_cols, vv_pixels, vv_projection, vv_transform = get_tiles(vv_path)

    # Get vh tiles
    vh_tiles, vh_rows, vh_cols, vh_pixels, vh_projection, vh_transform = get_tiles(vh_path)

    model = load_model(model_path)

    # Predict masks
    masks = model.predict(
        np.stack((vv_tiles, vh_tiles), axis=3), batch_size=1, verbose=verbose
    )

    masks.round(decimals=0, out=masks)

    # Stitch masks together
    mask = masks.reshape((vv_rows, vv_cols, dems, dems)) \
        .swapaxes(1, 2) \
        .reshape(vv_rows * dems, vv_cols * dems)  # yapf: disable

    mask[vv_pixels] = 0
    write_mask_to_file(mask, outfile, vv_projection, vv_transform)

    # Needed?
    f = None
