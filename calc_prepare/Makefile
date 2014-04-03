#
# Author: Minux
# Author: Xiangfu Liu <xiangfu@openmobilefree.net>
# Bitcoin:	1CanaaniJzgps8EV6Sfmpb7T8RutpaeyFn
#
# This is free and unencumbered software released into the public domain.
# For details see the UNLICENSE file at the root of the source tree.
#

BIN_DIR:=$(shell date +%Y-%m-%d)
GIT_VERSION:=$(shell git rev-parse HEAD | cut -c 1-7)
GIT_STATUS:=$(shell ([ -z "`git status -s -uno`" ] && echo 0) || echo +)

DEPEND	:= $(CPP) $(CFLAGS) -D__OPTIMIZE__ -MM -MG

# ----- Customer ----------------------------------------------------------
INCLUDES   = -I.
LDFLAGS    += 
LDLIBS     += 

SSRCS      = 
CSRCS      = main.c sha2.c
OBJS       := $(addsuffix .o,$(basename $(CSRCS) $(SSRCS)))

.PHONY: all clean distclean load reflash

# C rules
all: main

main: ${OBJS}

%.o: %.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ -c $<
	$(MKDEP)


# Clean rules
clean:
	rm -f $(OBJS) $(OBJS:.o=.d) main

# ----- Dependencies ----------------------------------------------------------
MKDEP =									\
	$(DEPEND) $< |							\
	  sed 								\
	    -e 's|^$(basename $(notdir $<)).o:|$@:|'			\
	    -e '/^\(.*:\)\? */{p;s///;s/ *\\\?$$/ /;s/  */:\n/g;H;}'	\
	    -e '$${g;p;}'						\
	    -e d >$(basename $@).d;					\
	  [ "$${PIPESTATUS[*]}" = "0 0" ] ||				\
	  { rm -f $(basename $@).d; exit 1; }

-include $(OBJS:.o=.d)
