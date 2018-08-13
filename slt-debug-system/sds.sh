#!/bin/bash
#
# Author Feb 2018 Zhenxing Xu <xzxlnmail@163.com>
#

# Create result.csv
echo "Freq,Voltage,GHSmm,Temp,TMax,WU,GHSav,DH,Iout,Vo,Power,Power/GHSav,Options" > miner-result.csv

# Get raspberry IP address
IP=`cat slt-options.conf | grep "IP" | awk '{ print $2 }'`
tmp=`who | cut -f 1 -d: | awk '{ print $1 }'`
name=`echo $tmp | awk '{ print $1 }'`
ssh-keygen -f "/home/$name/.ssh/known_hosts" -R $IP > /dev/null
./scp-login.exp $IP 0 > /dev/null
sleep 3

TIME=`cat slt-options.conf | grep "TIME" | awk '{ print $2 }'`

# Create result directory
dirip="result-"$IP
mkdir $dirip

# Config /etc/config/cgminer and restart cgminer, Get Miner debug logs
cat slt-options.conf | grep avalon |  while read tmp
do
    more_options=`cat cgminer | grep more_options`
    if [ "$more_options" == "" ]; then
        echo "option more_options" >> cgminer
    fi

    more_options=`cat cgminer | grep more_options`
    sed -i "s/$more_options/	option more_options '$tmp'/g" cgminer

    # Cp cgminer to /etc/config
    ./scp-login.exp $IP 1
    sleep 3

    # CGMiner restart
    ./ssh-login.exp $IP /etc/init.d/cgminer restart > /dev/null
    sleep $TIME

    ./ssh-login.exp $IP cgminer-api debug debug.log > /dev/null
    debug=`cat debug.log | grep '\[Debug\] => true' | wc -l`
    if [ $debug -eq 0 ]; then
        # SSH no password
        ./ssh-login.exp $IP cgminer-api "debug\|D" > /dev/null
    fi

    sleep 1
    ./ssh-login.exp $IP cgminer-api estats estats.log > /dev/null
    ./ssh-login.exp $IP cgminer-api edevs edevs.log > /dev/null
    ./ssh-login.exp $IP cgminer-api summary summary.log > /dev/null

    # Read CGMiner Log
    ./debuglog.sh $tmp
done

# Remove cgminer file
rm cgminer
rm debug.log

echo -e "\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m"
echo -e "\033[1;32m++++++++++++++++++++++++++++++  Done   ++++++++++++++++++++++++++++++\033[0m"
echo -e "\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m"
