#!/bin/sh
# Set FCLK0 to 100Mhz
# ./setfclk.sh 100000000
set -e

c=fclk0
devcfg=$(find /sys/devices -name "*.devcfg" -type d)
echo $c | tee $devcfg/fclk_export > /dev/null

clk=$devcfg/fclk/$c
echo 1 | tee $clk/enable > /dev/null
echo "Rate.Before:" $(cat $clk/set_rate)
echo $1 | tee $clk/set_rate > /dev/null
echo "Rate.After :" $(cat $clk/set_rate)

echo $c | tee $devcfg/fclk_unexport > /dev/null
