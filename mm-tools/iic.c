#include <stdio.h>
#include <stdint.h>
#include <linux/i2c-dev.h>
#include <fcntl.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

static int g_i2cfd;
static uint8_t curslave_addr = 0;

int i2c_open(char *dev)
{
	if ((g_i2cfd = open(dev, O_RDWR)) < 0) {
		printf("Failed to open i2c port\n");
		return 1;
	}
	return 0;
}

int i2c_close()
{
	close(g_i2cfd);
	g_i2cfd = -1;
	return 0;
}

int i2c_setslave(uint8_t addr)
{
	curslave_addr = addr;
	if (ioctl(g_i2cfd, I2C_SLAVE, addr) < 0) {
		printf("Unable to find slave addr %x\n", addr);
		return 1;
	}
	return 0;
}

int i2c_write(unsigned char *wbuf, unsigned int wlen)
{
	int ret;

	ret = write(g_i2cfd, wbuf, wlen);
	if (ret != wlen) {
		printf("Write to %x failed!(%d-%d)\n", curslave_addr, ret, wlen);
		if (ret < 0)
			return -1;

		return 1;
	}

	return 0;
}

int i2c_read(unsigned char *rbuf, unsigned int rlen)
{
	int ret;

	ret = read(g_i2cfd, rbuf, rlen);
	if (ret != rlen) {
		printf("Read from %x failed!(%d-%d)\n", curslave_addr, ret, rlen);
		if (ret < 0)
			return -1;
		return 1;
	}

	return 0;
}

