

import os
import numpy as np
from argparse import ArgumentParser, Namespace
from osgeo import gdal


def get_mask_array(mask_file: str) -> np.ndarray:
    """Input mask TIFF file, returns nd.array"""
    
    g = gdal.Open(mask_file)
    mask_array = g.ReadAsArray()

    return mask_array




#TODO set dimensions to the bigger mask!
def water_added(mask_orig: np.ndarray, mask_new: np.ndarray) -> np.ndarray:
    """takes in two mask from same region, return mask of water added"""

    mask_final = np.zeros(mask_new.shape)

    # print(f"old mask: {mask_orig.shape} new mask: {mask_new.shape}")
    for i in range(mask_final.shape[0]):
        for j in range(mask_final.shape[1]):
            if mask_orig[i][j] == 0 and mask_new[i][j] == 1:
                mask_final[i][j] = 1

    return mask_final



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





                

if __name__ == '__main__':
    p = ArgumentParser()

    p.add_argument('olderMask', help='The oldest mask')
    p.add_argument('newerMask', help='The more recent mask')
    p.add_argument('name', help ='Name of mask that shows the added water')

    args = p.parse_args()


    oldma = get_mask_array(args.olderMask)
    newma = get_mask_array(args.newerMask)

    mask = water_added(oldma, newma)

    f = gdal.Open(args.olderMask)
    
    write_mask_to_file(mask, args.name, f.GetProjection(), f.GetGeoTransform())



        

    


