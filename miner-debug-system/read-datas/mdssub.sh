#!/bin/bash
#
# Author March 2018 Zhenxing Xu <xuzhenxing@canaan-creative.com>
#

[ -z $1 ] && exit
time=$1

# Create result directory
[ -z $2 ] && exit
[ -z $3 ] && exit
CIP=$2
PIP=$3
dirip="result-"$CIP
mkdir $dirip

# Copy CGMiner configuration file
./scp-login.exp $CIP $dirip 0
if [ $? -ne '0' ]; then
    rm -fr $dirip
    exit
fi
sleep 3

# Create result.csv
echo "Freq,Volt-level,Vcore,GHSmm,Temp,TMax,WU,GHSav,Power,Power/GHSav,DH,DNA" > ./$dirip/miner-result.csv

# Config /etc/config/cgminer and restart cgminer, Get Miner debug logs
cat miner-options.conf | grep avalon |  while read tmp
do
    more_options=`cat ./$dirip/cgminer | grep more_options`
    if [ "$more_options" == "" ]; then
        echo "option more_options" >> ./$dirip/cgminer
    fi

    more_options=`cat ./$dirip/cgminer | grep more_options`
    sed -i "s/$more_options/	option more_options '$tmp'/g" ./$dirip/cgminer

    # Cp cgminer to /etc/config
    ./scp-login.exp $CIP $dirip 1
    sleep 3

    # CGMiner restart
    ./ssh-login.exp $CIP /etc/init.d/cgminer restart
    sleep $time

    # Read AvalonMiner Power
    ./ssh-power.py $PIP | sed '/^$/d' | cut -d \: -f 2 > ./$dirip/CGMiner_Power.log
    for i in `cat ./$dirip/CGMiner_Power.log`
    do
        if [ $i -ge 300 -a $i -le 3000 ]; then
            echo $i >> ./$dirip/CGMiner_Power.log
        fi
    done
    sleep 3

    # Debuglog switch
    dbg=`./ssh-login.exp $CIP cgminer-api debug | grep "\[Debug\] => true" | wc -l`
    if [ $dbg -eq 0 ]; then
        ./ssh-login.exp $CIP cgminer-api "debug\|D" > /dev/null
    fi
    sleep 1

    ./ssh-login.exp $CIP cgminer-api estats ./$dirip/estats.log > /dev/null
    ./ssh-login.exp $CIP cgminer-api edevs ./$dirip/edevs.log > /dev/null
    ./ssh-login.exp $CIP cgminer-api summary ./$dirip/summary.log > /dev/null

    # Read CGMiner Log
    ./debuglog.sh $CIP $tmp
done

more_options_flag=`cat miner-options.conf | grep avalon`
# more options is null
if [ -z "${more_options_flag}" ]; then
    more_options=`cat ./$dirip/cgminer | grep more_options`
    tmp=`echo ${more_options#*more_options} | sed "s/'//g"`

    # Read AvalonMiner Power
    ./ssh-power.py $PIP | sed '/^$/d' | cut -d \: -f 2 > ./$dirip/CGMiner_Power.log
    sleep 3

    # Debuglog switch
    dbg=`./ssh-login.exp $CIP cgminer-api debug | grep "\[Debug\] => true" | wc -l`
    if [ $dbg -eq 0 ]; then
        ./ssh-login.exp $CIP cgminer-api "debug\|D" > /dev/null
    fi
    sleep 1

    ./ssh-login.exp $CIP cgminer-api estats ./$dirip/estats.log > /dev/null
    ./ssh-login.exp $CIP cgminer-api edevs ./$dirip/edevs.log > /dev/null
    ./ssh-login.exp $CIP cgminer-api summary ./$dirip/summary.log > /dev/null

    # Read CGMiner Log
    ./debuglog.sh $CIP $tmp
fi

# Remove cgminer file
rm ./$dirip/cgminer
