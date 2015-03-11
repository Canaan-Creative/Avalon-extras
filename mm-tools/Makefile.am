JANSSON_CPPFLAGS= -I$(top_builddir)/compat/jansson-2.6/src -I$(top_srcdir)/compat/jansson-2.6/src
USBUTILS_CPPFLAGS = -I$(top_builddir)/compat/libusb-1.0/libusb -I$(top_srcdir)/compat/libusb-1.0/libusb

EXTRA_DIST	= mm.mcs hexdump.c

SUBDIRS		= compat

bin_PROGRAMS	= mm-tools

mm_tools_CPPFLAGS = $(JANSSON_CPPFLAGS) $(USBUTILS_CPPFLAGS)
mm_tools_LDADD	= @JANSSON_LIBS@ @LIBUSB_LIBS@ \
		  @PTHREAD_FLAGS@ @MATH_LIBS@

# common sources
mm_tools_SOURCES = main.c
mm_tools_SOURCES += api.h auc.h crc.h iic.h \
		   auc.c crc16.c mboot_api.c mm_api.c

if USE_IIC_RPI
mm_tools_SOURCES += iic_rpi.c
endif

if USE_IIC_AUC
mm_tools_SOURCES += iic_auc.c
endif
