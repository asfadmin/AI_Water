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
# downloaded from asf HyP3.
#
###############################################################################
#
# Python3
# Windows admin powershell or Linux
# - water_mark:
#   - water_mark.py
#   - etl_water_mark.py
#   - download-all-<nums>.py (python script from asf HyP3)
#   - identify_water.py
#   - inputs: (input directory made automatically)
#
################################################################################

import platform
import os
import shutil
import subprocess
import zipfile
from typing import Tuple


def determine_OS() -> Tuple[bool, bool]:
    if platform.system() == 'Windows':
        return (True, False)
    else:
        return (False, True)


def get_SAR_from_HyP3() -> None:
    linuxMode, windowsMode = determine_OS()
    python = 'python'
    if linuxMode:
        python = 'python3'
    scriptToRun = 'temp'
    for fileName in os.listdir():
        if 'download' in fileName:
            scriptToRun = fileName
    subprocess.call(f"{python} {scriptToRun}",
                    shell=True)


def make_input_dir() -> None:
    if not os.path.exists('inputs'):
        os.mkdir('inputs')


def extract_SAR_to_temp_dir() -> None:
    h3 = os.path.join(os.getcwd(), 'HyP3Downloads')
    if os.path.exists(h3):
        shutil.rmtree(h3)
    os.mkdir(h3)
    for f in os.listdir():
        if f.endswith('.zip'):
            zf = zipfile.ZipFile(f, 'r')
            zf.extractall(h3)
            zf.close()


def extract_VV_VH_to_inputs() -> None:
    h3 = os.path.join(os.getcwd(), 'HyP3Downloads')
    for sar in os.listdir(h3):
        for f in os.listdir(os.path.join(h3, sar)):
            copyInput = os.path.join(h3, sar,  f)
            copyOutput = os.path.join(os.getcwd(), 'inputs')
            if f.endswith('VH.tif'):
                shutil.copy(copyInput, copyOutput)
            if f.endswith('VV.tif'):
                shutil.copy(copyInput, copyOutput)


def clean_up() -> None:
    # Delete zips
    for f in os.listdir():
        if f.endswith('.zip'):
            os.remove(f)
    # Delete temp dir
    shutil.rmtree('HyP3Downloads')


def main():
    get_SAR_from_HyP3()
    make_input_dir()
    extract_SAR_to_temp_dir()
    extract_VV_VH_to_inputs()
    clean_up()


if __name__ == '__main__':
    main()
