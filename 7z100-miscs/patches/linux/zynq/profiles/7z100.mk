#
# Copyright (C) 2015 OpenWrt.org
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

define Profile/7Z100
	NAME:=Canaan 7Z100
	PACKAGES:= uboot-zynq-7z100
endef

define Profile/7Z100/Description
	Build firmware image for Canaan 7Z100
endef

$(eval $(call Profile,7Z100))
