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
# - water_mark:
#   - water_mark.py
#   - etl_water_mark.py
#   - download-all-<nums>.py (python script from ASF HyP3)
#   - gdal_reclassify.py
#   - downloadWaterData.pyz
################################################################################

import importlib
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

DOWNLOADS_FPATH = os.path.join(Path.home(), 'Downloads')


def get_SAR_from_HyP3():
    DOWNLOAD_REGEX = re.compile(r'download-all-(.*)\.py')
    for file_name in os.listdir(DOWNLOADS_FPATH):
        m = re.match(DOWNLOAD_REGEX, file_name)
        if not m:
            continue
        date_info = m.groups()
        module_name = f'download-all-{date_info[0]}'
        sys.path.append(DOWNLOADS_FPATH)
        download_module = importlib.import_module(
            module_name
        )

        downloader = download_module.bulk_downloader()
        downloader.download_files()
        downloader.print_summary()

        # Deletes the download-all-....py script
        os.remove(os.path.join(DOWNLOADS_FPATH, file_name))
        break


def make_inputs_dir():
    if not os.path.exists('inputs'):
        os.mkdir('inputs')


def extract_SAR_to_temp_dir():
    h3 = 'HyP3_downloads'
    ZIP_REGEX = re.compile(r'S1A_IW_SLC__(.*)-power-rtc-gamma\.zip')

    if os.path.exists(h3):
        shutil.rmtree(h3)
    os.mkdir(h3)

    for f_name in os.listdir():
        m = re.match(ZIP_REGEX, f_name)
        if not m:
            continue

        zf = zipfile.ZipFile(f_name, 'r')
        zf.extractall(h3)
        zf.close()
        os.remove(f_name)


def extract_VV_VH_to_inputs():
    h3 = 'HyP3_downloads'
    for sar in os.listdir(h3):
        for f_name in os.listdir(os.path.join(h3, sar)):
            input_file = os.path.join(h3, sar, f_name)
            if f_name.endswith('VH.tif') or f_name.endswith('VV.tif'):
                shutil.copy(input_file, 'inputs')


def clean_up():
    # Delete zips
    for f_name in os.listdir():
        if f_name.endswith('.zip'):
            os.remove(f_name)
    # Delete temp dir
    shutil.rmtree('HyP3_downloads')


def main():
    get_SAR_from_HyP3()
    make_inputs_dir()
    extract_SAR_to_temp_dir()
    extract_VV_VH_to_inputs()
    clean_up()


if __name__ == '__main__':
    main()
