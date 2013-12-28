#!/bin/bash

export PATH=/home/xiangfu/var/avalon/openwrt/staging_dir/host/bin/:$PATH

make clean

rm -f aclocal.m4;
if [ -f ./configure.ac ] || [ -f ./configure.in ]; then
    [ -d ./autom4te.cache ] && rm -rf autom4te.cache;
    [ -e ./config.rpath ] || ln -s /home/xiangfu/var/avalon/openwrt/scripts/config.rpath ./config.rpath;
    touch NEWS AUTHORS COPYING ABOUT-NLS ChangeLog;
    AUTOM4TE=/home/xiangfu/var/avalon/openwrt/staging_dir/host/bin/autom4te \
	AUTOCONF=/home/xiangfu/var/avalon/openwrt/staging_dir/host/bin/autoconf \
	AUTOMAKE=/home/xiangfu/var/avalon/openwrt/staging_dir/host/bin/automake \
	ACLOCAL=/home/xiangfu/var/avalon/openwrt/staging_dir/host/bin/aclocal \
	AUTOHEADER=/home/xiangfu/var/avalon/openwrt/staging_dir/host/bin/autoheader \
	LIBTOOLIZE=/home/xiangfu/var/avalon/openwrt/staging_dir/host/bin/libtoolize \
	LIBTOOL=/home/xiangfu/var/avalon/openwrt/staging_dir/host/bin/libtool \
	M4=/home/xiangfu/var/avalon/openwrt/staging_dir/host/bin/m4 \
	AUTOPOINT=true \
	/home/xiangfu/var/avalon/openwrt/staging_dir/host/bin/autoreconf -v -f -i -s -B /home/xiangfu/var/avalon/openwrt/staging_dir/host/share/aclocal -I /home/xiangfu/var/avalon/openwrt/staging_dir/target-mips_34kc_uClibc-0.9.33.2/host/share/aclocal -I /home/xiangfu/var/avalon/openwrt/staging_dir/target-mips_34kc_uClibc-0.9.33.2/usr/share/aclocal -I m4 -I . . || true;
fi

CPPFLAGS="-I/home/xiangfu/var/avalon/openwrt/staging_dir/target-mips_34kc_uClibc-0.9.33.2/usr/include -I/home/xiangfu/var/avalon/openwrt/staging_dir/target-mips_34kc_uClibc-0.9.33.2/include -I/home/xiangfu/var/avalon/openwrt/staging_dir/toolchain-mips_34kc_gcc-4.6-linaro_uClibc-0.9.33.2/usr/include -I/home/xiangfu/var/avalon/openwrt/staging_dir/toolchain-mips_34kc_gcc-4.6-linaro_uClibc-0.9.33.2/include " \
LDFLAGS="-L/home/xiangfu/var/avalon/openwrt/staging_dir/target-mips_34kc_uClibc-0.9.33.2/usr/lib -L/home/xiangfu/var/avalon/openwrt/staging_dir/target-mips_34kc_uClibc-0.9.33.2/lib -L/home/xiangfu/var/avalon/openwrt/staging_dir/toolchain-mips_34kc_gcc-4.6-linaro_uClibc-0.9.33.2/usr/lib -L/home/xiangfu/var/avalon/openwrt/staging_dir/toolchain-mips_34kc_gcc-4.6-linaro_uClibc-0.9.33.2/lib -Wl,-rpath-link=/home/xiangfu/var/avalon/openwrt/staging_dir/target-mips_34kc_uClibc-0.9.33.2/usr/lib " \
CFLAGS="-g -Wall -W -O2" \
STAGING_DIR="/home/xiangfu/var/avalon/openwrt/staging_dir/" \
./configure --target=mips-openwrt-linux --host=mips-openwrt-linux --without-curses --enable-avalon && \
make -j
