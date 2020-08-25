#!/bin/python
import argparse
from osgeo import gdal
import numpy as np
import os

parser = argparse.ArgumentParser()
parser.add_argument('infile',  type=str, help='Input file')
parser.add_argument('outfile', type=str, help='Output file')
parser.add_argument('--scale', type=int, nargs=4, default=[3000, 28000, 1, 255], help='like scale for gdal_translate')
parser.add_argument('--nodata', type=int, default=0, help='new nodata')
args = parser.parse_args()

curmin, curmax, newmin, newmax = args.scale

ds = gdal.Open(args.infile, gdal.GA_ReadOnly)
xoffset, px_w, rot1, yoffset, rot2, px_h = ds.GetGeoTransform()

bd = ds.GetRasterBand(1)
nd = bd.GetNoDataValue()

A = bd.ReadAsArray().astype(np.int32)
B = (A-curmin)*(newmax-newmin)/(curmax-curmin)+newmin
B[A<curmin] = newmin
B[A>curmax] = newmax
B[A==nd] = args.nodata

drv = gdal.GetDriverByName('GTiff')
outfile=args.outfile
ods = drv.Create(outfile, B.shape[1], B.shape[0], bands=1, eType=gdal.GDT_Byte, options=['COMPRESS=LZW','BIGTIFF=YES'])
ods.GetRasterBand(1).WriteArray(B)
ods.GetRasterBand(1).SetNoDataValue(args.nodata)
ods.GetRasterBand(1).ComputeStatistics(True)
#ods.SetGeoTransform((xoffset, px_w, rot1, yoffset, rot2, px_h))
ods.SetGeoTransform(ds.GetGeoTransform())
ods.SetProjection(ds.GetProjection())

ods = None
ds = None 


