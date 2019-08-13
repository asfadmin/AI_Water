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
# '-vrt' to make vrt
# - water_mark:
#   - water_mark.py
#   - etl_water_mark.py
#   - download-all-<nums>.py (python script from ASF HyP3)
#   - gdal_reclassify.py
#   - downloadWaterData.pyz
################################################################################

import argparse
import os
import shutil
import zipfile
import sys


def get_SAR_from_HyP3():
    script_to_run = 'temp'
    for file_name in os.listdir():
        if ('download' in file_name) and (not file_name.endswith('.pyz')):
            script_to_run = file_name
    exec(Open(script_to_run).read())


def make_inputs_dir():
    if not os.path.exists('inputs'):
        os.mkdir('inputs')
        if os.path.exists('downloadWaterData.py'):
            shutil.move('downloadWaterData.py', 'inputs')


def make_vrt():
    world_mask_path = os.path.join('inputs', 'worldMask')
    if os.path.exists(world_mask_path):
        shutil.rmtree(world_mask_path)
    os.mkdir(world_mask_path)
    sys.argv = [os.getcwd(), 'occurrence']
    exec(open('download_water_data.pyz').read())
    gdal.BuildVRT(
        os.path.join(world_mask_path, 'worldMask.vrt'),
        [os.path.join(os.getcwd(), 'occurrence', x) for x in os.listdir('occurrence')]
    )


def extract_SAR_to_temp_dir():
    h3 = 'HyP3_downloads'
    if os.path.exists(h3):
        shutil.rmtree(h3)
    os.mkdir(h3)
    for f_name in os.listdir():
        if f_name.endswith('.zip'):
            zf = zipfile.ZipFile(f_name, 'r')
            zf.extractall(h3)
            zf.close()


def extract_VV_VH_to_inputs():
    h3 = 'HyP3_downloads'
    for sar in os.listdir(h3):
        for f_name in os.listdir(os.path.join(h3, sar)):
            input_file = os.path.join(h3, sar,  f_name)
            if f_name.endswith('VH.tif'):
                shutil.copy(input_file, 'inputs')
            if f_name.endswith('VV.tif'):
                shutil.copy(input_file, 'inputs')


def clean_up():
    # Delete zips
    for f_name in os.listdir():
        if f_name.endswith('.zip'):
            os.remove(f_name)
    # Delete temp dir
    shutil.rmtree('HyP3_downloads')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-vrt', action='store_true')
    args = parser.parse_args()
    vrt = args.vrt

    get_SAR_from_HyP3()
    make_inputs_dir()
    if vrt:
        make_vrt()
    extract_SAR_to_temp_dir()
    extract_VV_VH_to_inputs()
    clean_up()


if __name__ == '__main__':
    main()
