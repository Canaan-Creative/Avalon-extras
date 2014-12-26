TARGET = mm-tools
SRC = iic.c crc16.c auc.c mboot_api.c mm_api.c main.c
OBJS = $(SRC:.c=.o)

CFLAGS += -Wall

all: $(TARGET)

$(TARGET):$(OBJS)
	$(CC) $^ -o $@

%.o:%.c
	$(CC) -c $< -o $@ $(CFLAGS)

main.c: iic.c crc16.c hexdump.c auc.c mboot_api.c mm_api.c

clean:
	@rm -f $(DENPENDS) $(OBJS) $(TARGET)

download:
	wget http://downloads.canaan-creative.com/software/avalon4/mm/latest/mm-no-mboot/mm.mcs -O ./mm.mcs
