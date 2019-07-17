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
from identify_water import main
from datetime import date

# cmd line argumnet parcer 
parser=argparse.ArgumentParser()
parser.add_argument('-s', type=int  , default=512)
args=parser.parse_args()
mxmTileSize = args.s # set tile size manually here

# Make data set
path=os.getcwd()
inputsPath='/home/gtmeier/Desktop/waterMark/inputs/'

path=os.getcwd()
dataList=[]
for f in os.listdir(os.path.join(path, 'inputs')):
    if f.endswith('.tif'):
        dataList.append(f)
dataList.sort()

data={}

for info in range(0,40,2):
    name    = dataList[info]
    name    = name[:-7]
    vv      = dataList[info+1]
    vh      = dataList[info] 
    
    data[name]=[vv,vh]

# Set up dir
synData = 'syntheticTriainingData'+date.isoformat(date.today())
os.mkdir(synData)
for sar in data:
    os.mkdir(os.path.join(path, synData, sar))

# copy files
for sar, vvvhband in data.items():
    shutil.copy(os.path.join(inputsPath,vvvhband[0]), os.path.join(path, synData, sar))
    shutil.copy(os.path.join(inputsPath,vvvhband[1]), os.path.join(path, synData, sar))
        
        
# make masks
for sar, vvvhband in data.items():
    os.chdir(os.path.join(path, synData, sar))
    main(os.path.join(inputsPath, vvvhband[0]), os.path.join(inputsPath, vvvhband[1]))
    os.rename('mask-0.tif', sar+'_Mask.tif')

os.chdir(path)

# Tile vv vh mask
for sar in os.listdir(os.path.join(path,synData)):
    os.chdir(os.path.join(path,synData,sar))
    for img in os.listdir(os.path.join(path,synData,sar)):
        imageVV = ''
        imageVH = ''
        mask = ''
        if img.endswith('VV.tif'):
            imageVV = img    
            imageVVData = gdal.Open(os.path.join(path,synData,sar,imageVV))
            xStep, yStep    = mxmTileSize, mxmTileSize
            xSize, ySize    = imageVVData.RasterXSize, imageVVData.RasterYSize
            count           = 0
            for x in range(0, xSize, xStep):
                for y in range(0, ySize, yStep):
                    fileName = 'Image_'+img[:-4]+'_'+str(count)+'.tif'                    
                    gdal.Translate(fileName, imageVV, srcWin=[x, y, xStep, yStep], format="GTiff")
                    count+=1
        elif img.endswith('VH.tif'):
            imageVH = img   
            imageVHData = gdal.Open(os.path.join(path,synData,sar,imageVH))
            xStep, yStep    = mxmTileSize, mxmTileSize
            xSize, ySize    = imageVHData.RasterXSize, imageVHData.RasterYSize
            count           = 0
            for x in range(0, xSize, xStep):
                for y in range(0, ySize, yStep):
                    fileName = 'Image_'+img[:-4]+'_'+str(count)+'.tif'                    
                    gdal.Translate(fileName, imageVH, srcWin=[x, y, xStep, yStep], format="GTiff")
                    count+=1
        elif img.endswith('Mask.tif'):
            mask = img
            maskData    = gdal.Open(os.path.join(path,synData,sar,mask))     
            xStep, yStep    = mxmTileSize, mxmTileSize
            xSize, ySize    = maskData.RasterXSize, maskData.RasterYSize
            count           = 0
            for x in range(0, xSize, xStep):
                for y in range(0, ySize, yStep):
                    fileName = 'Mask_'+img[:-4]+'_'+str(count)+'.tif'                    
                    gdal.Translate(fileName, mask, srcWin=[x, y, xStep, yStep], format="GTiff")
                    count+=1
os.chdir(path)
        
        

















