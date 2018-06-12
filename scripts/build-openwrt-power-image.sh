#!/bin/bash
#
# This is a script for build avalon851 controller image
#
#  Copyright June 2018 Zhenxing Xu <xuzhenxing@canaan-creative.com>
#
# OPENWRT_DIR is ${ROOT_DIR}/openwrt, build the image in it
#
# Learn bash: http://explainshell.com/

set -e

SCRIPT_VERSION='2018-06-06'

# OpenWrt repo
openwrt_repo="git://github.com/openwrt/openwrt.git@a789c0f4"

# OpenWrt config files and read power file
FEEDS_CONF_URL=https://raw.github.com/Canaan-Creative/Avalon-extras/master/dds238-2-power/feeds.conf
DEV_CONF_URL=https://raw.github.com/Canaan-Creative/Avalon-extras/master/dds238-2-power/rpi3.conf

DHCP_CONF_URL=https://raw.github.com/Canaan-Creative/Avalon-extras/master/dds238-2-power/etc/config/dhcp
NETWORK_CONF_URL=https://raw.github.com/Canaan-Creative/Avalon-extras/master/dds238-2-power/etc/config/network

IPV6_CONF_URL=https://raw.github.com/Canaan-Creative/Avalon-extras/master/dds238-2-power/etc/sysctl.conf
RC_CONF_URL=https://raw.github.com/Canaan-Creative/Avalon-extras/master/dds238-2-power/etc/rc.local

POWER_CONF_URL=https://raw.github.com/Canaan-Creative/Avalon-extras/master/dds238-2-power/usr/bin/read-power.py

which wget > /dev/null && DL_PROG=wget && DL_PARA="-nv -O"
which curl > /dev/null && DL_PROG=curl && DL_PARA="-L -o"

# According to http://wiki.openwrt.org/doc/howto/build
unset SED
unset GREP_OPTIONS
[ "`id -u`" == "0" ] && echo "[ERROR]: Please use non-root user" && exit 1

# Adjust CORE_NUM by yourself
[ -z "${CORE_NUM}" ] && CORE_NUM="$(expr $(nproc) + 1)"
DATE=`date +%Y%m%d`
SCRIPT_FILE="$(readlink -f $0)"
SCRIPT_DIR=`dirname ${SCRIPT_FILE}`
OPENWRT_DIR=${SCRIPT_DIR}/openwrt

# Get OpenWrt source codes
prepare_source() {
    cd ${SCRIPT_DIR}
    if [ ! -d openwrt ]; then
        eval OPENWRT_URL=\${openwrt_repo}
        PROTOCOL="`echo ${OPENWRT_URL} | cut -d : -f 1`"

        case "${PROTOCOL}" in
            git)
                GITBRANCH="`echo ${OPENWRT_URL} | cut -s -d @ -f 2`"
                GITREPO="`echo ${OPENWRT_URL} | cut -d @ -f 1`"
                [ -z ${GITBRANCH} ] && GITBRANCH=master
                git clone ${GITREPO} openwrt
                cd openwrt && git checkout ${GITBRANCH}
                cd ..
                ;;
            svn)
                SVNVER="`echo ${OPENWRT_URL} | cut -s -d @ -f 2`"
                SVNREPO="`echo ${OPENWRT_URL} | cut -d @ -f 1`"
                if [ -z ${SVNVER} ]; then
                    svn co ${SVNREPO}@${SVNVER} openwrt
                else
                    svn co ${SVNREPO} openwrt
                fi
                ;;
            *)
                echo "Protocol not supported"; exit 1;
                ;;
        esac
    fi
}

prepare_feeds() {
    cd ${OPENWRT_DIR}
    $DL_PROG ${FEEDS_CONF_URL} $DL_PARA feeds.conf && \
    ./scripts/feeds update -a && \
    ./scripts/feeds install -a
}

prepare_config() {
    cd ${OPENWRT_DIR}
    $DL_PROG ${DEV_CONF_URL} $DL_PARA .config
}

prepare_patch() {
    cd ${OPENWRT_DIR}

    # /etc/config files
    [ ! -e ${OPENWRT_DIR}/package/base-files/files/etc/config ] && \
    mkdir ${OPENWRT_DIR}/package/base-files/files/etc/config

    $DL_PROG ${DHCP_CONF_URL} $DL_PARA ./package/base-files/files/etc/config/dhcp
    $DL_PROG ${NETWORK_CONF_URL} $DL_PARA ./package/base-files/files/etc/config/network

    # /etc/sysctl.conf and /etc/rc.local files
    $DL_PROG ${IPV6_CONF_URL} $DL_PARA ./package/base-files/files/etc/sysctl.conf
    $DL_PROG ${RC_CONF_URL} $DL_PARA ./package/base-files/files/etc/rc.local

    # read-power.py file
    [ ! -e ${OPENWRT_DIR}/package/base-files/files/usr/bin ] && \
    mkdir ${OPENWRT_DIR}/package/base-files/files/usr/bin

    $DL_PROG ${POWER_CONF_URL} $DL_PARA ./package/base-files/files/usr/bin/readpower
    chmod +x ./package/base-files/files/usr/bin/readpower
}

build_image() {
    cd ${OPENWRT_DIR}
    yes "" | make oldconfig > /dev/null
    # clean before build
    make -j${CORE_NUM} clean world
}

do_release() {
    cd ${SCRIPT_DIR}
    if [ ! -e bin ]; then
        mkdir ./bin
    fi
    cp -a ./openwrt/bin/targets/brcm2708/bcm2710/* ./bin/
}

cleanup() {
    cd ${ROOT_DIR}
    rm -rf openwrt/ > /dev/null
}

show_help() {
    echo "\
Usage: $0 [--help] [--build] [--cleanup]
    --help             Display help message
    --build            Get .config file and build firmware
    --cleanup          Remove all files

Written by: Zhenxing Xu <xuzhenxing@canaan-creative.com>
    Version: ${SCRIPT_VERSION}"
}

# Paramter is null, display help messages
if [ "$#" == "0" ]; then
    $0 --help
    exit 0
fi

for i in "$@"
do
    case $i in
        --help)
            show_help
            exit
            ;;
        --build)
            prepare_source && prepare_feeds && prepare_config && prepare_patch && build_image && do_release
            ;;
        --cleanup)
            cleanup
            ;;
        *)
            show_help
            exit
            ;;
    esac
done
