TARGET = mm-tools
SRC = iic.c crc16.c auc.c mboot_api.c mm_api.c main.c
OBJS = $(SRC:.c=.o)

INCLUDE += `pkg-config --cflags libusb-1.0`
CFLAGS += -Wall
LDFLAGS += `pkg-config --libs libusb-1.0`

all: $(TARGET)

$(TARGET):$(OBJS)
	$(CC) $^ -o $@ $(LDFLAGS)

%.o:%.c
	$(CC) -c $< -o $@ $(INCLUDE) $(CFLAGS)

main.c: iic.c crc16.c hexdump.c auc.c mboot_api.c mm_api.c

clean:
	@rm -f $(DENPENDS) $(OBJS) $(TARGET)

download:
	wget http://downloads.canaan-creative.com/software/avalon4/mm/latest/mm-no-mboot/mm.mcs -O ./mm.mcs
