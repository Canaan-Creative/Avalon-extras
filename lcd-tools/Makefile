PROG=lcd-tools
SRCS=gpio.c iic.c lcd.c main.c
OBJS=$(patsubst %.c, %.o, $(SRCS))
CFLAGS = -g -O2 -Wall

all:$(OBJS)
	$(CC) $(OBJS) -o $(PROG)

clean:
	rm -rf $(OBJS) $(PROG)
