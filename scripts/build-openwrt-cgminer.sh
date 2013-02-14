IP=192.168.0.100

cp ${HOME}/workspace/bitcoin/avalon/cgminer/driver-avalon.c \
     ${HOME}/workspace/PanGu/openwrt/build_dir/target-mips_r2_uClibc-0.9.33.2/cgminer-20130108 && \
cp ${HOME}/workspace/bitcoin/avalon/cgminer/driver-avalon.h \
     ${HOME}/workspace/PanGu/openwrt/build_dir/target-mips_r2_uClibc-0.9.33.2/cgminer-20130108 && \
cp ${HOME}/workspace/bitcoin/avalon/cgminer/cgminer.c       \
     ${HOME}/workspace/PanGu/openwrt/build_dir/target-mips_r2_uClibc-0.9.33.2/cgminer-20130108 && \
make -C build_dir/target-mips_r2_uClibc-0.9.33.2/cgminer-20130108 && \
cp ./build_dir/target-mips_r2_uClibc-0.9.33.2/cgminer-20130108/cgminer ./cgminer-mips && \
scp cgminer-mips root@$IP:/tmp/cgminer && \
scp ./r root@$IP:/tmp/ 


#ssh-keygen -f "${HOME}/.ssh/known_hosts" -R $IP && \
