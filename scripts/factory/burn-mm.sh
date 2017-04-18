#! /bin/bash
cd /home/factory/Avalon-extras/scripts/factory
while true; do
        make isedir=/home/factory/Xilinx/14.6/ISE_DS reflash PLATFORM=$1
echo;
read -p "Press any key to burn next"
done
