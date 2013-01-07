all:
	gcc -g -Wall -W fake-avalon.c -o fake-avalon
	./fake-avalon || ./fake-avalon /dev/ttyUSB2
