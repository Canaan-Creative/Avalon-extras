#!/bin/bash

IP=192.168.0.100

DATE=`date +%Y%m%d`
GIT_VERSION=`git rev-parse HEAD | cut -c 1-7`
if [ ! -z "`git status -s -uno`" ]; then
	GIT_STATUS="+"
fi

LUCI_GIT_VERSION=`cd ../luci && git rev-parse HEAD | cut -c 1-7`
if [ ! -z "`cd ../luci git status -s -uno`" ]; then
	LUCI_GIT_STATUS="+"
fi

OW_GIT_VERSION=`cd ../cgminer-openwrt-package && git rev-parse HEAD | cut -c 1-7`
if [ ! -z "`cd ../cgminer-openwrt-package && git status -s -uno`" ]; then
	OW_GIT_STATUS="+"
fi


git archive --format tar.gz --prefix=cgminer-20130108/ HEAD > ${HOME}/workspace/PanGu/dl/cgminer-20130108-HEAD.tar.gz && \
rm -rf  ${HOME}/workspace/bitcoin/avalon/luci/applications/luci-cgminer/dist && \
make -C ${HOME}/workspace/bitcoin/avalon/luci&& \
cp -a   ${HOME}/workspace/bitcoin/avalon/luci/applications/luci-cgminer/dist/* \
        ${HOME}/workspace/PanGu/openwrt/files/ && \
echo "$DATE" > ${HOME}/workspace/PanGu/openwrt/files/etc/avalon_version && \
echo "cgminer-$GIT_VERSION$GIT_STATUS" >> ${HOME}/workspace/PanGu/openwrt/files/etc/avalon_version && \
echo "luci-$LUCI_GIT_VERSION$LUCI_GIT_STATUS" >> ${HOME}/workspace/PanGu/openwrt/files/etc/avalon_version && \
echo "openwrt-package-$OW_GIT_VERSION$OW_GIT_STATUS" >> ${HOME}/workspace/PanGu/openwrt/files/etc/avalon_version && \
make -C ${HOME}/workspace/PanGu/openwrt package/cgminer/{clean,compile} V=99 && \
make -C ${HOME}/workspace/PanGu/openwrt && \
cp ${HOME}/workspace/PanGu/openwrt/bin/ar71xx/openwrt-ar71xx-generic-tl-wr703n-v1-squashfs-factory.bin \
     ${HOME}/workspace/PanGu/openwrt/bin/old/openwrt-ar71xx-generic-tl-wr703n-v1-squashfs-factory-${DATE}.bin;  \
ssh-keygen -f "${HOME}/.ssh/known_hosts" -R ${IP} && \
scp ${HOME}/workspace/PanGu/openwrt/bin/ar71xx/openwrt-ar71xx-generic-tl-wr703n-v1-squashfs-factory.bin root@${IP}:/tmp/abc && \
ssh root@${IP} mtd -r write /tmp/abc firmware
