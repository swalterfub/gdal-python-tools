# gdal-python-tools

## autocrop.py

usage: python autocrop.py <infile> <outfile> [--minsize <minimum number of samples per patch>] [--keepstats <copy statistics of source file to segments>]

## customstretch.py

usage: python customstretch.py <infile> <outfile> --scale <min> <max> <newmin> <newmax> --nodata <newnodata>

This utility stretches the data and converts it to Byte but sets everything below min to the new min and not to nodata as gdal_translate does.

