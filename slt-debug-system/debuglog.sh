#!/bin/bash
#
# Author Feb 2018 Zhenxing Xu <xzxlnmail@163.com>
#

IP=`cat slt-options.conf | grep "IP" | awk '{ print $2 }'`
DATE=`date +%Y-%m-%d-%H-%M-%S`
dirname=$IP"-"$DATE"-"$2"-"$4
mkdir $dirname

cat estats.log  | grep "\[MM ID" > ./$dirname/CGMiner_Debug.log
cat edevs.log | grep -v Reply  > ./$dirname/CGMiner_Edevs.log
cat summary.log | grep -v Reply  > ./$dirname/CGMiner_Summary.log

rm estats.log edevs.log summary.log
cd ./$dirname

echo "$2" > freq.log
echo "$4" > voltage.log
echo "$@" > options.log

for i in CGMiner_Debug.log
do
    cat $i | sed 's/] /\]\n/g' | grep GHSmm | sed 's/GHSmm\[//g' | sed 's/\]//g' > $i.GHSmm
    cat $i | sed 's/] /\]\n/g' | grep Temp  | sed 's/Temp\[//g'  | sed 's/\]//g' > $i.Temp
    cat $i | sed 's/] /\]\n/g' | grep TMax  | sed 's/TMax\[//g'  | sed 's/\]//g' > $i.TMax
    cat $i | sed 's/] /\]\n/g' | grep WU    | sed 's/WU\[//g'    | sed 's/\]//g' > $i.WU
    cat $i | sed 's/] /\]\n/g' | grep DH    | sed 's/DH\[//g'    | sed 's/\]//g' > $i.DH
    cat $i | sed 's/] /\]\n/g' | grep Power | sed 's/Power\[//g' | sed 's/\]//g' > $i.Power
    cat $i | sed 's/] /\]\n/g' | grep "Iout\["    | sed 's/Iout\[//g'    | sed 's/\]//g' > $i.Iout
    cat $i | sed 's/] /\]\n/g' | grep V0 | awk '{ print $3 }' > $i.V0

    # According to WU value, calculate GHSav.
    # Formula: ghsav = WU / 60 * 2^32 / 10^9
    cat $i.WU | awk '{printf ("%.2f\n", ($1/60*2^32/10^9))}' > $i.GHSav

    # Power / GHSav
    paste $i.GHSav $i.Power | awk '{printf ("%.3f\n", ($2/$1))}' > ph.log

    Result=Results_$dirname

    paste -d, freq.log voltage.log $i.GHSmm $i.Temp $i.TMax $i.WU $i.GHSav $i.DH $i.Iout $i.V0 $i.Power ph.log options.log > ${Result#.log}.csv
    cat *.csv >> ../miner-result.csv
    echo "" >> ../miner-result.csv

    rm -rf $i.GHSmm $i.Temp $i.TMax $i.WU $i.GHSav $i.DH freq.log voltage.log $i.Iout $i.V0 $i.Power ph.log options.log

    cd ..
    mv ./$dirname ./result*
done
