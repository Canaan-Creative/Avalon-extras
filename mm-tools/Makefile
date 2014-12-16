TARGET = mmupgrade
SRC = iic.c crc16.c main.c
OBJS = $(SRC:.c=.o)

CFLAGS += -Wall

all: $(TARGET) 

$(TARGET):$(OBJS)
	gcc $^ -o $@

%.o:%.c
	gcc -c $< -o $@ $(CFLAGS)

main.c: iic.c crc16.c hexdump.c

clean:
	@rm -f $(DENPENDS) $(OBJS) $(TARGET)

