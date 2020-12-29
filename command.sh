exp=log
panpath=/share/hrsc-mos/michael/archive/2020-03-31_mc13e/pan
rgbpath=/share/hrsc-mos/michael/archive/2020-03-25_mc13e/rgb
mc=mc13

set -x

mkdir -pv hsv pan

[ -f rgb.vrt ] || gdalbuildvrt -overwrite rgb.vrt ${rgbpath}/tile*.tif 
for i in ${panpath}/tile*.tif; do
  echo $i
  [ -f hsv/`basename $i .tif`-${exp}.tif ] && continue
  [ -f pan/`basename $i .tif`-${exp}.tif ] || python customstretch.py --exp=$exp $i pan/`basename $i .tif`-${exp}.tif
  [ -f pan/`basename $i .tif`-${exp}.tif.ovr ] || gdaladdo -ro -r average --config COMPRESS_OVERVIEW LZW pan/`basename $i .tif`-${exp}.tif 2 4 8 16 32 64
  ll=`gdalinfo $i| grep 'Lower Left'|awk -F'\)' '{print $1}'|awk -F'(' '{print $2}'|awk -F, '{print $1,$2}'`
  ur=`gdalinfo $i| grep 'Upper Right'|awk -F'\)' '{print $1}'|awk -F'(' '{print $2}'|awk -F, '{print $1,$2}'`
  rm -f rgb_current_tile-${exp}.tif
  gdalwarp -tr 12.5 12.5 -te $ll $ur rgb.vrt rgb_current_tile-${exp}.tif
  python hsv-pansharp.py --pan=pan/`basename $i .tif`-${exp}.tif --rgb=rgb_current_tile-${exp}.tif --out=hsv/`basename $i .tif`-${exp}.tif
  gdaladdo -ro -r average --config COMPRESS_OVERVIEW LZW hsv/`basename $i .tif`-${exp}.tif 2 4 8 16 32 64
done
gdalbuildvrt -overwrite ${mc}.vrt hsv/tile*-${exp}.tif
