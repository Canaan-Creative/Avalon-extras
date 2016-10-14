JANSSON_CPPFLAGS= -I$(top_builddir)/compat/jansson-2.6/src -I$(top_srcdir)/compat/jansson-2.6/src
USBUTILS_CPPFLAGS = -I$(top_builddir)/compat/libusb-1.0/libusb -I$(top_srcdir)/compat/libusb-1.0/libusb

ACLOCAL_AMFLAGS = -I m4

EXTRA_DIST	= mm.mcs hexdump.c

SUBDIRS		= compat

bin_PROGRAMS	= mm-tools

mm_tools_CPPFLAGS = $(JANSSON_CPPFLAGS) $(USBUTILS_CPPFLAGS)
mm_tools_LDADD	= @JANSSON_LIBS@ @LIBUSB_LIBS@ \
		  @PTHREAD_FLAGS@ @MATH_LIBS@

# common sources
mm_tools_SOURCES = main.c
mm_tools_SOURCES += api.h auc.h crc.h iic.h \
		   auc.c mboot_api.c mm_api.c iic_rpi.c iic_auc.c
if USE_SOFT_CRC
mm_tools_SOURCES += crc16_soft.c
else
mm_tools_SOURCES += crc16.c
endif
