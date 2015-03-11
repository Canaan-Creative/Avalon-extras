#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include "auc.h"

static AUC_HANDLE g_hauc[AUC_DEVCNT];
static uint32_t g_auc_cnts = 0;
static uint8_t g_slaveaddr = 0;

int i2c_open(char *dev)
{
	uint32_t i;

	g_auc_cnts = auc_getcounts();
	if (!g_auc_cnts) {
		printf("i2c_open: No AUC found!\n");
		return 1;
	}

	for (i = 0; i < AUC_DEVCNT; i++)
		g_hauc[i] = NULL;

	for (i = 0; i < g_auc_cnts; i++) {
		g_hauc[i] = auc_open(i);
		if (g_hauc[i]) {
			auc_init(g_hauc[i], I2C_CLK_1M, 9600);
			printf("i2c_open: auc-%d, ver:%s\n", i, auc_version(i));
		} else
			printf("i2c_open: auc-%d init failed!\n", i);
	}
	return 0;
}

int i2c_close()
{
	uint32_t i = 0;

	for (i = 0; i < g_auc_cnts; i++) {
		auc_close(g_hauc[i]);
		g_hauc[i] = NULL;
	}

	return 0;
}

int i2c_setslave(uint8_t addr)
{
	g_slaveaddr = addr;
	return 0;
}

int i2c_write(unsigned char *wbuf, unsigned int wlen)
{
	int ret;
	uint32_t i = 0;

	for (i = 0; i < g_auc_cnts; i++) {
		ret = auc_xfer(g_hauc[i], g_slaveaddr, wbuf, wlen, NULL, 0);
		if (ret)
			printf("i2c_write: auc-%d Write to %x failed!(ret = %d)\n", i, g_slaveaddr, ret);
	}

	return 0;
}

int i2c_read(unsigned char *rbuf, unsigned int rlen)
{
	int ret;
	uint32_t i;

	for (i = 0; i < g_auc_cnts; i++) {
		ret = auc_xfer(g_hauc[i], g_slaveaddr, NULL, 0, rbuf, rlen);
		if (ret != rlen) {
			printf("i2c_read: auc-%d Read from %d failed!(%d-%d)\n", i, g_slaveaddr, ret, rlen);
			return 1;
		}
	}

	return 0;
}

