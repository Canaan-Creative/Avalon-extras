#!/bin/bash
#
# Author June 2018 Zhenxing Xu <xuzhenxing@canaan-creative.com>
#

IP=$1
dirip="result-"$IP
DATE=`date +%Y%m%d%H%M`
dirname=$IP"-"$DATE"-"$3"-"$5
mkdir -p ./$dirip/$dirname

cat ./$dirip/estats.log  | grep "\[MM ID" > ./$dirip/$dirname/CGMiner_Debug.log
cat ./$dirip/edevs.log | grep -v Reply  > ./$dirip/$dirname/CGMiner_Edevs.log
cat ./$dirip/summary.log | grep -v Reply  > ./$dirip/$dirname/CGMiner_Summary.log

rm ./$dirip/estats.log ./$dirip/edevs.log ./$dirip/summary.log
mv ./$dirip/CGMiner_Power.log ./$dirip/$dirname
cd ./$dirip/$dirname

sum=0
cnt=0
avg_int=0
avg_float2=0.00
avg_float3=0.000

# Calc PVT_T average
for i in `cat CGMiner_Debug.log | sed 's/] /\]\n/g' | grep "PVT_V" | sed 's/PVT\_V[0-3]\[//g' | sed 's/\]//g'`
do
    if [ "$i" != "0" ]; then
         let sum=sum+$i
         let cnt=cnt+1
   fi
done
let avg=$sum/$cnt
echo $avg > vcore.log

# Freq and voltage level options
echo "$3" > freq.log
echo "$5" > voltage.log

# Average value function
calc_int_avg() {
    avg_int=0
    s_int=0
    n_int=0

    for l in `cat $1`
    do
        let s_int=s_int+$l
        let n_int=n_int+1
    done

    let avg_int=${s_int}/${n_int}
}

calc_float2_avg() {
    avg_float2=0.00
    s_float2=0.00
    n_float2=0

    for m in `cat $1`
    do
	s_float2=$(echo "scale=2; ${s_float2} + $m" | bc | awk '{printf "%.2f", $0}')
        let n_float2=n_float2+1
    done

    avg_float2=$(echo "scale=2; ${s_float2} / ${n_float2}" | bc | awk '{printf "%.2f", $0}')
}

calc_float3_avg() {
    avg_float3=0.000
    s_float3=0.000
    n_float3=0

    for n in `cat $1`
    do
	s_float3=$(echo "scale=3; ${s_float3} + $n" | bc | awk '{printf "%.3f", $0}')
        let n_float3=n_float3+1
    done

    avg_float3=$(echo "scale=3; ${s_float3} / ${n_float3}" | bc | awk '{printf "%.3f", $0}')
}

for i in CGMiner_Debug.log
do
    cat $i | sed 's/] /\]\n/g' | grep "GHSmm\[" | sed 's/GHSmm\[//g' | sed 's/\]//g' > $i.GHSmm
    cat $i | sed 's/] /\]\n/g' | grep Temp  | sed 's/Temp\[//g'  | sed 's/\]//g' > $i.Temp
    cat $i | sed 's/] /\]\n/g' | grep TMax  | sed 's/TMax\[//g'  | sed 's/\]//g' > $i.TMax
    cat $i | sed 's/] /\]\n/g' | grep WU    | sed 's/WU\[//g'    | sed 's/\]//g' > $i.WU
    cat $i | sed 's/] /\]\n/g' | grep DH    | sed 's/DH\[//g'    | sed 's/\]//g' | sed 's/\%//g' > $i.DH
    cat $i | sed 's/] /\]\n/g' | grep DNA   | sed 's/DNA\[//g'   | sed 's/\]//g' | cut -b 13- > $i.DNA

    # According to WU value, calculate GHSav.
    # Formula: ghsav = WU / 60 * 2^32 /10^9
    cat $i.WU | awk '{printf ("%.2f\n", ($1/60*2^32/10^9))}' > $i.GHSav

    Power=CGMiner_Power.log
    Result=Results_$dirname

    # Power ratio
    paste $i.GHSav $Power | awk '{printf ("%.3f\n", ($2/$1))}' > ph.log

    # GHSmm average
    calc_float2_avg $i.GHSmm
    echo "${avg_float2}" > ghsmm-avg.log

    # Temp average
    calc_int_avg $i.Temp
    echo "${avg_int}" > temp-avg.log

    # TMax average
    calc_int_avg $i.TMax
    echo "${avg_int}" > tmax-avg.log

    # WU average
    calc_float2_avg $i.WU
    echo "${avg_float2}" > wu-avg.log

    # GHSav average
    calc_float2_avg $i.GHSav
    echo "${avg_float2}" > ghsav-avg.log

    # Power average
    calc_int_avg $Power
    echo "${avg_int}" > power-avg.log

    # Power/GHSav average
    calc_float3_avg ph.log
    echo "${avg_float3}" > ph-avg.log

    # DH average
    calc_float3_avg $i.DH
    echo "${avg_float3}" > dh-avg.log

    paste -d, freq.log voltage.log vcore.log $i.GHSmm $i.Temp $i.TMax $i.WU $i.GHSav $Power ph.log $i.DH $i.DNA >> ${Result#.log}.csv
    paste -d, freq.log voltage.log vcore.log ghsmm-avg.log temp-avg.log tmax-avg.log wu-avg.log ghsav-avg.log power-avg.log ph-avg.log dh-avg.log >> ${Result#.log}.csv
    echo "" >> ${Result#.log}.csv
    cat *.csv >> ../miner-result.csv

    rm -rf $i.GHSmm $i.Temp $i.TMax $i.WU $i.GHSav $i.DH $i.DNA ph.log freq.log voltage.log vcore.log
    rm -f ghsmm-avg.log temp-avg.log tmax-avg.log wu-avg.log ghsav-avg.log power-avg.log ph-avg.log dh-avg.log
done
