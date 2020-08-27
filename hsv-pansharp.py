#!/bin/python
import argparse
from osgeo import gdal
import numpy as np
import os
import cv2 as cv
import logging as log
log.basicConfig(level=log.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('--rgb',  type=str, help='RGB file')
parser.add_argument('--pan',  type=str, help='Panchromatic file')
parser.add_argument('--out', type=str, help='Output file')
args = parser.parse_args()

ds = gdal.Open(args.rgb, gdal.GA_ReadOnly)
log.debug('read rgb')
rgb = ds.ReadAsArray()
log.debug(rgb.shape)
log.debug('convert to uint8')
red,green,blue = rgb.astype(np.uint8)
rgb=None
log.debug('convert to bgr')
bgr = np.dstack([blue,green,red])
log.debug(bgr.shape)
red=None
green=None
blue=None
log.debug('call cv.COLOR_BGR2HSV')
hsv = cv.cvtColor(bgr, cv.COLOR_BGR2HSV)
log.debug(hsv.shape)
bgr=None

pds = gdal.Open(args.pan)
log.debug('read pan')
pan = pds.ReadAsArray()
log.debug('substitute v')
hsv[:,:,2] = pan
pan=None

log.debug('call cv.COLOR_HSV2RGB')
sharp = cv.cvtColor(hsv, cv.COLOR_HSV2RGB)
hsv=None
log.debug(sharp.shape)

log.debug('save result')
drv = gdal.GetDriverByName('GTiff')
outfile=args.out
ods = drv.Create(outfile, sharp.shape[1], sharp.shape[0], bands=3, eType=gdal.GDT_Byte, options=['COMPRESS=LZW','BIGTIFF=YES'])
#ods.GetRasterBand(1).WriteArray(hsv[:,:,0])
#ods.GetRasterBand(2).WriteArray(hsv[:,:,1])
#ods.GetRasterBand(3).WriteArray(hsv[:,:,2])
log.debug('1')
ods.GetRasterBand(1).WriteArray(sharp[:,:,0])
log.debug('2')
ods.GetRasterBand(2).WriteArray(sharp[:,:,1])
log.debug('3')
ods.GetRasterBand(3).WriteArray(sharp[:,:,2])
#ods.GetRasterBand(1).WriteArray(sharp[0:,:])
#ods.GetRasterBand(2).WriteArray(sharp[1:,:])
#ods.GetRasterBand(3).WriteArray(sharp[2:,:])
#ods.GetRasterBand(1).ComputeStatistics(True)
#ods.GetRasterBand(1).SetStatistics(min,max,mean,stddev)
ods.SetGeoTransform(ds.GetGeoTransform())
ods.SetProjection(ds.GetProjection())

ods = None
pds = None
ds = None 


