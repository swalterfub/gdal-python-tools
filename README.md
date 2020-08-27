# gdal-python-tools

## autocrop.py

usage: python autocrop.py <infile> <outfile> [--minsize <minimum number of samples per patch>] [--keepstats <copy statistics of source file to segments>]

## customstretch.py

usage: python customstretch.py <infile> <outfile> --scale <min> <max> <newmin> <newmax> --nodata <newnodata>

This utility stretches the data and converts it to Byte but sets everything below min to the new min and not to nodata as gdal_translate does.

## hsv-pansharp.py

usage: python hsv-pansharp.py --pan <panchromatic image> --rgb <colour image> --out <pansharpened image>

This tool calculates a high-resolution colour image from a high-resolution panchromatic image (Byte format) and its corresponding lower-resolution colour images (3 bands in Byte format). Dimensions and resolution of the two input images must match.

