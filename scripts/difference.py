

import os
import numpy as np
from argparse import ArgumentParser, Namespace
from osgeo import gdal




# script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
# rel_path = "2091/data.txt"
# abs_file_path = os.path.join(script_dir, rel_path)


# f = "/home/jmherning/code/asf/AI_Water/mask/test/S1B_IW_GRDH_1SDV_20190904T022842_20190904T022910_017882_021A6E_9CCA-PREDORB-30m-amp-rtc-gamma_10.tif"
# vrt = "/home/jmherning/code/asf/AI_Water/mask/test/test.vrt"



# print(__file__)
# print(abs_file_path)



# ds = gdal.Open(f)

# myarray = ds.ReadAsArray()

# print(myarray.sum())
# print(f"rows: {myarray.shape[0]} cols: {myarray.shape[1]}")


def get_mask_array(mask_file: str) -> np.ndarray:
    """Input mask TIFF file, returns nd.array"""
    
    g = gdal.Open(mask_file)
    mask_array = g.ReadAsArray()

    return mask_array




#TODO set dimensions to the bigger mask!
def mask_difference(mask_orig: np.ndarray, mask_new: np.ndarray) -> np.ndarray:
    """takes in mask"""

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

    mask = mask_difference(oldma, newma)

    f = gdal.Open(args.olderMask)
    
    write_mask_to_file(mask, args.name, f.GetProjection(), f.GetGeoTransform())



        

    


