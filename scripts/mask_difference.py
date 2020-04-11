"""
 Jason Herning
 03-01-20
 mask_difference.py
 Script creates a mask to show where water has been added or subtracted
 over time.
 Sources: used https://sciience.tumblr.com/post/101722591382/finding-the-georeferenced-intersection-between-two
"""
from argparse import ArgumentParser, Namespace

import numpy as np
from osgeo import gdal


def intersection(raster1, raster2):
    """Finds the intersection of 2 raster"""
    band1 = raster1.GetRasterBand(1)
    band2 = raster2.GetRasterBand(1)
    geotransform1 = raster1.GetGeoTransform()
    geotransform2 = raster2.GetGeoTransform()

    # find each image's bounding box
    # r1 has left, top, right, bottom of dataset's bounds in geospatial coordinates.
    r1 = [geotransform1[0], geotransform1[3], geotransform1[0] + (geotransform1[1] * raster1.RasterXSize), geotransform1[3] + (geotransform1[5] * raster1.RasterYSize)]
    r2 = [geotransform2[0], geotransform2[3], geotransform2[0] + (geotransform2[1] * raster2.RasterXSize), geotransform2[3] + (geotransform2[5] * raster2.RasterYSize)]

    # find intersection between bounding boxes
    intersection = [max(r1[0], r2[0]), min(r1[1], r2[1]), min(r1[2], r2[2]), max(r1[3], r2[3])]
    if r1 != r2:
        print("different bounding boxes!")
        # check for any overlap at all...
        if (intersection[2] < intersection[0]) or (intersection[1] < intersection[3]):
            intersection = None
            print("no overlap")
            return
        else:
            print(f"intersection: {intersection}")

            left1 = int(round((intersection[0] - r1[0]) / geotransform1[1]))
            top1 = int(round((intersection[1] - r1[1]) / geotransform1[5]))
            col1 = int(round((intersection[2] - r1[0]) / geotransform1[1])) - left1
            row1 = int(round((intersection[3] - r1[1]) / geotransform1[5])) - top1

            left2 = int(round((intersection[0] - r2[0]) / geotransform2[1]))
            top2 = int(round((intersection[1] - r2[1]) / geotransform2[5]))
            col2 = int(round((intersection[2] - r2[0]) / geotransform2[1])) - left2
            row2 = int(round((intersection[3] - r2[1]) / geotransform2[5])) - top2

            if col1 != col2 or row1 != row2:
                print("ERROR: COLS and ROWS DO NOT MATCH")
            # these arrays should now have the same spatial geometry though NaNs may differ
            array1 = band1.ReadAsArray(left1, top1, col1, row1)
            array2 = band2.ReadAsArray(left2, top2, col2, row2)

    else:  # same dimensions from the get go
        col1 = raster1.RasterXSize  # = col2
        row1 = raster1.RasterYSize  # = row2
        array1 = band1.ReadAsArray()
        array2 = band2.ReadAsArray()

    return array1, array2, col1, row1, intersection


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
    mask1_ds = gdal.Open(args.first_mask)
    mask2_ds = gdal.Open(args.second_mask)

    mask1_intersect, mask2_intersect, col, row, box_intersect = intersection(mask1_ds, mask2_ds)

    mask_difference = difference(mask1_intersect, mask2_intersect)

    mask_difference_ds = gdal.GetDriverByName('GTiff').Create(args.name, col, row, bands=1)
    mask_difference_ds.SetGeoTransform((box_intersect[0], mask1_ds.GetGeoTransform()[1], 0, box_intersect[1], 0,
                                        mask1_ds.GetGeoTransform()[5]))
    mask_difference_ds.SetProjection(mask1_ds.GetProjection())

    mask_difference_ds.GetRasterBand(1).WriteArray(mask_difference)
    mask_difference_ds.GetRasterBand(1).SetNoDataValue(0)


if __name__ == '__main__':
    p = ArgumentParser()

    p.add_argument('first_mask', help='The older mask of the pair')
    p.add_argument('second_mask', help='The newer mask of the pair')
    p.add_argument('name', help='Name of the new mask')
    p.set_defaults(func=create_mask)

    args = p.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        p.print_help()