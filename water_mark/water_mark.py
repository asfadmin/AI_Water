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
# - water_mark:
#   - water_mark.py
#   - set_up_water_mark.py
#   - download-all-<nums>.py (from asf hyp3)
#   - identify_water.py
#   - inputs:
#       - downloadWaterData.py
#       - gdal_reclassify.py
#       - worldMask:
#       - sar.tif (1+)
#       - syntheticTriainingData<date>: (output directory made automatically)
#           - sar: (1+)
#               - Original and tiled: VV, VH, and Mask images.
###############################################################################

import argparse
import os
import shutil
from osgeo import gdal
from identify_water import main as idw_main
from datetime import date


def make_database():
    dataList = []
    for f in os.listdir(os.path.join(os.getcwd(), 'inputs')):
        if f.endswith('.tif'):
            dataList.append(f)
    dataList.sort()
    data = {}
    for info in range(0, len(dataList), 2):
        sar = dataList[info]
        sar = sar[:-7]
        vv = dataList[info+1]
        vh = dataList[info]
        data[sar] = [vv, vh]
    return data


def make_output_dir(outDir, dataDict):
    if os.path.exists(outDir):
        shutil.rmtree(outDir)
    os.mkdir(outDir)
    for sar in dataDict:
        os.mkdir(os.path.join(os.getcwd(), outDir, sar))
    return


def copy_vv_vh_to_inputs(outDir, dataDict):
    inputsPath = os.path.join(os.getcwd(), 'inputs')
    for sar, vvvhband in dataDict.items():
        shutil.copy(os.path.join(inputsPath, vvvhband[0]),
                    os.path.join(os.getcwd(), outDir, sar))
        shutil.copy(os.path.join(inputsPath, vvvhband[1]),
                    os.path.join(os.getcwd(), outDir, sar))
    return


def make_masks(outDir, dataDict):
    for sar, vvvhband in dataDict.items():
        inputPath = os.path.join(os.getcwd(), 'inputs')
        renamePath = os.path.join(os.getcwd(), outDir, sar)
        idw_main(os.path.join(inputPath, vvvhband[0]),
                 os.path.join(inputPath, vvvhband[1]))
        # rename 'mask-0.tif' -> 'Mask_<sar>.tif'
        os.rename(renamePath + 'mask-0.tif', renamePath + sar + '.tif')
    return


def tile_vv_vh_mask(outDir, mxmTileSize):
    for sar in os.listdir(os.path.join(os.getcwd(), outDir)):
        for tifName in os.listdir(os.path.join(os.getcwd(), outDir, sar)):
            if tifName.endswith('VV.tif'):
                tile(outDir, tifName, sar, mxmTileSize, False)
            elif tifName.endswith('VH.tif'):
                tile(outDir, tifName, sar, mxmTileSize, False)
            elif tifName.beginswith('Mask'):
                tile(outDir, tifName, sar, mxmTileSize, True)
    return


def tile(outDir, tifName, sar, mxmTileSize, isMask):
    label = ''
    if isMask:
        label = 'Mask_'
    else:
        label = 'Image_'
    tifData = gdal.Open(os.path.join(os.getcwd(), outDir, sar, tifName))
    xStep, yStep = mxmTileSize, mxmTileSize
    xSize, ySize = tifData.RasterXSize, tifData.RasterYSize
    count = 0
    for x in range(0, xSize, xStep):
        for y in range(0, ySize, yStep):
            # fileName = '<Image|Mask>_<sar>_<0-9+>.tif'
            fileName = label + tifName[:-4] + '_' + str(count) + '.tif'
            gdal.Translate(os.path.join(os.getcwd(), outDir, sar, fileName),
                           tifName,
                           srcWin=[x, y, xStep, yStep],
                           format="GTiff")
            count += 1
    return


def main():
    # set tile size manually here (comment out parser block below)
    # mxmTileSize = 512

    # cmd line argumnet parser for tile size
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=int, default=512)
    args = parser.parse_args()
    mxmTileSize = args.s

    synData = 'syntheticTriainingData'+date.isoformat(date.today())  # outDir
    data = make_database()

    make_output_dir(synData, data)
    copy_vv_vh_to_inputs(synData, data)
    make_masks(synData, data)
    tile_vv_vh_mask(synData, mxmTileSize)


if __name__ == '__main__':
    main()
