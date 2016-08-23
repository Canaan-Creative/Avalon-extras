#!/bin/sh
xadc=$(find /sys/devices -name "*.adc" -type d)/iio\:device0
offset=`cat ${xadc}/in_temp0_offset`
raw=`cat ${xadc}/in_temp0_raw`
scale=`cat ${xadc}/in_temp0_scale`

awk -v offset="${offset}" \
-v raw="${raw}" \
-v scale="${scale}" \
'BEGIN {print "RAW="raw, "OFFSET="offset, "SCALE="scale, "TEMP="(raw + offset) * scale / 1000}'
