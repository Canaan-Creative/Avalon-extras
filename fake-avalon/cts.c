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

#define BAUDRATE B19200
#define MODEMDEVICE "/dev/ttyUSB0"
#define _POSIX_SOURCE 1 /* POSIX compliant source */

int rts(int fd, int rtsEnable)
{
	int flags;

	ioctl(fd, TIOCMGET, &flags);

	printf("Info: Flags before: %x\t RTS: %d\t CTS: %d\n",
	       flags,
	       ((flags & TIOCM_RTS) ? 1 : 0),
	       ((flags & TIOCM_CTS) ? 1 : 0));

	if(rtsEnable!=0)
		flags |= TIOCM_RTS;
	else
		flags &= ~TIOCM_RTS;

	ioctl(fd, TIOCMSET, &flags);

	printf("Info: Flags after: %x\t RTS: %d\t CTS: %d\n",
	       flags,
	       ((flags & TIOCM_RTS) ? 1 : 0),
	       ((flags & TIOCM_CTS) ? 1 : 0));

	return 0;
}

int get_cts(int fd)
{
	int flags;

	ioctl(fd, TIOCMGET, &flags);

	printf("Info: Flags: %x\t RTS: %d\t CTS: %d\n",
	       flags,
	       ((flags & TIOCM_RTS) ? 1 : 0),
	       ((flags & TIOCM_CTS) ? 1 : 0));

	return (flags & TIOCM_CTS) ? 1 : 0;
}

int main(int argc, char *argv[])
{
	struct termios oldtio,newtio;
	uint8_t buf[1024];

	int fd, ret;
	int read_count;

	if (argc < 3) {
		printf("Usage: %s DEVICE high/low/set \t\tVersion:20130110\n", argv[0]);
		return 1;
	}

	fd = open(argv[1], O_RDWR | O_NOCTTY);
	if (fd <0) {
		printf("Usage: %s DEVICE high/low/set \t\tVersion:20130110\n", argv[0]);
		perror(argv[1]);
		return 1;
	}

	tcgetattr(fd,&oldtio); /* save current serial port settings */
	bzero(&newtio, sizeof(newtio)); /* clear struct for new port settings */

	newtio.c_cflag |= BAUDRATE;
	newtio.c_cflag |= CS8;
	newtio.c_cflag |= CREAD;
	newtio.c_cflag |= CLOCAL;
	newtio.c_cflag &= ~(CSIZE | PARENB);
	newtio.c_iflag &= ~(IGNBRK | BRKINT | PARMRK |
			    ISTRIP | INLCR | IGNCR | ICRNL | IXON);
	newtio.c_oflag &= ~OPOST;
	newtio.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);


	newtio.c_cc[VTIME] = 100;
	newtio.c_cc[VMIN] = 0;

	tcflush(fd, TCIFLUSH);
	tcsetattr(fd, TCSANOW, &newtio);

	if (!strcmp(argv[2], "set") && argc == 4) {
		while (1) {
			rts(fd, atoi(argv[3]));
			char b[2] = {'b', 'B'};
			if (write(fd, b, 1) != 1) {
				printf("Error: on write\n");
				goto xout;
			}
			usleep(1000000);
		}
	}

	const char *result = "A";
	int cts;
	cts = get_cts(fd);
	while ((!strcmp(argv[2], "high") && cts != 1) || (!strcmp(argv[2], "low") && cts != 0)) {
		printf("CTS is not what I want. wait another second\n");
		sleep(1);
		cts = get_cts(fd);
	}

	printf("Write [A]\n");
	if (write(fd, result, 1) != 1) {
		printf("Error: on write\n");
		return 1;
	}
	get_cts(fd);

	uint8_t r[2] = {0, 0};
	printf("Read...\n");
	while (read(fd, r, 1) != 1) {
		printf("No data in 10 seconds\n");
	}
	printf(" [0x%02x:%c] \n", r[0], r[0]);
	get_cts(fd);
	printf("Done\n");


xout:
	tcsetattr(fd,TCSANOW,&oldtio);
	close(fd);

	return 0;
}
