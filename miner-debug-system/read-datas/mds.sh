#!/bin/bash
#
# Author June 2018 Zhenxing Xu <xuzhenxing@canaan-creative.com>
#

# Get delay times
time=`cat miner-options.conf | grep TIME | awk '{ print $2 }'`

# Get RPI's IP
cat miner-options.conf | awk 'NR > 3' | while read tmp
do
    if [[ -z $tmp ]]; then
	break;
    fi
    ./mdssub.sh $time $tmp &
    sleep 5
done
