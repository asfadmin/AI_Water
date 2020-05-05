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

from scripts.mask_shape import raster_boundary2shape


def intersection(raster1, raster2):
    """Finds the intersection of 2 raster"""
    band1 = raster1.GetRasterBand(1)
    band2 = raster2.GetRasterBand(1)
    transform1 = raster1.GetGeoTransform()
    transform2 = raster2.GetGeoTransform()

    # find each image's bounding box
    bounds1 = [transform1[0], transform1[3], transform1[0] + (transform1[1] * raster1.RasterXSize),
               transform1[3] + (transform1[5] * raster1.RasterYSize)]
    bounds2 = [transform2[0], transform2[3], transform2[0] + (transform2[1] * raster2.RasterXSize),
               transform2[3] + (transform2[5] * raster2.RasterYSize)]

    intersection_between_bounding_boxes = [max(bounds1[0], bounds2[0]), min(bounds1[1], bounds2[1]),
                                           min(bounds1[2], bounds2[2]), max(bounds1[3], bounds2[3])]
    if bounds1 != bounds2:
        print("different bounding boxes!")
        # check for any overlap at all...
        if (intersection_between_bounding_boxes[2] < intersection_between_bounding_boxes[0]) or (
                intersection_between_bounding_boxes[1] < intersection_between_bounding_boxes[3]):
            print("no overlap")
            return
        else:
            print(f"intersection: {intersection_between_bounding_boxes}")

            left1 = int(round((intersection_between_bounding_boxes[0] - bounds1[0]) / transform1[1]))
            top1 = int(round((intersection_between_bounding_boxes[1] - bounds1[1]) / transform1[5]))
            col1 = int(round((intersection_between_bounding_boxes[2] - bounds1[0]) / transform1[1])) - left1
            row1 = int(round((intersection_between_bounding_boxes[3] - bounds1[1]) / transform1[5])) - top1

            left2 = int(round((intersection_between_bounding_boxes[0] - bounds2[0]) / transform2[1]))
            top2 = int(round((intersection_between_bounding_boxes[1] - bounds2[1]) / transform2[5]))
            col2 = int(round((intersection_between_bounding_boxes[2] - bounds2[0]) / transform2[1])) - left2
            row2 = int(round((intersection_between_bounding_boxes[3] - bounds2[1]) / transform2[5])) - top2

            if col1 != col2 or row1 != row2:
                print("ERROR: COLS and ROWS DO NOT MATCH")

            array1 = band1.ReadAsArray(left1, top1, col1, row1)
            array2 = band2.ReadAsArray(left2, top2, col2, row2)

    else:
        col1 = raster1.RasterXSize
        row1 = raster1.RasterYSize
        array1 = band1.ReadAsArray()
        array2 = band2.ReadAsArray()

    return array1, array2, col1, row1, intersection_between_bounding_boxes


def get_mask_array(mask_file: str) -> np.ndarray:
    """Input mask TIFF file, returns nd.array"""
    f = gdal.Open(mask_file)
    mask_array = f.ReadAsArray()

    return mask_array


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
    mask1 = gdal.Open(args.first_mask)
    mask2 = gdal.Open(args.second_mask)

    mask1_intersect, mask2_intersect, col, row, box_intersect = intersection(mask1, mask2)
    mask_difference = difference(mask1_intersect, mask2_intersect)

    driver = gdal.GetDriverByName('GTiff')
    output_raster = driver.Create(args.name, col, row, bands=1)
    output_raster.SetGeoTransform((box_intersect[0], mask1.GetGeoTransform()[1], 0, box_intersect[1], 0,
                                   mask1.GetGeoTransform()[5]))
    output_raster.SetProjection(mask1.GetProjection())

    output_raster.GetRasterBand(1).WriteArray(mask_difference)
    output_raster.GetRasterBand(1).SetNoDataValue(0)

    output_raster.FlushCache()

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
