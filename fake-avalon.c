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

	if(rtsEnable!=0)
		flags |= TIOCM_RTS;
	else
		flags &= ~TIOCM_RTS;

	ioctl(fd, TIOCMSET, &flags);

	return 0;
}

int get_rts(int fd)
{
	int flags;

	ioctl(fd, TIOCMGET, &flags);

	printf("Info: Flags: %x\t RTS: %d\t CTS: %d\n",
	       flags,
	       ((flags & TIOCM_RTS) ? 1 : 0),
	       ((flags & TIOCM_CTS) ? 1 : 0));

	return (flags & TIOCM_RTS) ? 1 : 0;
}

#define AVA_BUFFER_FULL 0
#define AVA_BUFFER_EMPTY 1
#define AVA_TASK_SIZE 56
#define AVA_RESULT_SIZE 56
#define AVALON_GET_WORK_COUNT 24

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
	char reset[AVA_RESULT_SIZE] = {
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
		0x00, 0x00, 0x00, 0x00, 0x20, 0x13, 0x01, 0x07,
		0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
	};

	uint8_t result[AVA_RESULT_SIZE];
	int finish_read = AVALON_GET_WORK_COUNT;
	uint8_t *p = buf;
	int write_i = 0;

	read_count = AVA_TASK_SIZE;

	memset(result, 0, AVA_RESULT_SIZE);

	rts(fd, AVA_BUFFER_EMPTY);
	while (1) {
		if (!read_count) {
			p = buf;
			read_count = AVA_TASK_SIZE;

			printf("Info: (%d) I got %d chars: ---------------\n", finish_read, AVA_TASK_SIZE);
			hexdump(buf, AVA_TASK_SIZE);

			if (buf[0] == 0xA1) {
				printf("Info: This is a BIG RESET\n");
				tcflush(fd, TCOFLUSH);
				if (write(fd, reset, AVA_RESULT_SIZE) != AVA_RESULT_SIZE) {
					printf("Error: on write\n");
					break;
				}
				finish_read = AVALON_GET_WORK_COUNT * 2;
				continue;
			}
			finish_read--;
		}

		if (!finish_read) {
			rts(fd, AVA_BUFFER_FULL);
			sleep(2);
			printf("Info: send back the results, rts: %d\n", get_rts(fd));

			for (; write_i < WORKS; write_i++) {
				hex2bin(result, data_test[write_i], AVA_RESULT_SIZE);
				if (write(fd, result, AVA_RESULT_SIZE) != AVA_RESULT_SIZE) {
					printf("Error: on write\n");
					break;
				}
				if (write_i >= WORKS)
					write_i = 0;
			}

			finish_read = AVALON_GET_WORK_COUNT;
		}

		rts(fd, AVA_BUFFER_EMPTY);
		ret = read(fd, p, 1);
		if (ret < 0) {
			printf("Error: on read\n");
			break;
		}

		if (ret == 0) {
			printf("Info: read nothing in X second, ret: %d, rts: %d\n", ret, get_rts(fd));
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
