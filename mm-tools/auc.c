#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "auc.h"

static struct auc_ctx auc_devctx;
static uint8_t g_auc_pkg[CDC_I2C_PACKET_SZ];

struct cdc_i2c_configparams {
	uint8_t clk_rate[4];	/* LSB */
	uint8_t xfer_delay[4];  /* LSB */
};

struct cdc_i2c_xferparams {
	uint8_t txLength;
	uint8_t rxLength;
	uint8_t reserved;
	uint8_t slaveAddr;
	uint8_t data[CDC_I2C_PAYLOAD_SZ];
};

uint32_t auc_getcounts(void)
{
	static int32_t usb_init = 0;
	struct libusb_device **devs = NULL;
	struct libusb_device_descriptor info;
	uint32_t count, i;

	if (!usb_init) {
		if (libusb_init(NULL) < 0) {
			printf("libusb_init failed!\n");
			return 1;
		}
		usb_init = 1;
	} else {
		if (devs) {
			libusb_free_device_list(devs, 1);
			devs = NULL;
		}
		for (i = 0; i < auc_devctx.auc_cnt; i++)
			auc_devctx.auc_devlist[i] = NULL;
		auc_devctx.auc_cnt = 0;
	}

	count = libusb_get_device_list(NULL, &devs);
	if (count <= 0) {
		printf("libusb_get_device_list get NULL\n");
		return 0;
	}

	for (i = 0; i < count; i++) {
		libusb_get_device_descriptor(devs[i], &info);
		if ((info.idVendor == AUC_VID) && (info.idProduct == AUC_PID)) {
			auc_devctx.auc_devlist[auc_devctx.auc_cnt] = devs[i];
			auc_devctx.auc_cnt++;
		}
	}

	return auc_devctx.auc_cnt;
}

AUC_HANDLE auc_open(uint32_t index)
{
	libusb_device_handle *handle;

	if (index > auc_devctx.auc_cnt) {
		printf("auc_open index > auc_devctx.auc_cnt\n");
		return NULL;
	}

	if (libusb_open(auc_devctx.auc_devlist[index], &handle)) {
		printf("auc_open libusb_open failed!\n");
		return NULL;
	}

	auc_devctx.handle[index] = handle;
	return (AUC_HANDLE)handle;
}

/* Call it after auc_init */
const char *auc_version(uint32_t index)
{
	if (index > auc_devctx.auc_cnt) {
		printf("auc_version index > auc_devctx.auc_cnt\n");
		return NULL;
	}

	return auc_devctx.auc_ver[index];
}

static int32_t usb_transfer(AUC_HANDLE handle, uint8_t *wbuf, uint32_t wlen, uint8_t *rbuf, uint32_t rlen)
{
	int32_t transfered;

	libusb_device_handle *dev_handle = (libusb_device_handle*)handle;
#ifdef DEBUG_VERBOSE
	printf("usb_transfer W\n");
	hexdump(wbuf, wlen);
#endif
	if (wlen && libusb_bulk_transfer(dev_handle,
				AUC_EP_OUT,
				wbuf,
				wlen,
				&transfered,
				AUC_TIMEOUT_MS)) {
		printf("usb_transfer AUC_EP_OUT failed!\n");
		return 1;
	}

	if (rlen && libusb_bulk_transfer(dev_handle,
				AUC_EP_IN,
				rbuf,
				rlen,
				&transfered,
				AUC_TIMEOUT_MS)) {
		printf("usb_transfer AUC_EP_IN failed!\n");
		return 1;
	}
#ifdef DEBUG_VERBOSE
	printf("usb_transfer R\n");
	hexdump(rbuf, rlen);
#endif

	return 0;
}

static uint32_t auc_pkg_init(uint8_t type, uint8_t *data, uint32_t len)
{
	struct cdc_i2c_header *header = (struct cdc_i2c_header*)g_auc_pkg;

	header->length = sizeof(struct cdc_i2c_header) + len;
	header->reserved[0] = 0;
	header->reserved[1] = 0;
	header->type = type;

	if (len)
		memcpy(g_auc_pkg + sizeof(struct cdc_i2c_header), data, len);

	return (uint32_t)header->length;
}

int32_t auc_init(AUC_HANDLE handle, uint32_t clk_rate, uint32_t xfer_delay)
{
	struct cdc_i2c_configparams params;
	uint8_t buf[CDC_I2C_PACKET_SZ];
	struct cdc_i2c_header *pheader = (struct cdc_i2c_header*)buf;
	uint32_t i, count;

	params.clk_rate[0] = clk_rate & 0xff;
	params.clk_rate[1] = (clk_rate >> 8) & 0xff;
	params.clk_rate[2] = (clk_rate >> 16) & 0xff;
	params.clk_rate[3] = (clk_rate >> 24) & 0xff;
	params.xfer_delay[0] = xfer_delay & 0xff;
	params.xfer_delay[1] = (xfer_delay >> 8) & 0xff;
	params.xfer_delay[2] = (xfer_delay >> 16) & 0xff;
	params.xfer_delay[3] = (xfer_delay >> 24) & 0xff;

	memset(buf, 0, CDC_I2C_PACKET_SZ);
	while (!usb_transfer(handle, NULL, 0, buf, CDC_I2C_PACKET_SZ));
	count = auc_pkg_init(CDC_I2C_REQ_INIT_PORT, (uint8_t*)&params, sizeof(params));
	if (usb_transfer(handle, g_auc_pkg, count, buf, CDC_I2C_PACKET_SZ)) {
		printf("auc_init usb_transfer failed!\n");
		return 1;
	}

	for (i = 0; i < AUC_DEVCNT; i++) {
		if (handle == auc_devctx.handle[i])
			break;
	}

	if (i >= AUC_DEVCNT) {
		printf("auc_init i(%d) > AUC_DEVCNT", i);
		return 1;
	}

	if (pheader->length > CDC_I2C_HEADER_SZ) {
		memset(auc_devctx.auc_ver[i], 0, AUC_VERLEN+1);
		memcpy(auc_devctx.auc_ver[i], buf + CDC_I2C_HEADER_SZ, AUC_VERLEN);
		auc_devctx.auc_ver[i][AUC_VERLEN] = '\0';
	} else {
		printf("auc_init pheader->length = %d\n", pheader->length);
		return 1;
	}

	return 0;
}

int32_t auc_close(AUC_HANDLE handle)
{
	uint32_t i;

	for (i = 0; i < AUC_DEVCNT; i++) {
		if (handle == auc_devctx.handle[i])
			break;
	}

	if (i < AUC_DEVCNT)
		auc_devctx.handle[i] = NULL;
	else
		printf("auc_close i(%d) >= AUC_DEVCNT\n", i);

	libusb_close((libusb_device_handle*)handle);
	return 0;
}

int32_t auc_reset(AUC_HANDLE handle)
{
	uint32_t count;
	uint8_t buf[CDC_I2C_HEADER_SZ];

	memset(buf, 0, CDC_I2C_HEADER_SZ);
	count = auc_pkg_init(CDC_I2C_REQ_RESET, NULL, 0);
	if (usb_transfer(handle, g_auc_pkg, count, buf, CDC_I2C_HEADER_SZ)) {
		printf("auc_reset usb_transfer failed!\n");
		return 1;
	}

	return 0;
}

int32_t auc_xfer(AUC_HANDLE handle, uint8_t slaveAddr, uint8_t *wbuf, uint32_t wlen, uint8_t *rbuf, uint32_t rlen)
{
	struct cdc_i2c_xferparams params;
	uint8_t buf[CDC_I2C_PACKET_SZ];
	struct cdc_i2c_header *pheader = (struct cdc_i2c_header *)buf;
	int32_t count;

	while ((wlen > 0) || (rlen > 0)) {
		memset(&params, 0, sizeof(params));

		if (wlen >= CDC_I2C_PAYLOAD_SZ) {
			params.txLength = CDC_I2C_PAYLOAD_SZ;
			wlen -= CDC_I2C_PAYLOAD_SZ;
		} else {
			params.txLength = wlen;
			wlen = 0;
		}

		if (rlen >= (CDC_I2C_PACKET_SZ - CDC_I2C_HEADER_SZ)) {
			params.rxLength = (CDC_I2C_PACKET_SZ - CDC_I2C_HEADER_SZ);
			rlen -= (CDC_I2C_PACKET_SZ - CDC_I2C_HEADER_SZ);
		} else {
			params.rxLength = rlen;
			rlen = 0;
		}
		params.reserved = 0;
		params.slaveAddr = slaveAddr;
		if (params.txLength)
			memcpy(params.data, wbuf, params.txLength);

		memset(buf, 0, CDC_I2C_PACKET_SZ);
		count = auc_pkg_init(CDC_I2C_REQ_DEVICE_XFER, (uint8_t*)&params, params.txLength + sizeof(struct cdc_i2c_header));
		if (usb_transfer(handle, g_auc_pkg, count, buf, CDC_I2C_PACKET_SZ)) {
			printf("auc_xfer usb_transfer failed!\n");
			return 0;
		}

		if (pheader->length > CDC_I2C_HEADER_SZ)
			memcpy(rbuf, buf + CDC_I2C_HEADER_SZ, pheader->length - CDC_I2C_HEADER_SZ);
#ifdef DEBUG_VERBOSE
		else {
			printf("auc_xfer pheader->length = %d\n", pheader->length);
		}
#endif
		wbuf += CDC_I2C_PAYLOAD_SZ;
		rbuf += (CDC_I2C_PACKET_SZ - CDC_I2C_HEADER_SZ);
	}

	return pheader->length - CDC_I2C_HEADER_SZ;
}

