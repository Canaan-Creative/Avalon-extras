#ifndef __AUC_H__
#define __AUC_H__

#include <stdint.h>
#include <libusb.h>

#define CDC_I2C_PACKET_SZ	    64		/*!< Packet size of each I2C command packet */
#define CDC_I2C_HEADER_SZ	    4		/*!< Size of the header in I2C command packet */
#define CDC_I2C_XFER_HEADER_SZ	    4		/*!< Size of the xfer header in I2C command packet */
#define CDC_I2C_PAYLOAD_SZ          (CDC_I2C_PACKET_SZ-CDC_I2C_HEADER_SZ-CDC_I2C_XFER_HEADER_SZ)

/* CDC_I2C Requests */
#define CDC_I2C_REQ_RESET	    0xa0		/*!< Request to abort and flush all pending requests */
#define CDC_I2C_REQ_INIT_PORT	    0xa1		/*!< Request to initialize the I2C port */
#define CDC_I2C_REQ_DEINIT_PORT     0xa2		/*!< Request to de-initialize the I2C port */
#define CDC_I2C_REQ_DEVICE_WRITE    0xa3		/*!< Request to write data to the I2C port */
#define CDC_I2C_REQ_DEVICE_READ     0xa4		/*!< Request to read data from the I2C port */
#define CDC_I2C_REQ_DEVICE_XFER     0xa5		/*!< Request to write and then read data from the I2C port */
#define CDC_I2C_REQ_DEVICE_INFO     0xa6		/*!< Request to get device information */

/** CDC_I2C responses. The response code below 0x10 should match with I2CM_STATUS codes. */
#define CDC_I2C_RES_OK		    0x00		/*!< Requested Request was executed successfully. */
#define CDC_I2C_RES_ERROR	    0x01		/*!< Unknown error condition. */
#define CDC_I2C_RES_NAK		    0x02		/*!< No device responded for given slave address. */
#define CDC_I2C_RES_BUS_ERROR	    0x03		/*!< I2C bus error */
#define CDC_I2C_RES_SLAVE_NAK	    0x04		/*!< NAK received after SLA+W or SLA+R */
#define CDC_I2C_RES_ARBLOST	    0x05		/*!< Arbitration lost */

#define CDC_I2C_RES_TIMEOUT	    0x10		/*!< Transaction timed out. */
#define CDC_I2C_RES_INVALID_CMD     0x11		/*!< Invalid CDC_I2C Request or Request not supported in this version. */
#define CDC_I2C_RES_INVALID_PARAM   0x12		/*!< Invalid parameters are provided for the given Request. */
#define CDC_I2C_RES_PARTIAL_DATA    0x13		/*!< Partial transfer completed. */

#define AUC_VID	0x29f1
#define AUC_PID	0x33f2
#define AUC_VERLEN	12
#define AUC_EP_IN	0x81
#define AUC_EP_OUT	0x1
#define AUC_DEVCNT	100
#define AUC_TIMEOUT_MS	200

struct cdc_i2c_header {
	uint8_t length;					/*!< Length of the packet (include header and body) */
	uint8_t reserved[2];				/*!< Reserved */
	uint8_t type;					/*!< Request or Response type */
};

enum i2c_clockrate {
	I2C_CLK_100K = 100000,
	I2C_CLK_400K = 400000,
	I2C_CLK_1M = 1000000,
};

typedef void *AUC_HANDLE;

struct auc_ctx {
	libusb_device *auc_devlist[AUC_DEVCNT];
	AUC_HANDLE handle[AUC_DEVCNT];
	char auc_ver[AUC_DEVCNT][AUC_VERLEN + 1];
	uint32_t auc_cnt;
};


uint32_t auc_getcounts(void);
AUC_HANDLE auc_open(uint32_t index);
const char *auc_version(uint32_t index);
int32_t auc_init(AUC_HANDLE handle, uint32_t clk_rate, uint32_t xfer_delay);
int32_t auc_close(AUC_HANDLE handle);
int32_t auc_reset(AUC_HANDLE handle);
int32_t auc_xfer(AUC_HANDLE handle, uint8_t slaveAddr, uint8_t *wbuf, uint32_t wlen, uint8_t *rbuf, uint32_t rlen);

#endif /* __AUC_H__ */
