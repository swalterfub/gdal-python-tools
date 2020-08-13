#!/bin/python
import argparse
from osgeo import gdal
import numpy as np
import os

parser = argparse.ArgumentParser()
parser.add_argument('infile',  type=str, help='Input file')
parser.add_argument('outfile', type=str, help='Output file')
parser.add_argument('--minsize', type=int, default=100, help='Minimum amount of samples for segment')
parser.add_argument('--keepstats', type=bool, default=True, help='Keep statistics of input dataset, otherwise calculates new statistics for every patch')
args = parser.parse_args()

ds = gdal.Open(args.infile, gdal.GA_ReadOnly)
xoffset, px_w, rot1, yoffset, rot2, px_h = ds.GetGeoTransform()

bd = ds.GetRasterBand(1)
nd = bd.GetNoDataValue()

A = bd.ReadAsArray().astype(np.int32)
B = (A==nd)

nl = A.shape[0]
ns = A.shape[1]

#determine start sample and length of segments
n_of_seg=0
currently_in_nd=False
currently_in_seg=False
ss_seg=[]
len_seg=[]
current_ss=0
for sample in range(0,ns-1):
  if np.all(B[:,sample]) and currently_in_nd==False:
    if currently_in_seg==True:
      len_seg.append(sample-current_ss)
    currently_in_nd=True
    currently_in_seg=False
  if not np.all(B[:,sample]) and currently_in_seg==False:
    ss_seg.append(sample)
    current_ss=sample
    n_of_seg+=1
    currently_in_nd=False
    currently_in_seg=True
if currently_in_seg==True:
  len_seg.append(sample-current_ss)

if args.keepstats==True or n_of_seg==1:
  min,max,mean,stddev = bd.GetStatistics(True, False)

print("filename:", args.outfile, "number of segments:", n_of_seg, "ss_seg:", ss_seg, "len_seg:", len_seg)
sl = 0
el = nl

for x in range(0,n_of_seg):
  if len_seg[x]<args.minsize:
    print("skipping segment",x,"as it's too small!")
    continue
  ss = ss_seg[x]
  es = ss_seg[x]+len_seg[x]
  sl_found=False
  for line in range(sl,nl-1):
    if np.all(B[line,ss_seg[x]:es]) and sl_found==False:
      sl = line
    if not np.all(B[line,ss_seg[x]:es]):
      sl_found=True
  el_found=False
  for line in reversed(range(sl,nl-1)):
    if np.all(B[line,ss_seg[x]:es]) and el_found==False:
      el = line+1
    if not np.all(B[line,ss_seg[x]:es]):
      el_found=True

  C=A[sl:el,ss:es]

  drv = gdal.GetDriverByName('GTiff')
  if n_of_seg > 1:
    outfile=os.path.splitext(args.outfile)[0]+'_'+str(x)+'.tif'
  else:
    outfile=args.outfile
  ods = drv.Create(outfile, C.shape[1], C.shape[0], bands=1, eType=gdal.GDT_Int16, options=['COMPRESS=LZW','BIGTIFF=YES'])
  ods.GetRasterBand(1).WriteArray(C)
  ods.GetRasterBand(1).SetNoDataValue(nd)
  if args.keepstats==False:
    ods.GetRasterBand(1).ComputeStatistics(True)
  else:
    ods.GetRasterBand(1).SetStatistics(min,max,mean,stddev)
  ods.SetGeoTransform((xoffset+ss*px_w, px_w, rot1, yoffset+sl*px_h, rot2, px_h))
  ods.SetProjection(ds.GetProjection())
  ods = None

ds = None 


