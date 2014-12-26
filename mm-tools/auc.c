#include <stddef.h>
#include "auc.h"

uint32_t auc_getcounts(void)
{
	return 0;
}

AUC_HANDLE auc_open(uint32_t index)
{
	return NULL;
}

const char *auc_version(AUC_HANDLE handle)
{
	return NULL;
}

int auc_init(AUC_HANDLE handle, struct i2c_config *config)
{
	return 1;
}

int auc_close(AUC_HANDLE handle)
{
	return 1;
}

int auc_reset(AUC_HANDLE handle)
{
	return 1;
}

int auc_write(AUC_HANDLE handle, uint8_t slaveAddr, unsigned char *wbuf, unsigned int wlen)
{
	return 1;
}

int auc_read(AUC_HANDLE handle, uint8_t slaveAddr, unsigned char *rbuf, unsigned int rlen)
{
	return 1;
}

int auc_xfer(AUC_HANDLE handle, uint8_t slaveAddr, unsigned char *wbuf, unsigned int wlen, unsigned char *rbuf, unsigned rlen)
{
	return 1;
}

