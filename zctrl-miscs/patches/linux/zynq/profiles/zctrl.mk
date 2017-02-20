#
# Copyright (C) 2015 OpenWrt.org
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

define Profile/ZCTRL
	NAME:=Canaan Z Controller
	PACKAGES:= uboot-zynq-zctrl
endef

define Profile/ZCTRL/Description
	Build firmware image for Canaan Z Controller
endef

$(eval $(call Profile,ZCTRL))
