/*
 * @brief
 *
 * @note
 * Author: Mikeqin Fengling.Qin@gmail.com
 *
 * @par
 * This is free and unencumbered software released into the public domain.
 * For details see the UNLICENSE file at the root of the source tree.
 */

#include <unistd.h>
#include <stdio.h>
#include "gpio.h"
#include "iic.h"

static void i2c_nop(uint32_t times)
{
	uint8_t i;

	for (i = 0; i < times; i++);
		usleep(1);
}

void iic_init(void)
{
	gpio_init_port();
	gpio_setsda_dir(GPIO_DIR_OUT);
	gpio_setscl_dir(GPIO_DIR_OUT);
}

void iic_start(void)
{
	gpio_setsda_val(1);
	gpio_setscl_val(1);
	i2c_nop(1);
	gpio_setsda_val(0);
	i2c_nop(1);
}

void iic_stop(void)
{
	gpio_setsda_val(0);
	gpio_setscl_val(1);
	i2c_nop(1);
	gpio_setsda_val(1);
	i2c_nop(1);
}

void iic_write(uint8_t data)
{
	uint8_t i;

	gpio_setscl_val(0);
	for (i = 0; i < 8; i++) {
		if ((data & 0x80) == 0x80)
			gpio_setsda_val(1);
		else
			gpio_setsda_val(0);

		i2c_nop(1);
		gpio_setscl_val(1);
		i2c_nop(1);
		gpio_setscl_val(0);
		i2c_nop(1);
		data <<= 1;
	}

	gpio_setsda_dir(GPIO_DIR_IN);
	gpio_setsda_val(1);
	i2c_nop(1);
	gpio_setscl_val(1);
	i2c_nop(1);
	gpio_setscl_val(0);
	i2c_nop(1);
	gpio_setsda_dir(GPIO_DIR_OUT);
}

uint8_t iic_read(void)
{
	uint8_t i;
	uint8_t data = 0;

	gpio_setscl_val(0);
	gpio_setsda_val(1);
	gpio_setsda_dir(GPIO_DIR_IN);

	for (i = 0; i < 8; i++) {
		gpio_setscl_val(1);
		i2c_nop(1);
		data <<= 1;
		data |= gpio_getsda_val();
		i2c_nop(1);
		gpio_setscl_val(0);
		i2c_nop(1);
	}

	i2c_nop(1);
	gpio_setscl_val(1);
	i2c_nop(1);
	gpio_setscl_val(0);
	i2c_nop(1);
	gpio_setsda_dir(GPIO_DIR_OUT);

	return data;
}
