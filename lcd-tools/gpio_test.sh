#!/bin/bash
SCL_PORT=27
SDA_PORT=17

clearenv() {
	echo ${SCL_PORT} > /sys/class/gpio/unexport
	echo ${SDA_PORT} > /sys/class/gpio/unexport
	echo "unexport finish"
	exit 1
}

trap clearenv SIGINT

echo ${SCL_PORT} > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio${SCL_PORT}/direction

echo ${SDA_PORT} > /sys/class/gpio/export
echo "in" > /sys/class/gpio/gpio${SDA_PORT}/direction

sleep 1

while true ; do
	echo -n "SCL:1, "; echo 1 > /sys/class/gpio/gpio${SCL_PORT}/value
	echo -n "SDA:"; cat /sys/class/gpio/gpio${SDA_PORT}/value;
	sleep 1
	echo -n "SCL:0, "; echo 0 > /sys/class/gpio/gpio${SCL_PORT}/value
	echo -n "SDA:"; cat /sys/class/gpio/gpio${SDA_PORT}/value;
	sleep 1
done

