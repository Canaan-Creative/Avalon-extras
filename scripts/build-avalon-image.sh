#!/bin/bash


VERSION=20130918
OPENWRT_PATH=./openwrt
LUCI_PATH=./luci

mkdir -p avalon/dl
mkdir -p avalon/bin


## Version
if [ "$1" == "--version" ] || [ "$1" == "--help" ]; then
    echo "\

Usage: $0 [--version] [--help] [--clone] [--update] [--cgminer]

     --version
     --help	Display help message

     --clone	Get all source code and build firmware, ONLY NEED ONCE

     --update	Update all repos

     --cgminer	Re-compile only cgminer openwrt package

Without any parameter I will build the Avalon firmware. make sure you run
  [$0 --clone] ONCE for get all sources

Written by: Xiangfu <xiangfu@openmobilefree.net>
		    19BT2rcGStUK23vwrmF6y6s3ZWpxzQQn8x

						     Version: ${VERSION}"
    exit 0
fi


## Init
if [ "$1" == "--clone" ]; then
    cd avalon
    svn co svn://svn.openwrt.org/openwrt/trunk@38031 openwrt
    git clone git://github.com/BitSyncom/cgminer.git
    git clone git://github.com/BitSyncom/cgminer-openwrt-packages.git
    git clone git://github.com/BitSyncom/luci.git && (cd luci && git checkout -b cgminer-webui origin/cgminer-webui)
     
    cd openwrt
    ln -s ../dl
    wget https://raw.github.com/BitSyncom/cgminer-openwrt-packages/master/cgminer/data/feeds.conf
    wget https://raw.github.com/BitSyncom/cgminer-openwrt-packages/master/cgminer/data/config -O .config
    yes "" | make oldconfig
    ./scripts/feeds update -a && ./scripts/feeds install -a

    ln -s feeds/cgminer/cgminer/root-files files
    (cd feeds/packages && \
        svn revert libs/curl/Makefile && \
	patch -Np0 < ../cgminer/cgminer/data/feeds-patches/packages-libs-curl-disable-libopenssl.patch)

    cp feeds/cgminer/cgminer/data/config .config
    yes "" | make oldconfig
    make V=s IGNORE_ERRORS=m
    exit 0;
fi


## Update all git
if [ "$1" == "--update" ]; then
    (cd avalon/cgminer && git pull)
    (cd avalon/luci    && git pull)
    (cd avalon/cgminer-openwrt-packages && git pull)
    (cd avalon/openwrt && ./scripts/feeds update cgminer; ./scripts/feeds install -a -p cgminer)
    (cd avalon/openwrt/feeds/packages && \
        svn revert libs/curl/Makefile && \
	patch -Np0 < ../cgminer/cgminer/data/feeds-patches/packages-libs-curl-disable-libopenssl.patch)
    exit 0
fi


## Rebuild cgminer
cd avalon
make -C ${OPENWRT_PATH} package/cgminer/{clean,compile} V=s
RET="$?"
if [ "${RET}" != "0" ] || [ "$1" == "--cgminer" ]; then
    if [ "${RET}" == "0" ]; then
	cp ${OPENWRT_PATH}/bin/ar71xx/packages/cgminer_*_ar71xx.ipk  bin/
	cp ${OPENWRT_PATH}/build_dir/target-mips_r2_uClibc-0.9.33.2/cgminer-*/cgminer bin/cgminer-mips
    fi
    exit "$?"
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
make -C ${LUCI_PATH}                                                                              && \
cp -a  ${LUCI_PATH}/applications/luci-cgminer/dist/* ${OPENWRT_PATH}/files/                       && \
echo "$DATE"		                              > ${OPENWRT_PATH}/files/etc/avalon_version  && \
echo "cgminer: $GIT_VERSION$GIT_STATUS"               >> ${OPENWRT_PATH}/files/etc/avalon_version && \
echo "cgminer-openwrt-packages: $OW_GIT_VERSION$OW_GIT_STATUS" >> ${OPENWRT_PATH}/files/etc/avalon_version && \
echo "luci: $LUCI_GIT_VERSION$LUCI_GIT_STATUS"        >> ${OPENWRT_PATH}/files/etc/avalon_version && \
make -C ${OPENWRT_PATH} V=s IGNORE_ERRORS=m                  && \
mkdir -p bin/${DATE}/                                     && \
cp -a ${OPENWRT_PATH}/bin/ar71xx/*  bin/${DATE}/
