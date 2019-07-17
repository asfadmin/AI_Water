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

import argparse
import platform
import os
import shutil
import subprocess
import zipfile

path = os.getcwd()

# choose windows or linux
linuxMode   = True
windowsMode = False 

if platform.system()=='Windows':
    windowsMode = True
    linuxMode   = False    

# Download SAR from hyp3
scriptToRun = ''
for fileName in os.listdir():
    if 'download' in fileName:
        scriptToRun = fileName

if windowsMode:
    subprocess.call('python ' + scriptToRun, shell=True)
elif linuxMode:
    subprocess.call('python3 '+ scriptToRun, shell=True)

# Make input dir
if not os.path.exists('inputs'):
    os.mkdir('inputs') 

# Extract VV VH to inputs
if os.path.exists('hyp3Downloads'):
    shutil.rmtree('hyp3Downloads')
os.mkdir('hyp3Downloads')
for each in os.listdir():
    if each.endswith('.zip'):
        zf = zipfile.ZipFile(each ,'r')
        zf.extractall('hyp3Downloads')
        zf.close()
        
# Extract VV VH to inputs  
os.chdir('hyp3Downloads')
for f in os.listdir():
    os.chdir(f)
    for each in os.listdir():
        if each.endswith('VH.tif'):
            shutil.copy(each, inputs)
        if each.endswith('VV.tif'):
            shutil.copy(each, inputs)
    os.chdir('..')
os.chdir('..')

# Delete zips        
for each in os.listdir():
    if each.endswith('.zip'):
        os.remove(each)
        
# Delete dir
shutil.rmtree('hyp3Downloads')






