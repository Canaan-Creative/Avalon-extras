#!/bin/bash

clearenv () {
    umount root &> /dev/null
    rm -r root &> /dev/null
    exit 0
}

trap clearenv SIGINT

MENU="
1   Write avalon2 config 
2   Write avalon3 config 
3   Update IP 
4   Update raspberrypi firmware 
5   Exit
"

while true; do
    clear
    echo "$MENU"
    echo -n "Please make your choice: "
    read INPUT # Read user input and assign it to variable INPUT

    [ ! -d root ] && mkdir root 
    umount root &> /dev/null
    mount /dev/sdb2 root
    [ $? -ne 0 ] && echo "mount sd card failed!" && rm -r root && exit 1

    case $INPUT in
	1)
	    cp -f config/cgminer.avalon2 root/etc/config/cgminer
	    cp -f config/system root/etc/config/system
	    cp -f config/02-pcgminer root/etc/uci-defaults/
	    [ $? -eq 0 ] && echo "Write avalon2 config success."
	    [ $? -ne 0 ] && echo "Write avalon2 config failed!" 
	    sync
	    umount root && rm -r root
	    read
	    ;;
	2)
	    cp -f config/cgminer.avalon3 root/etc/config/cgminer
	    cp -f config/system root/etc/config/system
	    cp -f config/02-pcgminer root/etc/uci-defaults/
	    [ $? -eq 0 ] && echo "Write avalon3 config success."
	    [ $? -ne 0 ] && echo "Write avalon3 config failed!"
	    sync
	    umount root && rm -r root
	    read
	    ;;
	3)
	    echo -n "Please input ip address: "
	    read IPADDR
	    sed "s/yee0ya7ieV/$IPADDR/g" config/network > root/etc/config/network 
	    [ $? -eq 0 ] && echo "Change ip success."
	    [ $? -ne 0 ] && echo "Change ip failed!"
	    sync
	    umount root && rm -r root
	    read
	    ;;
	4)
	    umount root &> /dev/null && rm -r root
	    umount /dev/sdb1 &> /dev/null
	    umount /dev/sdb2 &> /dev/null
	    dd if=./firmware/openwrt-brcm2708-sdcard-vfat-ext4.img of=/dev/sdb
	    [ $? -eq 0 ] && echo "Update firmware success."
	    [ $? -ne 0 ] && echo "Update firmware failed!"
	    sync
	    read
	    ;;

	5|q|Q) # If user presses 4, q or Q we terminate
	    umount root && rm -r root
	    exit 0
	    ;;
    esac
done
