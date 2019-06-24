import os

images=''
with open('waterMask.txt') as file:
    for line in file:
        images+=line[:-1]+' '
    images=images[:-1]
    
os.system('gdal_merge.py -o worldMask.tif '+images)
