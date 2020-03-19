

import os
import numpy as np
from argparse import ArgumentParser
from osgeo import gdal




# script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
# rel_path = "2091/data.txt"
# abs_file_path = os.path.join(script_dir, rel_path)


# f = "/home/jmherning/code/asf/AI_Water/mask/test/S1B_IW_GRDH_1SDV_20190904T022842_20190904T022910_017882_021A6E_9CCA-PREDORB-30m-amp-rtc-gamma_10.tif"
# vrt = "/home/jmherning/code/asf/AI_Water/mask/test/test.vrt"



# # print(__file__)
# # print(abs_file_path)



# ds = gdal.Open(f)

# myarray = ds.ReadAsArray()

# print(myarray.sum())
# print(f"rows: {myarray.shape[0]} cols: {myarray.shape[1]}")


# x = np.array([[1, 1, 1],
#               [1, 0, 1],
#               [1, 1, 1]])

# y = np.array([[0, 0, 0],
#               [1, 0, 1],
#               [1, 1, 1]])



# print(x+y)



def mask_difference(mask_orig: np.ndarray, mask_new: np.ndarray) -> np.ndarray:
    mask_final = np.zeros(mask_orig.shape)


    for i in range(mask_orig.shape[0]):
        for j in range(mask_orig.shape[1]):
            if mask_orig[i][j] == 1 and mask_new[i][j] == 0:
                mask_final[i][j] = 1

    return mask_final
                




        

    


