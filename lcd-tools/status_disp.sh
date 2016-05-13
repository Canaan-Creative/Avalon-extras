#!/bin/bash
IP=192.168.1.10
PORT=4028

./lcd-tools -i

while true; do
	GHS=`cgminer-api estats ${IP} ${PORT} | grep "\[MM ID" | awk '{ print $21 }' | cut -c7- | sed 's/]//g'`
	TEMP=`cgminer-api estats ${IP} ${PORT} | grep "\[MM ID" | awk '{ print $16 }' | cut -c6- | sed 's/]//g'`
	TEMP0=`cgminer-api estats ${IP} ${PORT} | grep "\[MM ID" | awk '{ print $17 }' | cut -c7- | sed 's/]//g'`
	TEMP1=`cgminer-api estats ${IP} ${PORT} | grep "\[MM ID" | awk '{ print $18 }' | cut -c7- | sed 's/]//g'`

	MAXTEMP=${TEMP}
	if [ ${MAXTEMP} -lt ${TEMP0} ]; then
		MAXTEMP=${TEMP0}
	fi

	if [ ${MAXTEMP} -lt ${TEMP1} ]; then
		MAXTEMP=${TEMP1}
	fi

	GHS=`printf "%-8.2f" ${GHS}`
	MAXTEMP=`printf "%-5d" ${MAXTEMP}`
	DISPLAY="GHSmm:${GHS}\nTemp:${MAXTEMP}"
	echo ${DISPLAY}
	./lcd-tools -s "${DISPLAY}"
	sleep 2
done
