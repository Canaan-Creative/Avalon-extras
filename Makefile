all:
	gcc cts.c -o cts-test-x86
	mips-openwrt-linux-gcc cts.c -o cts-test-703n
	gcc -g -Wall -W fake-avalon.c -o fake-avalon

fake-avalon:
	./fake-avalon || ./fake-avalon /dev/ttyUSB2

clean:
	rm -f cts-test-x86
	rm -f cts-test-703n
	rm -f fake-avalon
