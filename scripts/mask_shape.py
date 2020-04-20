#!/usr/bin/python
import argparse
import os
import sys
from argparse import RawTextHelpFormatter
import numpy as np

# from src.asf_geometry import data_geometry2shape

from osgeo import ogr, gdal, osr
from scipy import ndimage



def cut_blackfill(data, geoTrans):
    originX = geoTrans[0]
    originY = geoTrans[3]
    pixelSize = geoTrans[1]
    colProfile = list(data.max(axis=1))
    rows = colProfile.count(1)
    rowFirst = colProfile.index(1)
    rowProfile = list(data.max(axis=0))
    cols = rowProfile.count(1)
    colFirst = rowProfile.index(1)
    originX += colFirst * pixelSize
    originY -= rowFirst * pixelSize
    data = data[rowFirst:rows + rowFirst, colFirst:cols + colFirst]
    geoTrans = (originX, pixelSize, 0, originY, 0, -pixelSize)

    return (data, colFirst, rowFirst, geoTrans)


# Save data with fields to shapefile

def reproject2grid(inRaster, tsEPSG):
    # Read basic metadata
    cols = inRaster.RasterXSize
    rows = inRaster.RasterYSize
    geoTrans = inRaster.GetGeoTransform()
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(tsEPSG)

    # Define warping options
    rasterFormat = 'VRT'
    xRes = geoTrans[1]
    yRes = xRes
    resampleAlg = gdal.GRA_Bilinear
    options = ['COMPRESS=DEFLATE']

    outRaster = gdal.Warp('', inRaster, format=rasterFormat, dstSRS=proj,
                          targetAlignedPixels=True, xRes=xRes, yRes=yRes, resampleAlg=resampleAlg,
                          options=options)
    inRaster = None

    return outRaster


def data_geometry2shape_ext(data, fields, values, spatialRef, geoTrans,
                            classes, threshold, background, shapeFile):
    # Check input
    if threshold is not None:
        threshold = float(threshold)
    if background is not None:
        background = int(background)

    # Buffer data
    (rows, cols) = data.shape
    pixelSize = geoTrans[1]
    originX = geoTrans[0] - 10 * pixelSize
    originY = geoTrans[3] + 10 * pixelSize
    geoTrans = (originX, pixelSize, 0, originY, 0, -pixelSize)
    mask = np.zeros((rows + 20, cols + 20), dtype=np.float32)
    mask[10:rows + 10, 10:cols + 10] = data
    data = mask

    # Save in memory
    (rows, cols) = data.shape
    maxArea = rows * cols * pixelSize * pixelSize
    data = data.astype(np.byte)
    gdalDriver = gdal.GetDriverByName('Mem')
    outRaster = gdalDriver.Create('value', cols, rows, 1, gdal.GDT_Byte)
    outRaster.SetGeoTransform(geoTrans)
    outRaster.SetProjection(spatialRef.ExportToWkt())
    outBand = outRaster.GetRasterBand(1)
    outBand.WriteArray(data)

    # Write data to shapefile
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(shapeFile):
        driver.DeleteDataSource(shapeFile)
    outShape = driver.CreateDataSource(shapeFile)
    outLayer = outShape.CreateLayer('polygon', srs=spatialRef)
    outField = ogr.FieldDefn('value', ogr.OFTInteger)
    outLayer.CreateField(outField)
    gdal.Polygonize(outBand, None, outLayer, 0, [], callback=None)
    for field in fields:
        fieldDefinition = ogr.FieldDefn(field['name'], field['type'])
        if field['type'] == ogr.OFTString:
            fieldDefinition.SetWidth(field['width'])
        outLayer.CreateField(fieldDefinition)
    fieldDefinition = ogr.FieldDefn('area', ogr.OFTReal)
    fieldDefinition.SetWidth(16)
    fieldDefinition.SetPrecision(3)
    outLayer.CreateField(fieldDefinition)
    fieldDefinition = ogr.FieldDefn('centroid', ogr.OFTString)
    fieldDefinition.SetWidth(50)
    outLayer.CreateField(fieldDefinition)
    if classes:
        fieldDefinition = ogr.FieldDefn('size', ogr.OFTString)
        fieldDefinition.SetWidth(25)
        outLayer.CreateField(fieldDefinition)
    featureDefinition = outLayer.GetLayerDefn()
    for outFeature in outLayer:
        for value in values:
            for field in fields:
                name = field['name']
                outFeature.SetField(name, value[name])
        cValue = outFeature.GetField('value')
        fill = False
        if cValue == 0:
            fill = True
        if background is not None and cValue == background:
            fill = True
        geometry = outFeature.GetGeometryRef()
        area = float(geometry.GetArea())
        outFeature.SetField('area', area)
        if classes:
            for ii in range(len(classes)):
                if area > classes[ii]['minimum'] and area < classes[ii]['maximum']:
                    outFeature.SetField('size', classes[ii]['class'])
        centroid = geometry.Centroid().ExportToWkt()
        outFeature.SetField('centroid', centroid)
        if fill == False and area > threshold:
            outLayer.SetFeature(outFeature)
        else:
            outLayer.DeleteFeature(outFeature.GetFID())
    outShape.Destroy()


def data_geometry2shape(data, fields, values, spatialRef, geoTrans, shapeFile):
    return data_geometry2shape_ext(data, fields, values, spatialRef, geoTrans,
                                   None, 0, None, shapeFile)


def geotiff2boundary_mask(inGeotiff, tsEPSG, threshold, use_closing=True):
    inRaster = gdal.Open(inGeotiff)
    proj = osr.SpatialReference()
    proj.ImportFromWkt(inRaster.GetProjectionRef())
    if proj.GetAttrValue('AUTHORITY', 0) == 'EPSG':
        epsg = int(proj.GetAttrValue('AUTHORITY', 1))

    if tsEPSG != 0 and epsg != tsEPSG:
        print('Reprojecting ...')
        inRaster = reproject2grid(inRaster, tsEPSG)
        proj.ImportFromWkt(inRaster.GetProjectionRef())
        if proj.GetAttrValue('AUTHORITY', 0) == 'EPSG':
            epsg = int(proj.GetAttrValue('AUTHORITY', 1))

    geoTrans = inRaster.GetGeoTransform()
    inBand = inRaster.GetRasterBand(1)
    noDataValue = inBand.GetNoDataValue()
    data = inBand.ReadAsArray()
    minValue = np.min(data)

    ### Check for black fill
    if minValue > 0:
        data /= data
        colFirst = 0
        rowFirst = 0
    else:
        data[np.isnan(data) == True] = noDataValue
        if threshold is not None:
            print('Applying threshold ({0}) ...'.format(threshold))
            data[data < np.float(threshold)] = noDataValue
        if noDataValue == np.nan or noDataValue == -np.nan:
            data[np.isnan(data) == False] = 1
        else:
            data[data > noDataValue] = 1
        if use_closing:
            data = ndimage.binary_closing(data, iterations=10,
                                          structure=np.ones((3, 3))).astype(data.dtype)
        inRaster = None

        (data, colFirst, rowFirst, geoTrans) = cut_blackfill(data, geoTrans)

    return (data, colFirst, rowFirst, geoTrans, proj)


def raster_meta(rasterFile):
    raster = gdal.Open(rasterFile)
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromWkt(raster.GetProjectionRef())
    gt = raster.GetGeoTransform()
    shape = [raster.RasterYSize, raster.RasterXSize]
    pixel = raster.GetMetadataItem('AREA_OR_POINT')
    raster = None

    return (spatialRef, gt, shape, pixel)


# from asf_time_series import raster_metadata

def raster_metadata(input):
    # Set up shapefile attributes
    fields = []
    field = {}
    values = []
    field['name'] = 'granule'
    field['type'] = ogr.OFTString
    field['width'] = 254
    fields.append(field)
    field = {}
    field['name'] = 'epsg'
    field['type'] = ogr.OFTInteger
    fields.append(field)
    field = {}
    field['name'] = 'originX'
    field['type'] = ogr.OFTReal
    fields.append(field)
    field = {}
    field['name'] = 'originY'
    field['type'] = ogr.OFTReal
    fields.append(field)
    field = {}
    field['name'] = 'pixSize'
    field['type'] = ogr.OFTReal
    fields.append(field)
    field = {}
    field['name'] = 'cols'
    field['type'] = ogr.OFTInteger
    fields.append(field)
    field = {}
    field['name'] = 'rows'
    field['type'] = ogr.OFTInteger
    fields.append(field)
    field = {}
    field['name'] = 'pixel'
    field['type'] = ogr.OFTString
    field['width'] = 8
    fields.append(field)

    # Extract other raster image metadata
    (outSpatialRef, outGt, outShape, outPixel) = raster_meta(input)
    if outSpatialRef.GetAttrValue('AUTHORITY', 0) == 'EPSG':
        epsg = int(outSpatialRef.GetAttrValue('AUTHORITY', 1))

    # Add granule name and geometry
    base = os.path.basename(input)
    granule = os.path.splitext(base)[0]
    value = {}
    value['granule'] = granule
    value['epsg'] = epsg
    value['originX'] = outGt[0]
    value['originY'] = outGt[3]
    value['pixSize'] = outGt[1]
    value['cols'] = outShape[1]
    value['rows'] = outShape[0]
    value['pixel'] = outPixel
    values.append(value)

    return (fields, values, outSpatialRef)


def raster_boundary2shape(inFile, threshold, outShapeFile, use_closing=True, fill_holes=False,
                          pixel_shift=False):
    # Extract raster image metadata
    print('Extracting raster information ...')
    (fields, values, spatialRef) = raster_metadata(inFile)

    print("Initial origin {x},{y}".format(x=values[0]['originX'], y=values[0]['originY']))

    if spatialRef.GetAttrValue('AUTHORITY', 0) == 'EPSG':
        epsg = int(spatialRef.GetAttrValue('AUTHORITY', 1))
    # Generate GeoTIFF boundary geometry
    print('Extracting boundary geometry ...')
    (data, colFirst, rowFirst, geoTrans, proj) = \
        geotiff2boundary_mask(inFile, epsg, threshold, use_closing=use_closing)
    (rows, cols) = data.shape

    print("After geotiff2boundary_mask origin {x},{y}".format(x=geoTrans[0], y=geoTrans[3]))

    if fill_holes:
        data = ndimage.binary_fill_holes(data).astype(bool)

        #    if pixel_shift:
        if values[0]['pixel']:
            minx = geoTrans[0]
            maxy = geoTrans[3]
            maxx = geoTrans[0] + cols * geoTrans[1]
            miny = geoTrans[3] + rows * geoTrans[5]

            # compute the pixel-aligned bounding box (larger than the feature's bbox)
            left = minx - (geoTrans[1] / 2)
            top = maxy - (geoTrans[5] / 2)

            values[0]['originX'] = left
            values[0]['originY'] = top

    print("After pixel_shift origin {x},{y}".format(x=values[0]['originX'], y=values[0]['originY']))

    values[0]['rows'] = rows
    values[0]['cols'] = cols

    # Write broundary to shapefile
    print('Writing boundary to shapefile ...')
    data_geometry2shape(data, fields, values, spatialRef, geoTrans, outShapeFile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="mask_shape",
                                     description='generates boundary shapefile from GeoTIFF file',
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('input', metavar='<geotiff file>',
                        help='name of the GeoTIFF file')
    parser.add_argument('-threshold', metavar='<code>', action='store',
                        default=None, help='threshold value what is considered blackfill')
    parser.add_argument('shape', metavar='<shape file>', help='name of the shapefile')

    parser.add_argument('--fill_holes', default=False, action="store_true", help='Turn on hole filling')

    parser.add_argument('--pixel_shift', default=False,
                        action="store_true", help='apply pixel shift')

    parser.add_argument('--no_closing',
                        default=True, action='store_false',
                        help='Switch to turn off closing operation')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print('GeoTIFF file (%s) does not exist!' % args.input)
        sys.exit(1)

    raster_boundary2shape(args.input, args.threshold, args.shape, args.no_closing,
                          args.fill_holes, args.pixel_shift)
