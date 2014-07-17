#!/bin/bash
# Create a POOLPATH for Openwrt packages and firmware storage
# The POOLPATH will sync with $1 
[ -z "$POOLPATH" ] && POOLPATH=./pool
[ ! -e $POOLPATH ] && echo "Cann't find the folder: $POOLPATH" && exit 1
[ ! -e $1 ] && echo "Cann't find the folder: $1" && exit 1
[ $# -eq 0 ] && echo "Usage: $0 syncsrc" && exit 1

echo -n "Please make sure sync (y/n):"
read INPUT
case $INPUT in
	y)
	echo "Sync start"
	rm -rf $POOLPATH/*
	mkdir $POOLPATH/pi-modelb-v2 $POOLPATH/tl-wr1043nd-v2 $POOLPATH/tl-wr703n-v1
	cp $1/*.log $POOLPATH 
	TARGET=pi-modelb-v2
	cp -r $1/avalon/bin/$TARGET/2*/* $POOLPATH/$TARGET
	echo "Sync $TARGET success!"
	TARGET=tl-wr1043nd-v2
	cp -r $1/avalon/bin/$TARGET/2*/* $POOLPATH/$TARGET
	echo "Sync $TARGET success!"
	TARGET=tl-wr703n-v1
	cp -r $1/avalon/bin/$TARGET/2*/* $POOLPATH/$TARGET
	echo "Sync $TARGET success!"
	echo "Sync end"
	;;
	
	n)
	echo "Sync dropped"
	;;
esac

