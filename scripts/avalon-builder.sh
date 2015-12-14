#!/bin/bash
set -e

AVA_MACHINE=avalon6
[ -z $AVA_TARGET_BOARD ] && AVA_TARGET_BOARD=rpi2
case $AVA_TARGET_BOARD in
	"raspberry-pi" | "rpi2" )
		AVA_TARGET_PLATFORM=brcm2708
		;;
	"mr3020" )
		AVA_TARGET_PLATFORM=ar71xx
		;;
esac

OPENWRT_URL=git://git.openwrt.org/15.05/openwrt.git
OPENWRT_CONFIG=config.$AVA_MACHINE.$AVA_TARGET_BOARD

unset SED
unset GREP_OPTIONS
[ "`id -u`" == "0" ] && echo "[ERROR]: Please use non-root user" && exit 1
CORE_NUM="$(expr $(nproc) + 1)"
[ -z "$CORE_NUM" ] && CORE_NUM=2


[ ! -d avalon ] && mkdir -p avalon/bin
cd avalon
[ ! -d openwrt ] && git clone $OPENWRT_URL openwrt
cd openwrt
[ ! -f toolchain-uclibc-xattr.patch ] &&\
	wget https://github.com/archangdcc/avalon-extras/raw/master/openwrt-patches/toolchain-uclibc-xattr.patch &&\
	patch -p0 < toolchain-uclibc-xattr.patch

cat > feeds.conf << EOL
src-git packages git://github.com/openwrt/packages.git
src-git luci git://github.com/archangdcc/luci.git;avalon6
src-git cgminer git://github.com/Canaan-Creative/cgminer-openwrt-packages.git
EOL
./scripts/feeds update -a
./scripts/feeds install -a
[ ! -e files ] && ln -s feeds/cgminer/cgminer/root-files files


DATE=`date +%Y%m%d`
GIT_VERSION=`git ls-remote https://github.com/Canaan-Creative/cgminer avalon4 | cut -f1 | cut -c1-7`
LUCI_GIT_VERSION=`git --git-dir=feeds/luci/.git rev-parse HEAD | cut -c1-7`
OW_GIT_VERSION=`git --git-dir=feeds/cgminer/.git rev-parse HEAD | cut -c1-7`

cat > files/etc/avalon_version << EOL
Avalon Firmware - $DATE
   luci: $LUCI_GIT_VERSION
   cgminer: $GIT_VERSION
   cgminer-packages: $OW_GIT_VERSION
EOL


make defconfig
make prereq
cp feeds/cgminer/cgminer/data/$OPENWRT_CONFIG .config
yes "" | make oldconfig > /dev/null


make -j$CORE_NUM


cd ..
mkdir -p bin/${DATE}/
mv openwrt/bin/${AVA_TARGET_PLATFORM} bin/${DATE}/${AVA_TARGET_BOARD}
