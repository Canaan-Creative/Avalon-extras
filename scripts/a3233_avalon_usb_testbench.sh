#!/bin/sh 
for i in `seq 1 100` 
do
    echo "test $i"
    sleep 0.1
    ./a3233_avalon_usb_test.py
    echo "==========================="
done
