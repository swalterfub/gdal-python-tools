#!/bin/python
import argparse
from osgeo import gdal
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('infile',  type=str, help='Input file')
parser.add_argument('outfile', type=str, help='Output file')
args = parser.parse_args()

ds = gdal.Open(args.infile, gdal.GA_ReadOnly)
xoffset, px_w, rot1, yoffset, rot2, px_h = ds.GetGeoTransform()

bd = ds.GetRasterBand(1)
nd = bd.GetNoDataValue()
min,max,mean,stddev = bd.GetStatistics(True, False)
A = bd.ReadAsArray().astype(np.int32)
B = (A==nd)

nl = A.shape[0]
ns = A.shape[1]
#start line = first line with valid pixels
sl = 0
ss = 0
#end line = last line with valid pixels
el = nl
es = ns

sl_found=False
for line in range(0,nl-1):
  if np.all(B[line,:]) and sl_found==False:
    sl = line
  if not np.all(B[line,:]):
    sl_found=True

ss_found=False
for sample in range(0,ns-1):
  if np.all(B[:,sample]) and ss_found==False:
    ss = sample+1
  if not np.all(B[:,sample]):
    ss_found=True

el_found=False
for line in reversed(range(0,nl-1)):
  if np.all(B[line,:]) and el_found==False:
    el = line+1
  if not np.all(B[line,:]):
    el_found=True

es_found=False
for sample in reversed(range(0,ns-1)):
  if np.all(B[:,sample]) and es_found==False:
    es = sample+1
  if not np.all(B[:,sample]):
    es_found=True

C=A[sl:el,ss:es]

drv = gdal.GetDriverByName('GTiff')
ods = drv.Create(args.outfile, C.shape[1], C.shape[0], bands=1, eType=gdal.GDT_Int16, options=['COMPRESS=LZW','BIGTIFF=YES'])
ods.GetRasterBand(1).WriteArray(C)
ods.GetRasterBand(1).SetNoDataValue(nd)
ods.GetRasterBand(1).SetStatistics(min,max,mean,stddev)
ods.SetGeoTransform((xoffset+ss*px_w, px_w, rot1, yoffset+sl*px_h, rot2, px_h))
ods.SetProjection(ds.GetProjection())

ds = None 
ods = None

