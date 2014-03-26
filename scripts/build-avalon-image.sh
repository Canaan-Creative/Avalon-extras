#!/bin/bash

#MACHINE=avalon
MACHINE=avalon2	# Support Avalon2/MM firmware

HOST_TARGET=ar71xx	# TP-LINK WR703N
#HOST_TARGET=brcm2708	# Raspberry Pi

if [ "${HOST_TARGET}" == "ar71xx" ]; then
    OPENWRT_CONFIG=config.${MACHINE}.703n
fi

if [ "${HOST_TARGET}" == "brcm2708" ]; then
    OPENWRT_CONFIG=config.${MACHINE}.raspberry-pi
fi


VERSION=20140124
OPENWRT_PATH=./openwrt
LUCI_PATH=./luci

CORE_NUM="`nproc`"
[ "$CORE_NUM" -ge "2" ] || CORE_NUM=2

## Version
if [ "$#" == "0" -a ! -d ./avalon ]; then
    $0 --help
    exit 0
elif [ "$1" == "--version" ] || [ "$1" == "--help" ]; then
    echo "\

Usage: $0 [--version] [--help] [--clone] [--update] [--cgminer]

     --version
     --help	Display help message

     --clone	Get all source code and build firmware, ONLY NEED ONCE

     --update	Update all repos

     --cgminer	Re-compile only cgminer openwrt package

Without any parameter I will build the Avalon firmware. make sure you run
  [$0 --clone] ONCE for get all sources

     --removeall	Remove all files

Written by: Xiangfu <xiangfu@openmobilefree.net>
		    19BT2rcGStUK23vwrmF6y6s3ZWpxzQQn8x

						     Version: ${VERSION}"
    exit 0
fi


## Remove
if [ "$1" == "--removeall" ]; then
    rm -rf avalon/cgminer avalon/cgminer-openwrt-packages/ avalon/luci/ avalon/openwrt/ 
    exit $?
fi


## Init
if [ "$1" == "--clone" ]; then
    [ ! -d avalon ] && mkdir -p avalon/bin
    cd avalon
    svn co svn://svn.openwrt.org/openwrt/trunk@39381 openwrt
    git clone git://github.com/BitSyncom/cgminer.git
    git clone git://github.com/BitSyncom/cgminer-openwrt-packages.git

    if [ "${MACHINE}" == "avalon2" ]; then
	git clone git://github.com/BitSyncom/luci.git && (cd luci && git checkout -b cgminer-webui-avalon2 origin/cgminer-webui-avalon2)
    else
	git clone git://github.com/BitSyncom/luci.git && (cd luci && git checkout -b cgminer-webui origin/cgminer-webui)
    fi
     
    cd openwrt
    [ -d ../../dl ] && ln -sf ../dl ../dl
    [ ! -e ../dl ] && mkdir ../dl
    ln -sf ../dl
    wget https://raw.github.com/BitSyncom/cgminer-openwrt-packages/master/cgminer/data/feeds.conf
    ./scripts/feeds update -a && ./scripts/feeds install -a

    ln -s feeds/cgminer/cgminer/root-files files

    wget https://raw.github.com/BitSyncom/cgminer-openwrt-packages/master/cgminer/data/${OPENWRT_CONFIG} -O .config
    yes "" | make oldconfig
    make -j${CORE_NUM} V=s IGNORE_ERRORS=m || make V=s IGNORE_ERRORS=m
    exit $?
fi


## Update all git
if [ "$1" == "--update" ]; then
    (cd avalon/cgminer && git pull)
    (cd avalon/luci    && git pull)
    (cd avalon/cgminer-openwrt-packages && git pull)
    cd avalon/openwrt
    ./scripts/feeds update cgminer; ./scripts/feeds install -a -p cgminer
    wget https://raw.github.com/BitSyncom/cgminer-openwrt-packages/master/cgminer/data/${OPENWRT_CONFIG} -O .config
    yes "" | make oldconfig
    exit $?
fi


## Rebuild cgminer
cd avalon
make -j${CORE_NUM} -C ${OPENWRT_PATH} package/cgminer/{clean,compile} V=s || make -C ${OPENWRT_PATH} package/cgminer/{clean,compile} V=s
RET="$?"
if [ "${RET}" != "0" ] || [ "$1" == "--cgminer" ]; then
    if [ "${RET}" == "0" ]; then
	cp ${OPENWRT_PATH}/bin/${HOST_TARGET}/packages/cgminer*.ipk  bin/
	cp ${OPENWRT_PATH}/build_dir/target-*uClibc-*/cgminer-*/cgminer bin/cgminer-${HOST_TARGET}
	exit "$?"
    fi
    exit "${RET}"
fi


## Build the Web UI & OpenWrt
DATE=`date +%Y%m%d`
## Get all repo commit for Avalon version file /etc/avalon_version
GIT_VERSION=`cd cgminer && git rev-parse HEAD | cut -c 1-7`
if [ ! -z "`cd cgminer && git status -s -uno`" ]; then
    GIT_STATUS="+"
fi

LUCI_GIT_VERSION=`cd luci && git rev-parse HEAD | cut -c 1-7`
if [ ! -z "`cd luci && git status -s -uno`" ]; then
    LUCI_GIT_STATUS="+"
fi

OW_GIT_VERSION=`cd cgminer-openwrt-packages && git rev-parse HEAD | cut -c 1-7`
if [ ! -z "`cd cgminer-openwrt-packages && git status -s -uno`" ]; then
    OW_GIT_STATUS="+"
fi

rm -rf ${LUCI_PATH}/applications/luci-cgminer/dist                                                && \
( make -j${CORE_NUM} -C ${LUCI_PATH} || make -C ${LUCI_PATH} )                                    && \
cp -a  ${LUCI_PATH}/applications/luci-cgminer/dist/* ${OPENWRT_PATH}/files/                       && \
echo "$DATE"		                              > ${OPENWRT_PATH}/files/etc/avalon_version  && \
echo "cgminer: $GIT_VERSION$GIT_STATUS"               >> ${OPENWRT_PATH}/files/etc/avalon_version && \
echo "cgminer-openwrt-packages: $OW_GIT_VERSION$OW_GIT_STATUS" >> ${OPENWRT_PATH}/files/etc/avalon_version && \
echo "luci: $LUCI_GIT_VERSION$LUCI_GIT_STATUS"        >> ${OPENWRT_PATH}/files/etc/avalon_version && \
( make -j${CORE_NUM} -C ${OPENWRT_PATH} V=s IGNORE_ERRORS=m || make -C ${OPENWRT_PATH} V=s IGNORE_ERRORS=m ) && \
mkdir -p bin/${DATE}/                                     && \
cp -a ${OPENWRT_PATH}/bin/${HOST_TARGET}/*  bin/${DATE}/

