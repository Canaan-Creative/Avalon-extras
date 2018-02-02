#
# Author: Mikeqin <Fengling.Qin@gmail.com>
#
# This is free and unencumbered software released into the public domain.
# For details see the UNLICENSE file at the root of the source tree.
#
# ----- Customer ----------------------------------------------------------
# MM_PLATFORM: MM721, MM741, MM821, MM841
MM_PLATFORM ?= MM721

# MCU_PLATFORM: pmu721, pmu741, pmu821, auc2, auc3
MCU_PLATFORM ?= pmu721

BATCHFILE	:= $(shell mktemp)
isedir  ?= /home/Xilinx/14.6/ISE_DS
xil_env ?= . $(isedir)/settings$(shell getconf LONG_BIT).sh &>/dev/null
ifeq ($(MCU_PLATFORM),pmu821)
    NXP_PARAMETERS = -g -2 -vendor=NXP -pLPC824 -wire=winUSB -s50 -flash-driver=LPC800_32.cfx
else
    NXP_PARAMETERS = -g -2 -vendor=NXP -pLPC11U14/201 -wire=winUSB -s50 -flash-driver=LPC11_12_13_32K_4K.cfx
endif
LPCXPRESSODIR ?= /usr/local/lpcxpresso_7.9.2_493/lpcxpresso/bin
LPCLINK_FIRM ?= $(LPCXPRESSODIR)/LPCXpressoWIN.enc
SHELL := /bin/bash

# Install cable driver for Linux
# http://guqian110.github.io/pages/2014/03/27/install_ise_modelsim_on_ubuntu.html
.PHONY: reflash load erase erase_ulink2 reflash_ulink2

# Bitstream rules
reflash: $(MM_PLATFORM).mcs
	echo setmode -bs	>> $(BATCHFILE)
	echo setcable -p auto	>> $(BATCHFILE)
	echo identify		>> $(BATCHFILE)
ifeq ($(MM_PLATFORM),MM721)
	echo attachFlash -p 1 -spi W25Q80BV	        >> $(BATCHFILE)
else 
	echo attachFlash -p 1 -spi W25Q16BV             >> $(BATCHFILE)
endif
	echo assignfiletoattachedflash -p 1 -file $<	>> $(BATCHFILE)
	echo program -p 1 -dataWidth 4 -spionly -erase -loadfpga >> $(BATCHFILE)
	echo exit		>> $(BATCHFILE)
	$(SHELL) -c '$(xil_env) && impact -batch $(BATCHFILE)'
	@rm -f $(BATCHFILE)

load: $(MM_PLATFORM).bit
	echo setmode -bs	>> $(BATCHFILE)
	echo setcable -p auto	>> $(BATCHFILE)
	echo identify		>> $(BATCHFILE)
	echo assignfile -p 1 -file $^ >> $(BATCHFILE)
	echo program -p 1	>> $(BATCHFILE)
	echo exit		>> $(BATCHFILE)
	$(SHELL) -c '$(xil_env) && impact -batch $(BATCHFILE)'
	@rm -f $(BATCHFILE)

erase: $(MM_PLATFORM)
	echo setmode -bs	>> $(BATCHFILE)
	echo setcable -p auto	>> $(BATCHFILE)
	echo identify		>> $(BATCHFILE)
ifeq ($(MM_PLATFORM),MM721)
	echo attachFlash -p 1 -spi W25Q80BV		>> $(BATCHFILE)
else
	echo attachFlash -p 1 -spi W25Q16BV
endif
	echo erase -p 1 -o -spionly			>> $(BATCHFILE)
	echo exit		>> $(BATCHFILE)
	$(SHELL) -c '$(xil_env) && impact -batch $(BATCHFILE)'
	@rm -f $(BATCHFILE)

reflash_ulink2: $(MCU_PLATFORM).axf erase_ulink2
	(while ! (sleep 0.5 && $(LPCXPRESSODIR)/crt_emu_cm_redlink -flash-load-exec $< $(NXP_PARAMETERS)); do : ; done;)

erase_ulink2:
	-(killall -s 9 redlinkserv && sleep 1)
	(while ! (sleep 0.5 && $(LPCXPRESSODIR)/crt_emu_cm_redlink -flash-erase $(NXP_PARAMETERS)); do : ; done;)

