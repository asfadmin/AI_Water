###############################################################################
##########  __        __    _            __  __            _   ################
########### \ \      / /_ _| |_ ___ _ __|  \/  | __ _ _ __| | __###############
############ \ \ /\ / / _` | __/ _ \ '__| |\/| |/ _` | '__| |/ / ##############
############# \ V  V / (_| | ||  __/ |  | |  | | (_| | |  |   <   #############
############## \_/\_/ \__,_|\__\___|_|  |_|  |_|\__,_|_|  |_|\_\   ############
############### George Meier 6 July 2019                            ###########
################ ASF Water Detection AI Training Data Generator      ##########
###############################################################################   
# Runs on Linux or Windows
# Run on Linux by default               (run with sudo  python3   )             
# '-w True' when running on Windows     (run with admin powershell)              
# '-s <int>' set square tile pixel size (Default=512              )
# No directory named 'trainingData' can be in the same directory as this file
# Ensure the 'inputs' directory is in the same directory as this file  
# Put 1+ sar images in 'inputs'
# ~0.5  gb/granual data output
# ~1.5 min/granual runtime Linux
# ~5.0 min/granual runtime Windows
###############################################################################
# TODO
#    *batch/queue (cicd continuous integration continuous deployment)
#    
###############################################################################         

import time
import argparse
import os    
import shutil
import subprocess
from osgeo import gdal 

# time program
startTime = time.time()


# cmd line argumnet parcer 
parser=argparse.ArgumentParser()
parser.add_argument('-s', type=int  , default=512)
parser.add_argument('-w', type=bool , default=False)
args=parser.parse_args()
mxmTileSize = args.s # set tile size manually here
linuxMode = True
windowsMode = args.w
if windowsMode==True:
    linuxMode = False


# auto make locations list 
os.chdir('inputs')
locations=[]
for item in os.listdir(os.getcwd()):
    if item.endswith('.tif'):
        locations.append(item[:-4])
        os.rename(item, item[:-4]+'Image.tif') 
os.chdir('..')


# auto cut worldMask to images
os.chdir('inputs')
for item in os.listdir(os.getcwd()):
        if '.tif' in item:
            cutSize     = str(item)
            cutSizeShp  = cutSize[:-4]+'.shp' 
            input       = os.path.join(os.path.join(os.getcwd(), 'worldMask'),\
                                                               'worldMask.vrt')
            output      = item[:-9]+'Mask.tif'
            subprocess.call('gdaltindex '+cutSizeShp+' '+cutSize, shell=True)
            subprocess.call('gdalwarp -cutline '+cutSizeShp+' -crop_to_cutline '\
                                                 +input+' '+output, shell=True)
            # delete junk files
            cleanUp = os.listdir(os.getcwd())
            for item in cleanUp:
                if (".sh") in str(item):
                    os.remove(item)
                if (".pr") in str(item):
                    os.remove(item)
                if (".d") in str(item):
                    os.remove(item)
os.chdir('..')
    

# make trainingData directory (our 'homebase' if you will 
#                              each block of code begins and ends here)
trainingDataPath=os.path.join(os.getcwd(),'trainingData')
if os.path.exists('trainingData'):
    shutil.rmtree('trainingData')
os.mkdir('trainingData')
os.chdir('trainingData')

for location in locations:
    os.mkdir(location)
    
    
#move image and mask into its output directory
os.chdir('..')
os.chdir('inputs')
for location in locations:
    image   = location+"Image.tif" 
    mask    = location+"Mask.tif"
    program = 'gdal_reclassify.py'
    shutil.copy(image,   os.path.join(trainingDataPath, location))
    shutil.copy(mask ,   os.path.join(trainingDataPath, location))
    shutil.copy(program, os.path.join(trainingDataPath, location))
    os.remove(mask)
    os.rename(image, image[:-9]+'.tif')
os.chdir('..')
os.chdir('trainingData')


# make dictorary to store filenames
locationsFiles = {}
for location in locations:
    locationsFiles[location]=[]

    
#cut image into tiles
for location in locations:
    os.chdir(location)
    image           = location+"Image.tif" 
    imageData       = gdal.Open(image)
    xStep, yStep    = mxmTileSize, mxmTileSize
    xSize, ySize    = imageData.RasterXSize, imageData.RasterYSize
    count           = 0
    
    for x in range(0, xSize, xStep):
            for y in range(0, ySize, yStep):
                fileName = 'Image_'+location+'_'+str(count)+'.tif'
                locationsFiles[location].append(fileName)
                gdal.Translate(fileName, image, srcWin=[x, y, xStep, yStep], \
                                                               format="GTiff")
                count+=1
    os.chdir('..')

    
# clip mask to image size 
for location in locations:  
    os.chdir(location)
    for tile in locationsFiles[location]:
        cutSize     = str(tile)
        cutSizeShp  = cutSize[:-4]+'.shp' 
        input       = ''
        # linux windows chooser
        if windowsMode==True : 
            input = os.getcwd()+'\\'+location+'Mask.tif'
        if linuxMode==True :
            input = os.getcwd()+'/'+location+'Mask.tif'
        output      = 'Mask_'+tile[5:]
        
        subprocess.call('gdaltindex '+cutSizeShp+' '+cutSize, shell=True)
        subprocess.call('gdalwarp -cutline '+cutSizeShp+' -crop_to_cutline '+\
                                                input+' '+output, shell=True)
        cleanUp = os.listdir(os.getcwd())
        cleanUp = os.listdir(os.getcwd())
        # delete junk files
        for item in cleanUp:
            if (".sh") in str(item):
                os.remove(item)
            if (".prj") in str(item):
                os.remove(item)
            if (".dbf") in str(item):
                os.remove(item)
    os.chdir('..')
 
    
# Trim masks to mxm pixels 
for location in locations:
    os.chdir(location)
    for image in os.listdir(os.getcwd()):
        if location+'Image.tif' == str(image):
            pass
        elif location+'Mask.tif' == str(image):
            pass
        elif image.endswith('.py'):
            pass
        else:
            resizedImage="RS"+str(image)
            subprocess.call("gdal_translate -outsize "+str(mxmTileSize)+" "+  \
                                 str(mxmTileSize)+" "+str(image)+" "+         \
                                 resizedImage, shell=True)                                            
            os.remove(str(image))
            os.rename(resizedImage, resizedImage[2:])
    os.chdir('..')
    
# Reclassify mask to binary 
for location in locations:
    os.chdir(location)
    for item in os.listdir(os.getcwd()):
        if 'Mask' in item:
            # linux windows chooser
            if linuxMode:
                subprocess.call('python3 gdal_reclassify.py '+item+' Binary_'+\
                            item+' -c "<=45, <=100" -r "0, 1" -d 0 -n true -p \
                                                   "COMPRESS=LZW"', shell=True)
                os.rename('Binary_'+item, item)
            else:
                subprocess.call('python gdal_reclassify.py '+item+' Binary_'+ \
                            item+' -c "<=45, <=100" -r "0, 1" -d 0 -n true -p \
                                                   "COMPRESS=LZW"', shell=True)
                os.remove(item)
                os.rename('Binary_'+item, item)
    os.chdir('..')

# delete junk files
for location in locations:
    os.chdir(location)
    os.remove('gdal_reclassify.py')
    os.chdir('..')
    
# time program
print(str((time.time()-startTime)/60)+'min')
