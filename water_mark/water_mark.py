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
# '-waterMask'  to use european water mask
# '-size <int>' to set mxmTileSize
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


def make_output_dir(outDir: str, dataDict: Dict[str, Tuple[str, str]]) -> None:
    if os.path.exists(outDir):
        shutil.rmtree(outDir)
    os.mkdir(outDir)
    for sar in dataDict:
        os.mkdir(os.path.join(outDir, sar))


def delete_junk(directory):
    for f in os.listdir(directory):
        if ('.shp') in f:
            os.remove(os.path.join('inputs', f))
        if ('.shx') in f:
            os.remove(os.path.join('inputs', f))
        if ('.prj') in f:
            os.remove(os.path.join('inputs', f))
        if ('.dbf') in f:
            os.remove(os.path.join('inputs', f))


def cut_worldMask_to_sar():
    for f in os.listdir('inputs'):
        if '.tif' in f:
            cutSize = os.path.join('inputs', f)
            cutSizeShp = f"{cutSize[:-4]}.shp"  # change extension
            inputFile = os.path.join('inputs', 'worldMask', 'worldMask.vrt')
            outputFile = os.path.join('inputs', f"{f[:-4]}_Mask.tif")
            subprocess.call(
                f"gdaltindex {cutSizeShp} {cutSize}",
                shell=True
            )
            gdal.Warp(
                outputFile,
                inputFile,
                options=['-cutline', cutSizeShp, '-crop_to_cutline']
            )
            delete_junk('inputs')


def move_sar_mask_to_outDir(outDir):
    for sar in os.listdir(outDir):
        image = os.path.join('inputs', f"{sar}.tif")
        mask = os.path.join('inputs', f"{sar}Mask.tif")
        program = os.path.join('inputs', 'gdal_reclassify.py')
        copyLocation = os.path.join(outDir, sar)
        shutil.copy(image, copyLocation)
        os.rename(
            os.path.join(outDir, sar, f"{sar}.tif"),
            os.path.join(outDir, sar, f"{sar}_Image.tif")
        )
        shutil.copy(mask, copyLocation)
        shutil.copy(program, copyLocation)
        os.remove(mask)


def cut_sar_to_tiles(outDir, mxmTileSize):
    for sar in os.listdir(outDir):
        image = os.path.join(outDir, sar,  f"{sar}_Image.tif")
        imageData = gdal.Open(image)
        xStep, yStep = mxmTileSize, mxmTileSize
        xSize, ySize = imageData.RasterXSize, imageData.RasterYSize
        count = 0
        for x in range(0, xSize, xStep):
            for y in range(0, ySize, yStep):
                # fileName = 'Image_<sar>_<0-9+>.tif'
                fileName = f"Image_{sar}_{count}.tif"
                outputFile = os.path.join(outDir, sar, fileName)
                inputFile = image
                gdal.Translate(
                    outputFile,
                    inputFile,
                    srcWin=[x, y, xStep, yStep],
                    format="GTiff"
                )
                count += 1


def clip_mask_to_sar(outDir):
    for sar in os.listdir(outDir):
        for tile in os.listdir(os.path.join(outDir, sar)):
            cutSize = tile
            cutSizeShp = f"{cutSize[:-4]}.shp"  # change ext
            inputFile = sar
            outputFile = f"Mask_{tile[5:]}"
            subprocess.call(f"gdaltindex {cutSizeShp} {cutSize}", shell=True)
            gdal.Warp(
                outputFile,
                inputFile
                options=['-cutline', cutSizeShp, '-crop_to_cutline']
            )
            delete_junk('inputs')


def trim_masks(outDir, mxmTileSize):
    for sar in os.listdir(outDir):
        for f in os.listdir(os.path.join(outDir, sar)):
            if f == f"{sar}Image.tif" or f == f"{sar}Mask.tif" or f.endswith('.py'):
                pass
            else:
                resizedImage = f"RS{f}"
                outputFile = resizedImage
                inputFile = f
                gdal.Translate(
                    outputFile,
                    inputFile,
                    options=["-outsize", mxmTileSize, mxmTileSize]
                )
                os.remove(os.path.join(outDir, f))
                os.rename(resizedImage, resizedImage[2:])  # remove 'RS'


def reclassify_mask(outDir):
    for sar in os.listdir(outDir):
        for f in os.listdir(os.path.join(outDir, sar)):
            if 'Mask' in f:
                python = 'python'
                windowsMode = detect_windows_OS()
                if not windowsMode:
                    python = 'python3'
                inputFile = f
                outputFile = f"Binary{f}"
                processDataset(
                    src_file=inputFile,
                    dst_file=outputFile,
                    in_classes='<=45, <=100',
                    out_classes='0, 1',
                    default=0,
                    nodata=True,
                    output_format='GTiff',
                    compression='COMPRESS=LZW'
                )
                os.remove(f)
                oldName = os.path.join(outDir, f"Binary_{f}")
                newName = os.path.join(outDir, f)
                os.rename(oldName, newName)


def clean_up(outDir):
    for sar in os.listdir(outDir):
        os.remove(os.path.join(outDir, sar, 'gdal_reclassify.py'))


def copy_vv_vh_to_inputs(outDir, dataDict):
    for sar, vvvhband in dataDict.items():
        shutil.copy(
            os.path.join('inputs', vvvhband[0]),
            os.path.join(outDir, sar)
        )
        shutil.copy(
            os.path.join('inputs', vvvhband[1]),
            os.path.join(outDir, sar)
        )


def make_masks(outDir, dataDict):
    count = 0
    for sar, vvvhband in dataDict.items():
        renamePath = os.path.join(outDir, sar)
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


def tile(outDir, tifName, sar, mxmTileSize, isMask):
    label = 'temp'
    if isMask:
        label = 'Mask'
    else:
        label = 'Image'
    tif = os.path.join(outDir, sar, tifName)
    tifData = gdal.Open(tif)
    xStep, yStep = mxmTileSize, mxmTileSize
    xSize, ySize = tifData.RasterXSize, tifData.RasterYSize
    count = 0
    for x in range(0, xSize, xStep):
        for y in range(0, ySize, yStep):
            # fileName = '<Image|Mask>_<sar>_<0-9+>.tif'
            fileName = f"{label}_{tifName[:-4]}_{count}.tif"
            outputFile = os.path.join(outDir, sar, fileName)
            inputFile = tif
            gdal.Translate(
                outputFile,
                inputFile,
                srcWin=[x, y, xStep, yStep],
                format="GTiff"
            )
            count += 1


def tile_vv_vh_mask(outDir, mxmTileSize):
    for sar in os.listdir(outDir):
        for tifName in os.listdir(os.path.join(outDir, sar)):
            if tifName.endswith('VV.tif'):
                tile(outDir, tifName, sar, mxmTileSize, False)
            elif tifName.endswith('VH.tif'):
                tile(outDir, tifName, sar, mxmTileSize, False)
            elif tifName.startswith('Mask'):
                tifName = tifName[5:]  # remove leading 'Mask_'
                tile(outDir, tifName, sar, mxmTileSize, True)


def main(**flags):
    size = None
    worldMask = None
    if not flags:
        parser = argparse.ArgumentParser()
        parser.add_argument('-size', type=int, default=512)
        parser.add_argument('-worldMask, action='store_true')
        args = parser.parse_args()
        mxmTileSize = args.size
        worldMask = args.worldMask
    else:
        mxmTileSize = flags.get('mxmTileSize')
        worldMask = flagss.get('worldMask')

    outDir = f"syntheticTriainingData{date.isoformat(date.today())}"
    data = make_database()

    make_output_dir(outDir, data)
    if worldMask:
        cut_worldMask_to_sar()
        move_sar_mask_to_outDir(outDir)
        cut_sar_to_tiles(outDir, mxmTileSize)
        clip_mask_to_sar(outDir)
        trim_masks(outDir, mxmTileSize)
        reclassify_mask(outDir)
        clean_up(outDir)
        return
    copy_vv_vh_to_inputs(outDir, data)
    make_masks(outDir, data)
    tile_vv_vh_mask(outDir, mxmTileSize)


if __name__ == '__main__':
    main()
