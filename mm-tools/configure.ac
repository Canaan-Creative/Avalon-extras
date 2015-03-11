##--##--##--##--##--##--##--##--##--##--##--##--##--##--##--##--##
##--##--##--##--##--##--##--##--##--##--##--##--##--##--##--##--##
m4_define([v_maj], [1])
m4_define([v_min], [0])
m4_define([v_mic], [0])
##--##--##--##--##--##--##--##--##--##--##--##--##--##--##--##--##
m4_define([v_ver], [v_maj.v_min.v_mic])
##--##--##--##--##--##--##--##--##--##--##--##--##--##--##--##--##
##--##--##--##--##--##--##--##--##--##--##--##--##--##--##--##--##

AC_INIT([mm-tools], [v_ver], [Fengling.Qin@gmail.com])

AC_PREREQ(2.59)
AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_SRCDIR([main.c])
AM_INIT_AUTOMAKE([-Wall -Werror foreign subdir-objects])

dnl Check for programs
AC_PROG_CC
LT_INIT([disable-shared])

AC_CONFIG_SUBDIRS([compat/libusb-1.0])
LIBUSB_LIBS="compat/libusb-1.0/libusb/.libs/libusb-1.0.a"
AC_ARG_ENABLE([udev],
	      [AC_HELP_STRING([--disable-udev],[Disable building libusb with udev])],
	      [udev=$enableval]
	      )

if test "x$udev" != xno; then
    LIBUSB_LIBS+=" -ludev"
fi

AC_CONFIG_SUBDIRS([compat/jansson-2.6])
JANSSON_LIBS="compat/jansson-2.6/src/.libs/libjansson.a"
PKG_PROG_PKG_CONFIG()

PTHREAD_LIBS=-lpthread
PTHREAD_FLAGS="-lpthread"
MATH_LIBS="-lm"

AC_SUBST(PTHREAD_FLAGS)
AC_SUBST(PTHREAD_LIBS)
AC_SUBST(LIBUSB_LIBS)
AC_SUBST(JANSSON_LIBS)
AC_SUBST(MATH_LIBS)

iic_rpi="no"

AC_ARG_ENABLE([iic_rpi],
	      [AC_HELP_STRING([--enable-iic-rpi], [Compile support for mm upgrade by Raspberry Pi B(default disabled)])],
	      [iic_rpi=$enableval]
	      )
AM_CONDITIONAL([USE_IIC_RPI], [test x$iic_rpi = xyes])
AM_CONDITIONAL([USE_IIC_AUC], [test x$iic_rpi = xno])

AC_CONFIG_FILES([
	Makefile
	compat/Makefile
	])
AC_OUTPUT

echo
echo
echo
echo "------------------------------------------------------------------------"
echo "$PACKAGE $VERSION"
echo "------------------------------------------------------------------------"
echo
echo
echo "Configuration Options Summary:"
echo

if test "x$iic_rpi" = xyes; then
    echo "  USE_IIC_RPI  :  Enable"
else
    echo "  USE_IIC_AUC  :  Enable"
fi

echo
echo "Compilation............: make (or gmake)"
echo "  CPPFLAGS.............: $CPPFLAGS"
echo "  CFLAGS...............: $CFLAGS"
echo "  LDFLAGS..............: $LDFLAGS $PTHREAD_FLAGS"
echo "  LDADD................: $JANSSON_LIBS $PTHREAD_LIBS $MATH_LIBS $LIBUSB_LIBS"
echo
echo "Installation...........: make install (as root if needed, with 'su' or 'sudo')"
echo "  prefix...............: $prefix"
echo
