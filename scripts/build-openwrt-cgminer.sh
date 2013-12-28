#!/bin/bash

A_OPENWRT_DIR=/home/xiangfu/var/avalon/openwrt
A_TARGET=mips_34kc

export PATH=${A_OPENWRT_DIR}/staging_dir/host/bin/:$PATH

make clean

rm -f aclocal.m4;
if [ -f ./configure.ac ] || [ -f ./configure.in ]; then
    [ -d ./autom4te.cache ] && rm -rf autom4te.cache;
    [ -e ./config.rpath ] || ln -s ${A_OPENWRT_DIR}/scripts/config.rpath ./config.rpath;
    touch NEWS AUTHORS COPYING ABOUT-NLS ChangeLog;
    AUTOM4TE=${A_OPENWRT_DIR}/staging_dir/host/bin/autom4te \
	AUTOCONF=${A_OPENWRT_DIR}/staging_dir/host/bin/autoconf \
	AUTOMAKE=${A_OPENWRT_DIR}/staging_dir/host/bin/automake \
	ACLOCAL=${A_OPENWRT_DIR}/staging_dir/host/bin/aclocal \
	AUTOHEADER=${A_OPENWRT_DIR}/staging_dir/host/bin/autoheader \
	LIBTOOLIZE=${A_OPENWRT_DIR}/staging_dir/host/bin/libtoolize \
	LIBTOOL=${A_OPENWRT_DIR}/staging_dir/host/bin/libtool \
	M4=${A_OPENWRT_DIR}/staging_dir/host/bin/m4 \
	AUTOPOINT=true \
	${A_OPENWRT_DIR}/staging_dir/host/bin/autoreconf -v -f -i -s -B ${A_OPENWRT_DIR}/staging_dir/host/share/aclocal -I ${A_OPENWRT_DIR}/staging_dir/target-${A_TARGET}_uClibc-0.9.33.2/host/share/aclocal -I ${A_OPENWRT_DIR}/staging_dir/target-${A_TARGET}_uClibc-0.9.33.2/usr/share/aclocal -I m4 -I . . || true;
fi

CPPFLAGS="-I${A_OPENWRT_DIR}/staging_dir/target-${A_TARGET}_uClibc-0.9.33.2/usr/include -I${A_OPENWRT_DIR}/staging_dir/target-${A_TARGET}_uClibc-0.9.33.2/include -I${A_OPENWRT_DIR}/staging_dir/toolchain-${A_TARGET}_gcc-4.6-linaro_uClibc-0.9.33.2/usr/include -I${A_OPENWRT_DIR}/staging_dir/toolchain-${A_TARGET}_gcc-4.6-linaro_uClibc-0.9.33.2/include " \
LDFLAGS="-L${A_OPENWRT_DIR}/staging_dir/target-${A_TARGET}_uClibc-0.9.33.2/usr/lib -L${A_OPENWRT_DIR}/staging_dir/target-${A_TARGET}_uClibc-0.9.33.2/lib -L${A_OPENWRT_DIR}/staging_dir/toolchain-${A_TARGET}_gcc-4.6-linaro_uClibc-0.9.33.2/usr/lib -L${A_OPENWRT_DIR}/staging_dir/toolchain-${A_TARGET}_gcc-4.6-linaro_uClibc-0.9.33.2/lib -Wl,-rpath-link=${A_OPENWRT_DIR}/staging_dir/target-${A_TARGET}_uClibc-0.9.33.2/usr/lib " \
CFLAGS="-g -Wall -W -O2" \
STAGING_DIR="${A_OPENWRT_DIR}/staging_dir/" \
./configure --target=mips-openwrt-linux --host=mips-openwrt-linux --without-curses --enable-avalon && \
make -j
