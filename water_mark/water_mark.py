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
# '-waterMask True' to use european water mask
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
import sys
from osgeo import gdal
from identify_water import main as idw_main
from datetime import date
from typing import Tuple, Dict, List


def make_database() -> Dict[str, Tuple[str, str]]:
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
        data[sar] = (vv, vh)
    return data


def make_output_dir(outDir, dataDict) -> None:
    if os.path.exists(outDir):
        shutil.rmtree(outDir)
    os.mkdir(outDir)
    for sar in dataDict:
        os.mkdir(os.path.join(os.getcwd(), outDir, sar))


def cut_worldMask_to_sar() -> None:
    inputsPath = os.path.join(os.getcwd(), 'inputs')
    for f in os.listdir(inputsPath):
        if '.tif' in f:
            cutSize = os.path.join(inputsPath, f)
            cutSizeShp = cutSize[:-4]+'.shp'  # change extension
            input = os.path.join(inputsPath, 'worldMask',
                                 'worldMask.vrt')
            output = os.path.join(inputsPath, f[:-4]+'_Mask.tif')
            subprocess.call(f"gdaltindex {cutSizeShp} {cutSize}",
                            shell=True)
            subprocess.call(f"gdalwarp -cutline {cutSizeShp} -crop_to_cutline \
                            {input} {output}",
                            shell=True)
            # delete junk
            for f in os.listdir(inputsPath):
                if ('.shp') in f:
                    os.remove(os.path.join(inputsPath, f))
                if ('.shx') in f:
                    os.remove(os.path.join(inputsPath, f))
                if ('.prj') in f:
                    os.remove(os.path.join(inputsPath, f))
                if ('.dbf') in f:
                    os.remove(os.path.join(inputsPath, f))


def move_sar_mask_to_outDir(outDir) -> None:
    for sar in os.listdir(outDir):
        inputsPath = os.path.join(os.getcwd(), 'inputs')
        image = os.path.join(inputsPath, sar + '.tif')
        mask = os.path.join(inputsPath, sar + '_Mask.tif')
        program = os.path.join(inputsPath, 'gdal_reclassify.py')
        copyLocation = os.path.join(outDir, sar)
        shutil.copy(image, copyLocation)
        os.rename(os.path.join(outDir, sar, sar+'.tif'),
                               os.path.join(outDir, sar, sar+'_Image.tif'))
        shutil.copy(mask, copyLocation)
        shutil.copy(program, copyLocation)
        os.remove(mask)


def cut_sar_to_tiles(outDir, mxmTileSize) -> None:
    for sar in os.listdir(outDir):
        image = os.path.join(outDir, sar,  sar + '_Image.tif')
        imageData = gdal.Open(image)
        xStep, yStep = mxmTileSize, mxmTileSize
        xSize, ySize = imageData.RasterXSize, imageData.RasterYSize
        count = 0
        for x in range(0, xSize, xStep):
            for y in range(0, ySize, yStep):
                # fileName = 'Image_<sar>_<0-9+>.tif'
                fileName = f"Image_{sar}_'{count}.tif"
                gdal.Translate(os.path.join(outDir, sar, fileName),
                               image,
                               srcWin=[x, y, xStep, yStep],
                               format="GTiff")


def clip_mask_to_sar(outDir) -> None:
    for sar in os.listdir(outDir):
        for tile in sar:
            cutSize = tile
            cutSizeShp = cutSize[:-4]+'.shp'  # change ext
            input = os.path.join(os.getcwd(), sar)
            output = 'Mask_'+tile[5:]
            subprocess.call(f"gdaltindex {cutSizeShp} {cutSize}",
                            shell=True)
            subprocess.call(f"gdalwarp -cutline {cutSizeShp} -crop_to_cutline \
                            {input} {output}",
                            shell=True)
            # delete junk
            for f in os.listdir(os.path.join(outDir, sar)):
                if ('.shp') in f:
                    os.remove(os.path.join(outDir, sar, f))
                if ('.shx') in f:
                    os.remove(os.path.join(outDir, sar, f))
                if ('.prj') in f:
                    os.remove(os.path.join(outDir, sar, f))
                if ('.dbf') in f:
                    os.remove(os.path.join(outDir, sar, f))


def trim_masks(outDir, mxmTileSize) -> None:
    for sar in os.listdir(outDir):
        for f in os.listdir(outDir):
            if f == sar+'Image.tif':
                pass
            elif f == sar+'Mask.tif':
                pass
            elif f.endswith('.py'):
                pass
            else:
                resizedImage = 'RS'+f
                subprocess.call(f"gdal_translate -outsize {mxmTileSize} \
                                {mxmTileSize} {f} {resizedImage}",
                                shell=True)
                os.remove(os.path.join(outDir, f))
                os.rename(resizedImage, resizedImage[2:])  # remove 'RS'


def reclassify_mask(outDir) -> None:
    for sar in os.listdir(outDir):
        for f in os.listdir(outDir):
            if 'Mask' in f:
                python = 'python'
                windowsMode, linuxMode = determine_OS()
                if LinuxMode:
                    python = 'python3'
                subprocess.call(f"{python} gdal_reclassify.py {f}  Binary_{f} \
                                -c \"<=45, <=100\" -r \"0, 1\" -d 0 -n true -p \
                                \"COMPRESS=LZW\"",
                                shell=True)
                os.remove(f)
                oldName = os.path.join(outDir, 'Binary_'+f)
                newName = os.path.join(outDir, f)
                os.rename(oldName, newName)


def clean_up(outDir) -> None:
    for sar in os.listdir(outDir):
        os.remove(os.path.join(outDir, sar, 'gdal_reclassify.py'))


def copy_vv_vh_to_inputs(outDir, dataDict) -> None:
    inputsPath = os.path.join(os.getcwd(), 'inputs')
    for sar, vvvhband in dataDict.items():
        shutil.copy(os.path.join(inputsPath, vvvhband[0]),
                    os.path.join(os.getcwd(), outDir, sar))
        shutil.copy(os.path.join(inputsPath, vvvhband[1]),
                    os.path.join(os.getcwd(), outDir, sar))


def make_masks(outDir, dataDict) -> None:
    count = 1
    for sar, vvvhband in dataDict.items():
        inputPath = os.path.join(os.getcwd(), 'inputs')
        renamePath = os.path.join(os.getcwd(), outDir, sar)
        print(f"{count}")
        idw_main(os.path.join(inputPath, vvvhband[0]),
                 os.path.join(inputPath, vvvhband[1]))
        count += 1
        # rename 'mask-0.tif' -> 'Mask_<sar>.tif'
        os.rename('mask-0.tif',
                  os.path.join(renamePath, 'Mask_'+sar+'.tif'))


def tile(outDir, tifName, sar, mxmTileSize, isMask) -> None:
    label = 'temp'
    if isMask:
        label = ''
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
            gdal.Translate(os.path.join(outDir, sar, fileName),
                           tif,
                           srcWin=[x, y, xStep, yStep],
                           format="GTiff")
            count += 1


def tile_vv_vh_mask(outDir, mxmTileSize) -> None:
    for sar in os.listdir(os.path.join(outDir)):
        for tifName in os.listdir(os.path.join(outDir, sar)):
            if tifName.endswith('VV.tif'):
                tile(outDir, tifName, sar, mxmTileSize, False)
            elif tifName.endswith('VH.tif'):
                tile(outDir, tifName, sar, mxmTileSize, False)
            elif tifName.startswith('Mask'):
                tile(outDir, tifName, sar, mxmTileSize, True)


def main():
    # set tile size manually here (comment out parser block below)
    # mxmTileSize = 512

    # cmd line argumnet parser for tile size
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=int, default=512)
    parser.add_argument('-worldMask, type=bool, default=False')
    args = parser.parse_args()
    mxmTileSize = args.s
    worldMask = args.worldMask

    outDir = 'syntheticTriainingData'+date.isoformat(date.today())  # outDir
    data = make_database()

    make_output_dir(outDir, data)
    if worldMask:
        cut_worldMask_to_sar()
        move_sar_mask_to_outDir()
        cut_sar_to_tiles()
        clip_mask_to_sar()
        trim_masks()
        reclassify_mask()
        clean_up()
        sys.exit()
    copy_vv_vh_to_inputs(outDir, data)
    make_masks(outDir, data)
    tile_vv_vh_mask(outDir, mxmTileSize)


if __name__ == '__main__':
    main()
