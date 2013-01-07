#include <sys/time.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <signal.h>
#include <termios.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define BAUDRATE B115200
#define MODEMDEVICE "/dev/ttyUSB1"
#define _POSIX_SOURCE 1 /* POSIX compliant source */

#define hex_print(p) printf("%s\n", p)

static char nibble[] = {
	'0', '1', '2', '3', '4', '5', '6', '7',
	'8', '9', 'a', 'b', 'c', 'd', 'e', 'f' };

#define BYTES_PER_LINE 0x10

void hexdump(const uint8_t *p, unsigned int len)
{
	unsigned int i, addr;
	unsigned int wordlen = sizeof(void*);
	unsigned char v, line[BYTES_PER_LINE * 5];

	for (addr = 0; addr < len; addr += BYTES_PER_LINE) {
		/* clear line */
		for (i = 0; i < sizeof(line); i++) {
			if (i == wordlen * 2 + 52 ||
			    i == wordlen * 2 + 69) {
			    	line[i] = '|';
				continue;
			}

			if (i == wordlen * 2 + 70) {
				line[i] = '\0';
				continue;
			}

			line[i] = ' ';
		}

		/* print address */
		for (i = 0; i < wordlen * 2; i++) {
			v = addr >> ((wordlen * 2 - i - 1) * 4);
			line[i] = nibble[v & 0xf];
		}

		/* dump content */
		for (i = 0; i < BYTES_PER_LINE; i++) {
			int pos = (wordlen * 2) + 3 + (i / 8);

			if (addr + i >= len)
				break;

			v = p[addr + i];
			line[pos + (i * 3) + 0] = nibble[v >> 4];
			line[pos + (i * 3) + 1] = nibble[v & 0xf];

			/* character printable? */
			line[(wordlen * 2) + 53 + i] =
				(v >= ' ' && v <= '~') ? v : '.';
		}

		hex_print(line);
	}
}


/* Does the reverse of bin2hex but does not allocate any ram */
int hex2bin(unsigned char *p, const char *hexstr, size_t len)
{
	int ret = 0;

	while (*hexstr && len) {
		char hex_byte[4];
		unsigned int v;

		if (!hexstr[1]) {
			return ret;
		}

		memset(hex_byte, 0, 4);
		hex_byte[0] = hexstr[0];
		hex_byte[1] = hexstr[1];

		if (sscanf(hex_byte, "%x", &v) != 1) {
			printf("hex2bin sscanf '%s' failed", hex_byte);
			return ret;
		}

		*p = (unsigned char) v;

		p++;
		hexstr += 2;
		len--;
	}

	if (len == 0 && *hexstr == 0)
		ret = 1;
	return ret;
}

int rts(int fd, int rtsEnable)
{
	int flags;

	ioctl(fd, TIOCMGET, &flags);
	/* fprintf(stderr, "Flags before %x\t", flags); */

	if(rtsEnable!=0)
		flags |= TIOCM_RTS;
	else
		flags &= ~TIOCM_RTS;

	ioctl(fd, TIOCMSET, &flags);
	/* fprintf(stderr, "after: %x\n", flags); */

	return 0;
}

int main(int argc, char *argv[])
{
	struct termios oldtio,newtio;
	uint8_t buf[1024];

	int fd, ret;
	int read_count;
	char *path;

	if (argc == 1)
		path = MODEMDEVICE;
	else
		path = argv[1];

	fd = open(path, O_RDWR | O_CLOEXEC | O_NOCTTY );
	if (fd <0) {perror(path); exit(-1); }

	tcgetattr(fd,&oldtio); /* save current serial port settings */
	bzero(&newtio, sizeof(newtio)); /* clear struct for new port settings */

	newtio.c_cflag |= BAUDRATE;
	newtio.c_cflag |= CS8;
	newtio.c_cflag |= CREAD;
	newtio.c_cflag |= CRTSCTS;
	newtio.c_cflag |= CLOCAL;
	newtio.c_cflag &= ~(CSIZE | PARENB);
	newtio.c_iflag &= ~(IGNBRK | BRKINT | PARMRK |
			    ISTRIP | INLCR | IGNCR | ICRNL | IXON);
	newtio.c_oflag &= ~OPOST;
	newtio.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);


	newtio.c_cc[VTIME] = 20;
	newtio.c_cc[VMIN] = 0;

	tcflush(fd, TCIFLUSH);
	tcsetattr(fd, TCSANOW, &newtio);


#include "data.test.c"
	char reset[56] = {
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x20, 0x13, 0x01, 0x07,
		0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
	};

	int write_i;
	uint8_t result[56];
	int finish_read = 20;
	uint8_t *p = buf;

	read_count = 56;

	memset(result, 0, 56);
	while (1) {
		if (read_count == 0) {
			p = buf;
			read_count = 56;

			printf("Info: (%d) I got 56 chars: ---------------\n", finish_read);
			hexdump(buf, 56);
			printf("------------------------------------------\n");

			if (buf[0] == 0xA1) {
				printf("This is a BIG RESET\n");
				if (write(fd, reset, 56) != 56) {
					printf("Error: on write\n");
					break;
				}
				continue;
			}
			finish_read--;
		}

		if (finish_read == 0) {
			rts(fd, 0);
			sleep(1);
			for (write_i = 0; write_i < 20; write_i++) {
				hex2bin(result, data_test[write_i], 56);
				if (write(fd, result, 56) != 56) {
					printf("Error: on write\n");
					break;
				}
			}

			finish_read = 20;
			continue;
		}

		rts(fd, 1);
		ret = read(fd, p, 1);
		if (ret < 0) {
			printf("Error: on read\n");
			break;
		}

		if (ret == 0) {
			printf("Info: read nothing in X second, ret: %d\n", ret);
			continue;
		}

		if (ret > 0) {
			p += ret;
			read_count -= ret;
			/* printf("Info: (%d) read: %d\n", i++, ret); */
			continue;
		}
	}

	tcsetattr(fd,TCSANOW,&oldtio);
	close(fd);

	return 0;
}
