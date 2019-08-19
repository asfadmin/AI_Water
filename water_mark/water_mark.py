###############################################################################
#########   __        __    _            __  __            _    ###############
##########  \ \      / /_ _| |_ ___ _ __|  \/  | __ _ _ __| | __ ##############
###########  \ \ /\ / / _` | __/ _ \ '__| |\/| |/ _` | '__| |/ /  #############
############  \ V  V / (_| | ||  __/ |  | |  | | (_| | |  |   <    ############
############   \_/\_/ \__,_|\__\___|_|  |_|  |_|\__,_|_|  |_|\_\  #############
###########                                                      ##############
##########     George Meier 15 July 2019                        ###############
#########      ASF Water Detection AI Training Data Generator  ################
########################################################################80chars
# This program, given VV and VH sar images, outputs a directory of tiled and
# labeled sar and mask images.
#
# Begin by setting up the file directory shown below
# When identify_water.py runs, a gui will appear running an algorithm to
# generate 'synthetic' water mask tifs.  Use the magnifying glass icon to zoom
# in on the lower lefthand corner.  Click the magnifying glass agin to change
# the curser back to normal, then click to draw a box over an area of interest.
# Try many areas and change the bin size until the mask looks like a good fit
# to its corresponding sar images.  When satisfied click the make mask button.

###############################################################################
# Python3
# Windows admin powershell or Linux
# cmd line arguments
#   '-waterMask' '-size=<int>' to set mxm_tile_size
# import function w/ arguments
#   'main(waterMask=True, size=<int>)' # NOTE 512 IS NOT DEFAULT HERE
#
# - water_mark:
#   - inputs:
#       - sar.tif (1+)
#       - identify_water.py  (neede for waterMask)
#       - gdal_reclassify.py (needed for waterMAsk)
#   - syntheticTriainingData<date>: (output directory made automatically)
#       - sar: (1+)
#           - Original and tiled VV, VH, and Mask images.
#   - water_mark.py
#   - etl_water_mark.py
#   - download-all-<nums>.py (from ASF hyp3)
###############################################################################

import argparse
import os
import shutil
from osgeo import gdal
from datetime import date
from typing import Tuple, Dict, List
from gdal_reclassify import processDataset

import sys
sys.path.append('../scripts/')
from identify_water import main as idw_main


def make_database() -> Dict[str, Tuple[str, str]]:
    data_list = sorted([fname for fname in os.listdir('inputs') if fname.endswith('.tif')])
    '''Take every pair of consecutive file names and add them to
    data under a common key. This assumes that each pair of files
    shares a common prefix and that there are no stray unpaired images
    in the directory.'''
    data = {}
    for i in range(0, len(data_list), 2):
        sar_name = data_list[i]
        sar_name = sar_name[:-7]
        vv = data_list[i+1]
        vh = data_list[i]
        data[sar_name] = (vv, vh)
    return data


def make_output_dir(out_dir: str, data_dict: Dict[str, Tuple[str, str]]) -> None:
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.mkdir(out_dir)
    for sar in data_dict:
        os.mkdir(os.path.join(out_dir, sar))


def delete_junk(target_dir: str) -> None:
    for f_name in os.listdir(target_dir):
        if ('.shp') in f_name:
            os.remove(os.path.join('inputs', f_name))
        if ('.shx') in f_name:
            os.remove(os.path.join('inputs', f_name))
        if ('.prj') in f_name:
            os.remove(os.path.join('inputs', f_name))
        if ('.dbf') in f_name:
            os.remove(os.path.join('inputs', f_name))


def copy_vv_vh_to_inputs(out_dir: str, data_dict: Dict[str. Tuple[str, str]]) -> None:
    for sar, vv_vh_band in data_dict.items():
        shutil.copy(
            os.path.join('inputs', vv_vh_band[0]),
            os.path.join(out_dir, sar)
        )
        shutil.copy(
            os.path.join('inputs', vv_vh_band[1]),
            os.path.join(out_dir, sar)
        )


def make_masks(out_dir: str, data_dict: Dict[str. Tuple[str, str]]) -> None:
    count = 0
    for sar, vv_vh_band in data_dict.items():
        renamePath = os.path.join(out_dir, sar)
        print(f"{count} masks made")
        idw_main(
            os.path.join('inputs', vv_vh_band[0]),
            os.path.join('inputs', vv_vh_band[1])
        )
        count += 1
        os.rename(
            'mask-0.tif',
            os.path.join(renamePath, f"Mask_{sar}.tif")
        )


def tile(out_dir: str, tif_name: str, sar: str, mxm_tile_size: int, isMask: bool) -> None:
    label = 'temp'
    if isMask:
        label = 'Mask'
    else:
        label = 'Image'
    tif = os.path.join(out_dir, sar, tif_name)
    tifData = gdal.Open(tif)
    xStep, yStep = mxm_tile_size, mxm_tile_size
    xSize, ySize = tifData.RasterXSize, tifData.RasterYSize
    count = 0
    for x in range(0, xSize, xStep):
        for y in range(0, ySize, yStep):
            fileName = f"{label}_{tif_name[:-4]}_{count}.tif"
            output_file = os.path.join(out_dir, sar, fileName)
            input_file = tif
            gdal.Translate(
                output_file,
                input_file,
                srcWin=[x, y, xStep, yStep],
                format="GTiff"
            )
            count += 1


def tile_vv_vh_mask(out_dir: str, mxm_tile_size: int) -> None:
    for sar in os.listdir(out_dir):
        for tif_name in os.listdir(os.path.join(out_dir, sar)):
            if tif_name.endswith('VV.tif'):
                tile(out_dir, tif_name, sar, mxm_tile_size, False)
            elif tif_name.endswith('VH.tif'):
                tile(out_dir, tif_name, sar, mxm_tile_size, False)
            elif tif_name.startswith('Mask_'):
                tif_name = tif_name[5:]  # remove leading 'Mask_'
                tile(out_dir, tif_name, sar, mxm_tile_size, True)


def setup_data_wrapper(args: Namespace) -> None:
    mxm_tile_size = args.size
    out_dir = f"syntheticTriainingData{date.isoformat(date.today())}"
    data = make_database()
    make_output_dir(out_dir, data)
    copy_vv_vh_to_inputs(out_dir, data)
    make_masks(out_dir, data)
    tile_vv_vh_mask(out_dir, mxm_tile_size)


if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument('size', type=int, default=512)
    args = p.parse_args()
    p.set_defaults(func=setup_data_wrapper)
    args = p.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        p.print_help()
