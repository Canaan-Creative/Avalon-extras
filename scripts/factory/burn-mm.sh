#!/bin/bash
cd /home/factory/Avalon-extras/scripts/factory
make isedir=/home/factory/Xilinx/14.6/ISE_DS reflash MM_PLATFORM=$1
[ -z "$BAR" ] && BAR="+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n$1 Burn Complete\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo -e $BAR
