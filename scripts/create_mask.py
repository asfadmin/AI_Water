#!/usr/bin/env/python
"""
Create a water mask for an image. The image must be dual pol (VV + VH) and must
be calibrated.

****** NOTE ******
create_mask.py contains a memory leak. Use a subprocess call when using main
in a loop to prevent memory issues.
"""

import os
from argparse import ArgumentParser

import numpy as np
from src.model import load_model
from osgeo import gdal
from src.config import NETWORK_DEMS as dems


def main(
    model_path: str, vv_path: str, vh_path: str, outfile: str, verbose: int = 0
):

    if not os.path.isfile(vv_path):
        raise FileNotFoundError(f"Tiff '{vv_path}' does not exist")

    if not os.path.isfile(vh_path):
        raise FileNotFoundError(f"Tiff '{vh_path}' does not exist")

    # Get vv tiles
    f = gdal.Open(vv_path)
    vv_array = f.ReadAsArray()
    original_shape = vv_array.shape
    n_rows, n_cols = get_tile_dimensions(*original_shape, tile_size=dems)
    vv_array = pad_image(vv_array, dems)
    invalid_pixels = np.nonzero(vv_array == 0.0)

    vv_tiles = tile_image(vv_array)

    # Get vh tiles
    f = gdal.Open(vh_path)
    vh_array = pad_image(f.ReadAsArray(), dems)

    vh_tiles = tile_image(vh_array)

    model = load_model(model_path)
    # Predict masks
    masks = model.predict(
        np.stack((vh_tiles, vv_tiles), axis=3), batch_size=1, verbose=verbose
    )
    masks.round(decimals=0, out=masks)
    # Stitch masks together
    mask = masks.reshape((n_rows, n_cols, dems, dems)) \
                .swapaxes(1, 2) \
                .reshape(n_rows * dems, n_cols * dems)  # yapf: disable

    mask[invalid_pixels] = 0
    write_mask_to_file(mask, outfile, f.GetProjection(), f.GetGeoTransform())


def pad_image(image: np.ndarray, to: int) -> np.ndarray:
    height, width = image.shape

    n_rows, n_cols = get_tile_dimensions(height, width, to)
    new_height = n_rows * to
    new_width = n_cols * to

    padded = np.zeros((new_height, new_width))
    padded[:image.shape[0], :image.shape[1]] = image
    return padded


def get_tile_dimensions(height: int, width: int, tile_size: int):
    return int(np.ceil(height / tile_size)), int(np.ceil(width / tile_size))


def tile_image(
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


if __name__ == "__main__":
    p = ArgumentParser(description=__doc__)
    p.add_argument("model_path", help="Name of the trained model")
    p.add_argument("vv_path", help="path to the calibrated VV tiff")
    p.add_argument("vh_path", help="path to the calibrated VH tiff")
    p.add_argument("outfile", help="name of the generated mask")
    p.add_argument(
        "-v", "--verbose", help="keras verbosity", default=1, type=int
    )

    args = p.parse_args()

    try:
        main(
            args.model_path, args.vv_path, args.vh_path, args.outfile,
            args.verbose
        )
    except FileNotFoundError as e:
        print(e)
