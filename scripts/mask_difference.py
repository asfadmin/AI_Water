"""
 Jason Herning
 03-01-20
 mask_difference.py
 Script creates a mask to show where water has been added or subtracted
 over time.
"""
from argparse import ArgumentParser, Namespace
import numpy as np
from osgeo import gdal

from src.hyp3lib_functions import overlap_indices, geotiff_overlap, data2geotiff, geotiff2data, raster_boundary2shape


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
    for i in range(mask_final.shape[0]):
        for j in range(mask_final.shape[1]):
            if first_mask[i][j] == 0 and second_mask[i][j] == 1:
                mask_final[i][j] = 1
            if first_mask[i][j] == 1 and second_mask[i][j] == 0:
                mask_final[i][j] = 2

    return mask_final


def create_mask(args: Namespace) -> None:
    """main function to generate difference mask and optionally shape"""
    _, mask1_transform, projection, epsg, data_type, no_data = geotiff2data(args.first_mask)
    mask1_intersect, mask2_intersect, col, row, bounds = intersection(args.first_mask, args.second_mask)
    mask_difference = difference(mask1_intersect, mask2_intersect)
    transform = (bounds[0], mask1_transform[1], 0, bounds[3], 0, mask1_transform[5])
    data2geotiff(mask_difference, transform, projection, data_type, 0, args.name)

    if args.shape:
        raster_boundary2shape(args.name, None, args.name, use_closing=False)


if __name__ == '__main__':
    p = ArgumentParser()

    p.add_argument('first_mask', help='The older mask of the pair')
    p.add_argument('second_mask', help='The newer mask of the pair')
    p.add_argument('name', help='Name of the new mask')
    p.add_argument('--shape', default=False, action='store_true', help='Also return a shape file')
    p.set_defaults(func=create_mask)

    args = p.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        p.print_help()
