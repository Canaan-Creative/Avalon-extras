Scripts for factory
======================

# Scripts:
- burn-mm.sh       Program FPGA firmware
- burn-pmu.sh      Program PMU firmware
- Makefile         Program and erase utilities wrapper
- README.md        This file
- install.sh       Install script
- desktop          Shortcuts for desktop users

# Depends
	Xilinx ISE (/home/Xilinx/14.6/ISE_DS)
	LPCXpresso (/usr/local/lpcxpresso_7.9.2_493/lpcxpresso/bin)
	Git

# Install Guide
Login in with `factory` user, then invoke the commands as the
following steps:

	cd ~
	wget https://raw.githubusercontent.com/Canaan-Creative/Avalon-extras/master/scripts/factory/install.sh
	sh install.sh

# Synchronize with the latest version
	cd ~/Avalon-extras
	git pull

