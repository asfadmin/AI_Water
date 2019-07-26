###############################################################################
#################      _____ _____ _         ##################################
##################    | ____|_   _| |         #################################
###################   |  _|   | | | |          ################################
####################  | |___  | | | |___        ###############################
##################### |_____| |_| |_____|        ##############################
####################                            ###############################
################### George Meier 16 July 2019  ################################
##################  mater_mark ETL routine    #################################
########################################################################80chars
#
# This program sets up the current directory for water_mark to be run by
# creating an input directory, and filling it with VV and  VH sar tifs
# downloaded from ASF HyP3.
#
###############################################################################
# Python3
# Windows admin powershell or Linux
# '-vrt' or main(vrt=True) to make vrt
# - water_mark:
#   - inputs: (input directory made automatically)
#   - water_mark.py
#   - etl_water_mark.py
#   - download-all-<nums>.py (python script from asf HyP3)
#   - gdal_reclassify.py   (needed for vrt)
#   - downloadWaterData.py (needed for vrt)
################################################################################

import argparse
import platform
import os
import shutil
import subprocess
import zipfile
from typing import Tuple


def detect_windows_OS() -> bool:
    if platform.system() == 'Windows':
        return True
    else:
        return False


def get_SAR_from_HyP3():
    windowsMode = detect_windows_OS()
    python = 'python'
    if not windowsMode:
        python = 'python3'
    scriptToRun = 'temp'
    for fileName in os.listdir():
        if 'download' in fileName:
            scriptToRun = fileName
    subprocess.call(f"{python} {scriptToRun}",
                    shell=True)


def make_inputs_dir():
    if not os.path.exists('inputs'):
        os.mkdir('inputs')
        if os.path.exists('gdal_reclassify.py'):
            shutil.move('gdal_reclassify.py', 'inputs')
        if os.path.exists('downloadWaterData.py'):
            shutil.move('downloadWaterData.py', 'inputs')


def make_vrt():
    worldMaskPath = os.path.join('inputs', 'worldMask')
    if os.path.exists(worldMaskPath):
        shutil.rmtree(worldMaskPath)
    os.mkdir(worldMaskPath)
    windowsMode = detect_windows_OS()
    python = 'python'
    if not windowsMode:
        python = 'python3'
    scriptPath = os.path.join('inputs', 'downloadWaterData.py')
    subprocess.call(f"{python} {scriptPath} -d '{worldMaskPath}' occurrence",
                    shell=True)
    with open(os.path.join(worldMaskPath, 'worldMask.txt'), 'w') as f:
        for ff in os.listdir(worldMaskPath):
            f.write(ff+'\n')
    subprocess.call(
        f"gdalbuildvrt -input_file_list \
        {os.path.join(worldMaskPath, 'worldMask.txt')} \
        {os.path.join(worldMaskPath, 'worldMask.vrt')}",
        shell=True
    )
    os.remove(os.path.join(worldMaskPath, 'worldMask.txt'))


def extract_SAR_to_temp_dir():
    h3 = 'HyP3Downloads'
    if os.path.exists(h3):
        shutil.rmtree(h3)
    os.mkdir(h3)
    for f in os.listdir():
        if f.endswith('.zip'):
            zf = zipfile.ZipFile(f, 'r')
            zf.extractall(h3)
            zf.close()


def extract_VV_VH_to_inputs():
    h3 = 'HyP3Downloads'
    for sar in os.listdir(h3):
        for f in os.listdir(os.path.join(h3, sar)):
            copyInput = os.path.join(h3, sar,  f)
            if f.endswith('VH.tif'):
                shutil.copy(copyInput, 'inputs')
            if f.endswith('VV.tif'):
                shutil.copy(copyInput, 'inputs')


def clean_up():
    # Delete zips
    for f in os.listdir():
        if f.endswith('.zip'):
            os.remove(f)
    # Delete temp dir
    shutil.rmtree('HyP3Downloads')


def main(**flag):  # main(vrt=True)
    vrt = None
    if not flag:
        parser = argparse.ArgumentParser()
        parser.add_argument('-vrt', action='store_true')
        args = parser.parse_args()
        vrt = args.vrt
    else:
        vrt = flag.get('vrt')

    get_SAR_from_HyP3()
    make_inputs_dir()
    if vrt:
        make_vrt()
    extract_SAR_to_temp_dir()
    extract_VV_VH_to_inputs()
    clean_up()


if __name__ == '__main__':
    main()
