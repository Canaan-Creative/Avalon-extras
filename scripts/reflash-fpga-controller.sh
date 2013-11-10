#!/bin/bash

ISEDIR=/home/Xilinx/14.6/ISE_DS
SPI_CHIP=W25Q80BV

if [ "$1" == "--reflash" ]; then
    BATCH_FILE=`mktemp`

    cat > ${BATCH_FILE}<<EOF
setMode -bs
setCable -p auto
setCableSpeed -speed 6000000
Identify -inferir
identifyMPM
attachflash -position 1 -spi "$SPI_CHIP"
assignFileToAttachedFlash -p 1 -file "$2"
erase -p 1 -dataWidth 4 -spionly
Program -p 1 -dataWidth 4 -spionly -e -v -loadfpga
closeCable
quit

EOF

    if [ "$2" == "--cx3sprog" ]; then
	xc3sprog -c qi xc6slx16-2-ftg256.bscan_s6_spi_isf_ext.bit && sleep 1 && xc3sprog -c qi -v -I "$3"
	xc3sprog -c qi -v -I file.bin:R:0:bin
	dd if=file.bin bs=68 skip=1 of=file2.bin
	xc3sprog -c qi -v -I file2.bin:w:0:bin
	rm -f file.bin file2.bin
	exit 0;
    fi
fi

if [ "$1" == "--load" ]; then
    BATCH_FILE=`mktemp`

    cat > ${BATCH_FILE}<<EOF
setmode -bscan
setCable -p auto
setCableSpeed -speed 12000000
addDevice -p 1 -file "$2"
program -p 1
closeCable
quit

EOF

fi

if [ "$1" == "--erase" ]; then
    BATCH_FILE=`mktemp`

    cat > ${BATCH_FILE}<<EOF
setMode -bs
setCable -p auto
setCableSpeed -speed 6000000
Identify -inferir
identifyMPM
erase -p 1 -dataWidth 4 -spionly -spi "$SPI_CHIP"
closeCable
quit

EOF

fi

source ${ISEDIR}/settings`getconf LONG_BIT`.sh
impact -batch $BATCH_FILE
