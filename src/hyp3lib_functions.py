"""
 Created By:   Jason Herning
 Date Started: 07-24-2020
 Last Updated: 07-21-2020
 File Name:    hyp3lib_functions.py
 Description:  Various tools used by the project. Most are taken from hyp3-lib.
               All functions here will eventually be refactored and moved elsewhere.
"""

import os
from scipy import ndimage
from osgeo.gdalconst import GA_ReadOnly
from osgeo import gdal, ogr, osr
from typing import Tuple
import numpy as np



def overlap_indices(polygon, boundary, pixelSize):
    polyEnv = polygon.GetEnvelope()
    boundEnv = boundary.GetEnvelope()
    xOff = int((boundEnv[0] - polyEnv[0]) / pixelSize)
    yOff = int((polyEnv[3] - boundEnv[3]) / pixelSize)
    xCount = int((boundEnv[1] - boundEnv[0]) / pixelSize)
    yCount = int((boundEnv[3] - boundEnv[2]) / pixelSize)

    return (xOff, yOff, xCount, yCount)


def geotiff_overlap(firstFile, secondFile, method):
    # Check map projections
    raster = gdal.Open(firstFile)
    proj = raster.GetProjection()
    gt = raster.GetGeoTransform()
    pixelSize = gt[1]
    raster = None

    # Extract boundary polygons
    firstPolygon = geotiff2polygon(firstFile)
    secondPolygon = geotiff2polygon(secondFile)

    if method == 'intersection':
        overlap = firstPolygon.Intersection(secondPolygon)
    elif method == 'union':
        overlap = firstPolygon.Union(secondPolygon)

    return (firstPolygon, secondPolygon, overlap, proj, pixelSize)


def geotiff2polygon(geotiff):
    (polygon, proj) = geotiff2polygon_ext(geotiff)
    return polygon


def geotiff2polygon_ext(geotiff):
    raster = gdal.Open(geotiff)
    proj = osr.SpatialReference()
    proj.ImportFromWkt(raster.GetProjectionRef())
    gt = raster.GetGeoTransform()
    originX = gt[0]
    originY = gt[3]
    pixelWidth = gt[1]
    pixelHeight = gt[5]
    cols = raster.RasterXSize
    rows = raster.RasterYSize
    polygon = ogr.Geometry(ogr.wkbPolygon)
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint_2D(originX, originY)
    ring.AddPoint_2D(originX + cols * pixelWidth, originY)
    ring.AddPoint_2D(originX + cols * pixelWidth, originY + rows * pixelHeight)
    ring.AddPoint_2D(originX, originY + rows * pixelHeight)
    ring.AddPoint_2D(originX, originY)
    polygon.AddGeometry(ring)
    ring = None
    raster = None

    return (polygon, proj)


def data2geotiff(data, geoTrans, proj, dtype, noData, outFile):
    (rows, cols) = data.shape
    gdalDriver = gdal.GetDriverByName('GTiff')
    if dtype == 'BYTE':
        outRaster = gdalDriver.Create(outFile, cols, rows, 1, gdal.GDT_Byte,
                                      ['COMPRESS=DEFLATE'])
    elif dtype == 'FLOAT':
        outRaster = gdalDriver.Create(outFile, cols, rows, 1, gdal.GDT_Float32,
                                      ['COMPRESS=DEFLATE'])
    outRaster.SetGeoTransform(geoTrans)
    outRaster.SetProjection(proj.ExportToWkt())
    outBand = outRaster.GetRasterBand(1)
    outBand.SetNoDataValue(noData)
    outBand.WriteArray(data)
    outRaster = None


def geotiff2data(inGeotiff):
    inRaster = gdal.Open(inGeotiff)
    proj = osr.SpatialReference()
    proj.ImportFromWkt(inRaster.GetProjectionRef())
    if proj.GetAttrValue('AUTHORITY', 0) == 'EPSG':
        epsg = int(proj.GetAttrValue('AUTHORITY', 1))
    geoTrans = inRaster.GetGeoTransform()
    inBand = inRaster.GetRasterBand(1)
    noData = inBand.GetNoDataValue()
    data = inBand.ReadAsArray()
    if data.dtype == np.uint8:
        dtype = 'BYTE'
    elif data.dtype == np.float32:
        dtype = 'FLOAT'
    elif data.dtype == np.float64:
        dtype = 'DOUBLE'

    return (data, geoTrans, proj, epsg, dtype, noData)


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
            # maxx = geoTrans[0] + cols*geoTrans[1]
            # miny = geoTrans[3] + rows*geoTrans[5]

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


# Save data with fields to shapefile
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
    _ = outLayer.GetLayerDefn()
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


def raster_meta(rasterFile):
    raster = gdal.Open(rasterFile)
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromWkt(raster.GetProjectionRef())
    gt = raster.GetGeoTransform()
    shape = [raster.RasterYSize, raster.RasterXSize]
    pixel = raster.GetMetadataItem('AREA_OR_POINT')
    raster = None

    return (spatialRef, gt, shape, pixel)


def reproject2grid(inRaster, tsEPSG, xRes=None):
    # Read basic metadata
    geoTrans = inRaster.GetGeoTransform()
    proj = osr.SpatialReference()
    proj.ImportFromEPSG(tsEPSG)

    # Define warping options
    rasterFormat = 'VRT'
    if xRes is None:
        xRes = geoTrans[1]
    yRes = xRes
    resampleAlg = gdal.GRA_Bilinear
    options = ['COMPRESS=DEFLATE']

    outRaster = gdal.Warp('', inRaster, format=rasterFormat, dstSRS=proj,
                          targetAlignedPixels=True, xRes=xRes, yRes=yRes, resampleAlg=resampleAlg,
                          options=options)
    inRaster = None

    return outRaster


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