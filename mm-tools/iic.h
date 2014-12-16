#ifndef __IIC_H__
#define __IIC_H__

#define I2C_DEV		"/dev/i2c-1"

int i2c_open(char *dev);
int i2c_close();
int i2c_setslave(uint8_t addr);
int i2c_write(unsigned char *wbuf, unsigned int wlen);
int i2c_read(unsigned char *rbuf, unsigned int rlen);

#endif /* __IIC_H__ */
