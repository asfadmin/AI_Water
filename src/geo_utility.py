"""
 Created By:   Jason Herning
 File Name:    geo_utility.py
 Description:  Toolbox of functions to help process GeoTIFFs.
"""

import os
import itertools
from osgeo import gdal
from src.model import load_model
from src.config import NETWORK_DEMS as dems
import numpy as np
from shapely.geometry import Polygon, shape
import fiona

from src.hyp3lib_functions import overlap_indices, geotiff_overlap


# TODO: sepearte translate as sperate function that can be tested. (maybe)
def write_tiles(input_tif: str, output_directory: str, tile_size: int, name: str):
    """Creates tiles of given dimension out of input tif file"""
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


# TODO: Cut edge fill on final mask (make it more pretty!)
# TODO: SHould use pathlib as inputs
def create_water_mask(
        model_path: str, vv_path: str, vh_path: str, outfile: str, verbose: int = 0
):
    if not os.path.isfile(vv_path):
        raise FileNotFoundError(f"Tiff '{vv_path}' does not exist")

    if not os.path.isfile(vh_path):
        raise FileNotFoundError(f"Tiff '{vh_path}' does not exist")

    # Grabs corner coordinates of the shapefile
    glacier_check = gdal.Open(vh_path)
    width = glacier_check.RasterXSize
    height = glacier_check.RasterYSize
    gt = glacier_check.GetGeoTransform()
    minx = gt[0]
    miny = gt[3] + width*gt[4] + height*gt[5]
    maxx = gt[0] + width*gt[1] + height*gt[2]
    maxy = gt[3]    
    cornercoods = Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)])
    
    # glacier_database = 'glacier_database'
    glacier_C_database = 'glacier_C_database'
    
    # iterating over all glaciers in glacier database
    for files in os.listdir(glacier_C_database):
        if files.endswith('shp'):
            # Open the shapefile
            with fiona.open(glacier_C_database + '/' + files) as shapefile:
                # Iterate over the records
                for record in shapefile:
                    # Get the geometry from the record (currently only grabs geometry need to grab corner coords instead)
                    # Can do that with the database file 
                    # Example: print(dbfread.read('path to dbf file'))
                    # will also need to import dbfread
                    geometry = shape(record['geometry'])
                    if cornercoods.intersects(geometry):
                        # TODO: need to add the code to register it as a glacier to the model
                        break
        else:
            continue

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

def intersection(raster1: str, raster2: str):
    """Takes in the path of 2 GeoTiff raster's. Then returns the intersection between them"""

    raster1_ds = gdal.Open(raster1)
    raster2_ds = gdal.Open(raster2)
    band1 = raster1_ds.GetRasterBand(1)
    band2 = raster2_ds.GetRasterBand(1)

    raster1_polygon, raster2_polygon, overlap, _, pixel_size = geotiff_overlap(raster1, raster2, 'intersection')
    x1, y1, col1, row1 = overlap_indices(raster1_polygon, overlap, pixel_size)
    x2, y2, col2, row2 = overlap_indices(raster2_polygon, overlap, pixel_size)

    array1 = band1.ReadAsArray(x1, y1, col1, row1)
    array2 = band2.ReadAsArray(x2, y2, col2, row2)

    return array1, array2, col1, row1, overlap.GetEnvelope()


def difference(first_mask: np.ndarray, second_mask: np.ndarray) -> np.ndarray:
    """takes in two mask,  return mask with a 1 for water added,
       and 2 for water removed. """
    mask_final = np.zeros(first_mask.shape)
    gained = np.where(
        np.logical_and(first_mask == 0, second_mask == 1)
    )
    lost = np.where(
        np.logical_and(first_mask == 1, second_mask == 0)
    )
    mask_final[gained] = 1
    mask_final[lost] = 2
    return mask_final