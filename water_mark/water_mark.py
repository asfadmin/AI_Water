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
#   - download-all-<nums>.py (from asf hyp3)
###############################################################################

import argparse
import os
import shutil
from osgeo import gdal
from identify_water import main as idw_main
from datetime import date
from typing import Tuple, Dict, List

from etl_water_mark import detect_windows_OS
from gdal_reclassify import processDataset


def make_database() -> Dict[str, Tuple[str, str]]:
    data_list = []
    for f in os.listdir('inputs'):
        if f.endswith('.tif'):
            data_list.append(f)
    data_list.sort()
    data = {}
    for info in range(0, len(data_list), 2):
        sar = data_list[info]
        sar = sar[:-7]
        vv = data_list[info+1]
        vh = data_list[info]
        data[sar] = (vv, vh)
    return data


def make_output_dir(out_dir: str, data_dict: Dict[str, Tuple[str, str]]) -> None:
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.mkdir(out_dir)
    for sar in data_dict:
        os.mkdir(os.path.join(out_dir, sar))


def delete_junk(target_dir):
    for f in os.listdir(directory):
        if ('.shp') in f:
            os.remove(os.path.join('inputs', f))
        if ('.shx') in f:
            os.remove(os.path.join('inputs', f))
        if ('.prj') in f:
            os.remove(os.path.join('inputs', f))
        if ('.dbf') in f:
            os.remove(os.path.join('inputs', f))


def cut_world_mask_to_sar():
    for f in os.listdir('inputs'):
        if '.tif' in f:
            cut_size = os.path.join('inputs', f)
            cut_size_shp = f"{cut_size[:-4]}.shp"  # change extension
            input_file = os.path.join('inputs', 'world_mask', 'world_mask.vrt')
            output_file = os.path.join('inputs', f"{f[:-4]}_Mask.tif")
            subprocess.call(
                f"gdaltindex {cut_size_shp} {cut_size}",
                shell=True
            )
            gdal.Warp(
                output_file,
                input_file,
                options=['-cutline', cut_size_shp, '-crop_to_cutline']
            )
            delete_junk('inputs')


def move_sar_mask_to_out_dir(out_dir):
    for sar in os.listdir(out_dir):
        image = os.path.join('inputs', f"{sar}.tif")
        mask = os.path.join('inputs', f"{sar}Mask.tif")
        program = os.path.join('inputs', 'gdal_reclassify.py')
        copy_location = os.path.join(out_dir, sar)
        shutil.copy(image, copy_location)
        os.rename(
            os.path.join(out_dir, sar, f"{sar}.tif"),
            os.path.join(out_dir, sar, f"{sar}_Image.tif")
        )
        shutil.copy(mask, copy_location)
        shutil.copy(program, copy_location)
        os.remove(mask)


def cut_sar_to_tiles(out_dir, mxm_tile_size):
    for sar in os.listdir(out_dir):
        image = os.path.join(out_dir, sar,  f"{sar}_Image.tif")
        imageData = gdal.Open(image)
        xStep, yStep = mxm_tile_size, mxm_tile_size
        xSize, ySize = imageData.RasterXSize, imageData.RasterYSize
        count = 0
        for x in range(0, xSize, xStep):
            for y in range(0, ySize, yStep):
                # fileName = 'Image_<sar>_<0-9+>.tif'
                fileName = f"Image_{sar}_{count}.tif"
                output_file = os.path.join(out_dir, sar, fileName)
                input_file = image
                gdal.Translate(
                    output_file,
                    input_file,
                    srcWin=[x, y, xStep, yStep],
                    format="GTiff"
                )
                count += 1


def clip_mask_to_sar(out_dir):
    for sar in os.listdir(out_dir):
        for tile in os.listdir(os.path.join(out_dir, sar)):
            cut_size = tile
            cut_size_shp = f"{cut_size[:-4]}.shp"  # change ext
            input_file = sar
            output_file = f"Mask_{tile[5:]}"
            subprocess.call(f"gdaltindex {cut_size_shp} {cut_size}", shell=True)
            gdal.Warp(
                output_file,
                input_file
                options=['-cutline', cut_size_shp, '-crop_to_cutline']
            )
            delete_junk('inputs')


def trim_masks(out_dir, mxm_tile_size):
    for sar in os.listdir(out_dir):
        for f in os.listdir(os.path.join(out_dir, sar)):
            if f == f"{sar}Image.tif" or f == f"{sar}Mask.tif" or f.endswith('.py'):
                pass
            else:
                resizedImage = f"RS{f}"
                output_file = resizedImage
                input_file = f
                gdal.Translate(
                    output_file,
                    input_file,
                    options=["-outsize", mxm_tile_size, mxm_tile_size]
                )
                os.remove(os.path.join(out_dir, f))
                os.rename(resizedImage, resizedImage[2:])  # remove 'RS'


def reclassify_mask(out_dir):
    for sar in os.listdir(out_dir):
        for f in os.listdir(os.path.join(out_dir, sar)):
            if 'Mask' in f:
                python = 'python'
                windowsMode = detect_windows_OS()
                if not windowsMode:
                    python = 'python3'
                input_file = f
                output_file = f"Binary{f}"
                processDataset(
                    src_file=input_file,
                    dst_file=output_file,
                    in_classes='<=45, <=100',
                    out_classes='0, 1',
                    default=0,
                    nodata=True,
                    output_format='GTiff',
                    compression='COMPRESS=LZW'
                )
                os.remove(f)
                old_name = os.path.join(out_dir, f"Binary_{f}")
                new_name = os.path.join(out_dir, f)
                os.rename(old_name, new_name)


def clean_up(out_dir):
    for sar in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, sar, 'gdal_reclassify.py'))


def copy_vv_vh_to_inputs(out_dir, data_dict):
    for sar, vvvhband in data_dict.items():
        shutil.copy(
            os.path.join('inputs', vvvhband[0]),
            os.path.join(out_dir, sar)
        )
        shutil.copy(
            os.path.join('inputs', vvvhband[1]),
            os.path.join(out_dir, sar)
        )


def make_masks(out_dir, data_dict):
    count = 0
    for sar, vvvhband in data_dict.items():
        renamePath = os.path.join(out_dir, sar)
        print(f"{count} masks made")
        idw_main(
            os.path.join('inputs', vvvhband[0]),
            os.path.join('inputs', vvvhband[1])
        )
        count += 1
        # rename 'mask-0.tif' to 'Mask_<sar>.tif'
        os.rename(
            'mask-0.tif',
            os.path.join(renamePath, f"Mask_{sar}.tif")
        )


def tile(out_dir, tif_name, sar, mxm_tile_size, isMask):
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
            # fileName = '<Image|Mask>_<sar>_<0-9+>.tif'
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


def tile_vv_vh_mask(out_dir, mxm_tile_size):
    for sar in os.listdir(out_dir):
        for tif_name in os.listdir(os.path.join(out_dir, sar)):
            if tif_name.endswith('VV.tif'):
                tile(out_dir, tif_name, sar, mxm_tile_size, False)
            elif tif_name.endswith('VH.tif'):
                tile(out_dir, tif_name, sar, mxm_tile_size, False)
            elif tif_name.startswith('Mask'):
                tif_name = tif_name[5:]  # remove leading 'Mask_'
                tile(out_dir, tif_name, sar, mxm_tile_size, True)


def main(**flags):
    if not flags:
        parser = argparse.ArgumentParser()
        parser.add_argument('-size', type=int, default=512)
        parser.add_argument('-world_mask, action='store_true')
        args = parser.parse_args()
        mxm_tile_size = args.size
        world_mask = args.world_mask
    else:
        mxm_tile_size = flags.get('mxm_tile_size')
        world_mask = flags.get('world_mask')

    out_dir = f"syntheticTriainingData{date.isoformat(date.today())}"
    data = make_database()

    make_output_dir(out_dir, data)
    if world_mask:
        cut_world_mask_to_sar()
        move_sar_mask_to_out_dir(out_dir)
        cut_sar_to_tiles(out_dir, mxm_tile_size)
        clip_mask_to_sar(out_dir)
        trim_masks(out_dir, mxm_tile_size)
        reclassify_mask(out_dir)
        clean_up(out_dir)
        return
    copy_vv_vh_to_inputs(out_dir, data)
    make_masks(out_dir, data)
    tile_vv_vh_mask(out_dir, mxm_tile_size)


if __name__ == '__main__':
    main()
