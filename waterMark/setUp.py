###############################################################################
#################      ____       _     _   _     #############################
##################    / ___|  ___| |_  | | | |_ __ ############################
###################   \___ \ / _ \ __| | | | | '_ \ ###########################
####################   ___) |  __/ |_  | |_| | |_) | ##########################
##################### |____/ \___|\__|  \___/| .__/   #########################
####################                         |_|     ##########################
###################    George Meier 26 June 2019    ###########################
##################     WaterMark set up routine    ############################
###############################################################################  
# Runs Linux or Windows
# '-w True' to run on Windows
# 
#
#
#

import argparse
import os
import subprocess
import shutil

parser=argparse.ArgumentParser()
parser.add_argument('-w', type=bool , default=False)
args=parser.parse_args()
linuxMode   = True
windowsMode = args.w
if windowsMode==True:
    linuxMode = False

shutil.move('downloadWaterData.py', 'inputs')
os.chdir('inputs')

# windows linux toggle
if windowsMode:
    os.mkdir('worldMask')
    subprocess.call("python downloadWaterData.py worldMask occurrence",     \
                                                                  shell=True)
    shutil.move('downloadWaterData.py', 'worldMask')

if linuxMode:
    subprocess.call("python3 downloadWaterData.py worldMask occurrence",     \
                                                                   shell=True)
    shutil.move('downloadWaterData.py', 'worldMask')

os.chdir('worldMask')
with open('worldMask.txt', 'w') as file:
    for item in os.listdir(os.getcwd()):
        if item.endswith('.tif'):
            file.write(item+'\n')    
        else:
            pass            
    subprocess.call('gdalbuildvrt -input_file_list worldMask.txt \
                                        worldMask.vrt', shell=True)

