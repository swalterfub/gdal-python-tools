#!/bin/python
import argparse
from osgeo import gdal
import numpy as np
import os

parser = argparse.ArgumentParser()
parser.add_argument('infile',  type=str, help='Input file')
parser.add_argument('outfile', type=str, help='Output file')
parser.add_argument('--scale', type=int, nargs=4, default=[0, 32767, 1, 255], help='like scale for gdal_translate')
parser.add_argument('--nodata', type=int, default=0, help='new nodata')
parser.add_argument('--exp', type=str, default="1.00", help='exponent for power-law stretch, or log for logarithmic stretch')
args = parser.parse_args()

SrcMin, SrcMax, DstMin, DstMax = args.scale

ds = gdal.Open(args.infile, gdal.GA_ReadOnly)
xoffset, px_w, rot1, yoffset, rot2, px_h = ds.GetGeoTransform()

bd = ds.GetRasterBand(1)
nd = bd.GetNoDataValue()

A = bd.ReadAsArray().astype(np.float32)
A[A==-32768]=np.nan
A=A/18*25
print("min,max,mean,std", np.nanmin(A), np.nanmax(A), np.nanmean(A), np.nanstd(A))
if args.exp=='log':
  B = np.log2( 1 + (A-SrcMin) / (SrcMax-SrcMin)) * (DstMax-DstMin) + DstMin
else:
  B = (DstMax-DstMin) * np.power( (A-SrcMin) / (SrcMax-SrcMin), float(args.exp)) + DstMin
B[A<SrcMin] = DstMin
B[A>SrcMax] = DstMax
B[A==nd] = args.nodata

drv = gdal.GetDriverByName('GTiff')
outfile=args.outfile
ods = drv.Create(outfile, B.shape[1], B.shape[0], bands=1, eType=gdal.GDT_Byte, options=['COMPRESS=LZW','BIGTIFF=YES'])
ods.GetRasterBand(1).WriteArray(B)
ods.GetRasterBand(1).SetNoDataValue(args.nodata)
ods.GetRasterBand(1).ComputeStatistics(True)
ods.SetGeoTransform(ds.GetGeoTransform())
ods.SetProjection(ds.GetProjection())

ods = None
ds = None 


