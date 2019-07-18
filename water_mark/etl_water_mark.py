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
# downloaded from asf hype.
#
###############################################################################
#
# Python3
# Windows admin powershell or Linux
# - water_mark:
#   - water_mark.py
#   - etl_water_mark.py
#   - download-all-<nums>.py (python script from asf hyp3)
#   - identify_water.py
#   - inputs: (input directory made automatically)
#
################################################################################

import platform
import os
import shutil
import subprocess
import zipfile


def determine_OS():
    if platform.system() == 'Windows':
        return True, False
    else:
        return False, True


def get_SAR_from_HyP3():
    linuxMode, windowsMode = determine_OS()
    scriptToRun = ''
    for fileName in os.listdir():
        if 'download' in fileName:
            scriptToRun = fileName
    if windowsMode:
        subprocess.call('python ' + scriptToRun, shell=True)
    elif linuxMode:
        subprocess.call('python3 ' + scriptToRun, shell=True)
    return


def make_input_dir():
    if not os.path.exists('inputs'):
        os.mkdir('inputs')
    return


def extract_SAR_to_temp_dir():
    if os.path.exists('hyp3Downloads'):
        shutil.rmtree('hyp3Downloads')
    os.mkdir('hyp3Downloads')
    for each in os.listdir():
        if each.endswith('.zip'):
            zf = zipfile.ZipFile(each, 'r')
            zf.extractall('hyp3Downloads')
            zf.close()
    return


def extract_VV_VH_to_inputs():
    for sar in os.listdir(os.path.join(os.getcwd(),'hyp3Downloads'):
        for f in os.listdir(sar):
            if f.endswith('VH.tif'):
                shutil.copy(os.path.join(os.getcwd(),'hyp3Downloads', sar,  f),
                            os.path.join(os.getcwd(),'inputs'))
            if f.endswith('VV.tif'):
                shutil.copy(os.path.join(os.getcwd(),'hyp3Downloads', sar,  f),
                            os.path.join(os.getcwd(),'inputs'))
    return


def clean_up():
    # Delete zips
    for f in os.listdir():
        if f.endswith('.zip'):
            os.remove(f)
    # Delete temp dir
    shutil.rmtree('hyp3Downloads')
    return


def main():
    get_SAR_from_HyP3()
    make_input_dir()
    extract_SAR_to_temp_dir()
    extract_VV_VH_to_inputs()
    clean_up()


if __name__ == '__main__':
    main()
