#ifndef __IIC_H__
#define __IIC_H__

#define I2C_DEV		"/dev/i2c-1"

struct i2c_drv {
	char *name;

	int (*i2c_open)(char *dev);
	int (*i2c_close)(void);
	int (*i2c_setslave)(uint8_t addr);
	int (*i2c_write)(unsigned char *wbuf, unsigned int wlen);
	int (*i2c_read)(unsigned char *rbuf, unsigned int rlen);
};

#define DRIVERS_DO(DRIVER_DO)	\
	DRIVER_DO(auc)	\
	DRIVER_DO(rpi)

#define DRIVER_PROTOTYPE(X) struct i2c_drv X##_drv;
DRIVERS_DO(DRIVER_PROTOTYPE)

#endif /* __IIC_H__ */
