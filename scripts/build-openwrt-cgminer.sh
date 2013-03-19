#!/bin/bash

PATH=/home/xiangfu/workspace/PanGu/openwrt/staging_dir/toolchain-mips_r2_gcc-4.6-linaro_uClibc-0.9.33.2/bin:$PATH
STAGING_DIR=/home/xiangfu/workspace/PanGu/openwrt/staging_dir/toolchain-mips_r2_gcc-4.6-linaro_uClibc-0.9.33.2
export PATH
export STAGING_DIR

IP=$1

cp ${HOME}/workspace/bitcoin/avalon/cgminer/driver-avalon.c \
     ${HOME}/workspace/PanGu/openwrt/build_dir/target-mips_r2_uClibc-0.9.33.2/cgminer-20130108 && \
cp ${HOME}/workspace/bitcoin/avalon/cgminer/driver-avalon.h \
     ${HOME}/workspace/PanGu/openwrt/build_dir/target-mips_r2_uClibc-0.9.33.2/cgminer-20130108 && \
cp ${HOME}/workspace/bitcoin/avalon/cgminer/cgminer.c       \
     ${HOME}/workspace/PanGu/openwrt/build_dir/target-mips_r2_uClibc-0.9.33.2/cgminer-20130108 && \
make -C ${HOME}/workspace/PanGu/openwrt/build_dir/target-mips_r2_uClibc-0.9.33.2/cgminer-20130108 && \
cp ${HOME}/workspace/PanGu/openwrt/build_dir/target-mips_r2_uClibc-0.9.33.2/cgminer-20130108/cgminer ./cgminer-mips && \
scp cgminer-mips root@$IP:/tmp/
