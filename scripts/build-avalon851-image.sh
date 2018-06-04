#!/bin/bash
#
# This is a script for build avalon851 controller image
#
#  Copyright 2018 Zhenxing Xu <xuzhenxing@canaan-creative.com>
#
# OPENWRT_DIR is ${ROOT_DIR}/openwrt, build the image in it
# Controller's image should include the following configurations:
#    ${AVA_MACHINE}_owrepo : OpenWrt repo, format: repo_url@repo_ver
#    feeds.${AVA_MACHINE}.conf : OpenWrt feeds, file locate in cgminer-openwrt-packages
#    ${AVA_TARGET_BOARD}_brdcfg : OpenWrt target and config, file locate in cgminer-openwrt-packages
#
# Learn bash: http://explainshell.com/

set -e

SCRIPT_VERSION=20180604

# Support machine: avalon851
AVA_MACHINE=avalon8

# Support target board: rpi3-modelb, rpi2-modelb, rpi1-modelb
[ -z "${AVA_TARGET_BOARD}" ] && AVA_TARGET_BOARD=rpi3-modelb

# OpenWrt repo
avalon8_owrepo="git://github.com/Canaan-Creative/openwrt-archive.git"

# OpenWrt feeds, features:bitcoind
[ -z "${FEATURE}" ] && FEEDS_CONF_URL=https://raw.github.com/Canaan-Creative/cgminer-openwrt-packages/master/cgminer/data/feeds.${AVA_MACHINE}.conf

# Board config: target(get it in the OpenWrt bin), config
rpi3_modelb_brdcfg=("brcm2708" "config.${AVA_MACHINE}.rpi3")
rpi2_modelb_brdcfg=("brcm2708" "config.${AVA_MACHINE}.rpi2")
rpi1_modelb_brdcfg=("brcm2708" "config.${AVA_MACHINE}.raspberry-pi")

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
ROOT_DIR=${SCRIPT_DIR}/avalon
OPENWRT_DIR=${ROOT_DIR}/openwrt

prepare_source() {
    echo "Gen firmware for ${AVA_TARGET_BOARD}:${AVA_MACHINE}"
    cd ${SCRIPT_DIR}
    [ ! -d avalon ] && mkdir -p avalon/bin
    cd avalon
    if [ ! -d openwrt ]; then
        eval OPENWRT_URL=\${${AVA_MACHINE}_owrepo}
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
    [ ! -e dl ] && mkdir dl
    cd ${OPENWRT_DIR}
    ln -sf ../dl
}

prepare_feeds() {
    cd ${OPENWRT_DIR}
    $DL_PROG ${FEEDS_CONF_URL} $DL_PARA feeds.conf && \
    ./scripts/feeds update -a && \
    ./scripts/feeds install -a

    if [ ! -e files ]; then
        ln -s feeds/cgminer/cgminer/root-files files
    fi
}

prepare_patch() {
    cd ${OPENWRT_DIR}
    tmp1=`cat ./feeds/cgminer/cgminer/files/cgminer.avalon8.config | grep "fan"`
    tmp2="	option fan		'10'"
    sed -i "s/${tmp1}/${tmp2}/g" ./feeds/cgminer/cgminer/files/cgminer.avalon8.config
}

prepare_config() {
    cd ${OPENWRT_DIR}
    eval OPENWRT_CONFIG=\${"`echo ${AVA_TARGET_BOARD//-/_}`"_brdcfg[1]} && cp ./feeds/cgminer/cgminer/data/${OPENWRT_CONFIG} .config
}

prepare_version() {
    cd ${OPENWRT_DIR}
    GIT_VERSION=`git ls-remote https://github.com/Canaan-Creative/cgminer avalon8 | cut -f1 | cut -c1-7`
    LUCI_GIT_VERSION=`git --git-dir=./feeds/luci/.git rev-parse HEAD | cut -c1-7`
    OW_GIT_VERSION=`git --git-dir=./feeds/cgminer/.git rev-parse HEAD | cut -c1-7`

    cat > ./files/etc/avalon_version << EOL
Avalon Firmware - $DATE
    luci: $LUCI_GIT_VERSION
    cgminer: $GIT_VERSION
    cgminer-packages: $OW_GIT_VERSION
EOL
}

build_image() {
    cd ${OPENWRT_DIR}
    yes "" | make oldconfig > /dev/null
    # clean before build
    make -j${CORE_NUM} clean world
}

do_release() {
    cd ${ROOT_DIR}
    eval AVA_TARGET_PLATFORM=\${"`echo ${AVA_TARGET_BOARD//-/_}`"_brdcfg[0]}
    mkdir -p ./bin/${DATE}/${AVA_TARGET_BOARD}/
    cp -a ./openwrt/bin/${AVA_TARGET_PLATFORM}/* ./bin/${DATE}/${AVA_TARGET_BOARD}/
}

cleanup() {
    cd ${ROOT_DIR}
    rm -rf openwrt/ > /dev/null
}

show_help() {
    echo "\
Usage: $0 [--version] [--help] [--build] [--cleanup]

     --version
     --help             Display help message

     --build            Get .config file and build firmware

     --cleanup          Remove all files

     AVA_TARGET_BOARD   Environment variable, available target:
                        rpi1-modelb, rpi2-modelb, rpi3-modelb

Written by: Zhenxing Xu <xuzhenxing@canaan-creative.com>
Version: ${SCRIPT_VERSION}"
}

if [ "$#" == "0" ]; then
    $0 --help
    exit 0
fi

for i in "$@"
do
    case $i in
        --version|--help)
            show_help
            exit
            ;;
        --build)
            prepare_source && prepare_feeds && prepare_patch && prepare_config && prepare_version && build_image && do_release
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
