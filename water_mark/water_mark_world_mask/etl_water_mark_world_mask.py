###############################################################################
#################      _____ _____ _         ##################################
##################    | ____|_   _| |         #################################
###################   |  _|   | | | |          ################################
####################  | |___  | | | |___        ###############################
##################### |_____| |_| |_____|        ##############################
####################                            ###############################
################### George Meier 16 July 2019  ################################
##################  materMark ETL & worldMask #################################
########################################################################80chars
#
# This program sets up the current directory for water_mark to be run by
# creating an input directory, and filling it with VV and  VH sar tifs
# downloaded from asf HyP3.
#
###############################################################################
#
# Python3
# Windows admin powershell or Linux
# - water_mark_world_mask:
#   - water_mark_world_mask.py
#   - etl_water_mark_world_mask.py
#   - download-all-<nums>.py (python script from asf HyP3)
#   - identify_water.py
#   - downloadWaterData.py
#   - gdal_reclassify.py
#   - inputs: (input directory made automatically)
#
################################################################################

import platform
import os
import shutil
import subprocess
import zipfile
from typing import Tuple, List, Dict


def determine_OS() -> Tuple[bool, bool]:
    if platform.system() == 'Windows':
        return (True, False)
    else:
        return (False, True)


def get_sar_from_HyP3() -> None:
    linuxMode, windowsMode = determine_OS()
    python = 'python'
    if linuxMode:
        python = 'python3'
    scriptToRun = ''
    for fileName in os.listdir():
        if 'download' in fileName:
            scriptToRun = fileName
    subprocess.call(f"{python} {scriptToRun}",  shell=True)


def make_input_dir() -> None:
    inputsPath = os.path.join(os.getcwd(), 'inputs')
    if not os.path.exists(inputsPath):
        os.mkdir(inputsPath)
        shutil.move(os.path.join(os.getcwd(),
                                 'gdal_reclassify.py'), inputsPath)
        shutil.move(os.path.join(os.getcwd(),
                                 'downloadWaterData.py'), inputsPath)


def make_vrt() -> None:
    inputsPath = os.path.join(os.getcwd(), 'inputs')
    worldMaskPath = os.path.join(inputsPath, 'worldMask')
    if os.path.exists(worldMaskPath):
        shutil.rmtree(worldMaskPath)
    os.mkdir(worldMaskPath)
    windowsMode, linuxMode = determine_OS()
    python = 'python'
    if linuxMode:
        python = 'python3'
    scriptPath = os.path.join(inputsPath, 'downloadWaterData.py')
    subprocess.call(f"{python} {scriptPath} -d '{worldMaskPath}' occurrence",
                    shell=True)
    with open(os.path.join(worldMaskPath, 'worldMask.txt'), 'w') as f:
        for ff in os.listdir(worldMaskPath):
            f.write(ff+'\n')
    subprocess.call(f"gdalbuildvrt -input_file_list \
                    {os.path.join(worldMaskPath, 'worldMask.txt')} \
                    {os.path.join(worldMaskPath, 'worldMask.vrt')}",
                    shell=True)
    os.remove(os.path.join(worldMaskPath, 'worldMask.txt'))


def extract_sar_to_temp_dir() -> None:
    h3 = 'HyP3Downloads'
    if os.path.exists(h3):
        shutil.rmtree(h3)
    os.mkdir(h3)
    for f in os.listdir():
        if f.endswith('.zip'):
            zf = zipfile.ZipFile(f, 'r')
            zf.extractall(h3)
            zf.close()


def extract_vv_vh_to_inputs() -> None:
    h3 = 'HyP3Downloads'
    for sar in os.listdir(os.path.join(os.getcwd(), h3)):
        for f in sar:
            if f.endswith('VH.tif'):
                shutil.copy(os.path.join(os.getcwd(), h3, sar,  f),
                            os.path.join(os.getcwd(), 'inputs'))
            if f.endswith('VV.tif'):
                shutil.copy(os.path.join(os.getcwd(), h3, sar,  f),
                            os.path.join(os.getcwd(), 'inputs'))


def clean_up() -> None:
    # Delete zips
    for f in os.listdir():
        if f.endswith('.zip'):
            os.remove(f)
    # Delete temp dir
    shutil.rmtree(os.path.join(os.getcwd(), 'HyP3Downloads'))


def main():
    get_sar_from_HyP3()
    make_input_dir()
    make_vrt()
    extract_sar_to_temp_dir()
    extract_vv_vh_to_inputs()
    clean_up()


if __name__ == '__main__':
    main()
