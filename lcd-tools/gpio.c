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

#include <stdio.h>
#include <string.h>
#include "gpio.h"

#define SCL_PIN	27
#define SDA_PIN	17
#define PIN_BUFLEN	3
#define PATH_BUFLEN	40

static int gpio_export(int pin)
{
	char buffer[PIN_BUFLEN];
	FILE *fp = NULL;

	fp = fopen("/sys/class/gpio/export", "r+");
	if (!fp) {
		printf("Failed to open export %d!\n", pin);
		return 1;
	}

	snprintf(buffer, PIN_BUFLEN, "%d", pin);
	if (fwrite(buffer, 1, strlen(buffer), fp) != strlen(buffer)) {
		printf("Failed to write export %d!\n", pin);
		fclose(fp);
		return 1;
	}

	fclose(fp);
	return 0;
}

static int gpio_unexport(int pin)
{
	char buffer[PIN_BUFLEN];
	FILE *fp = NULL;

	fp = fopen("/sys/class/gpio/unexport", "r+");
	if (!fp) {
		printf("Failed to open unexport %d!\n", pin);
		return 1;
	}

	snprintf(buffer, PIN_BUFLEN, "%d", pin);
	if (fwrite(buffer, 1, strlen(buffer), fp) != strlen(buffer)) {
		printf("Failed to wrtie unexport %d!\n", pin);
		fclose(fp);
		return 1;
	}

	fclose(fp);
	return 0;
}

static int gpio_dir(int pin, int dir)
{
	char path[PATH_BUFLEN];
	FILE *fp = NULL;

	snprintf(path, PATH_BUFLEN, "/sys/class/gpio/gpio%d/direction", pin);
	fp = fopen(path, "r+");
	if (!fp) {
		printf("Failed to open gpio direction %d!\n", pin);
		return 1;
	}

	if (dir == GPIO_DIR_IN) {
		if (fwrite("in", 1, 2, fp) != 2) {
			printf("Failed to set direction %d!\n", pin);
			fclose(fp);
			return 1;
		}
	}

	if (dir == GPIO_DIR_OUT) {
		if (fwrite("out", 1, 3, fp) != 3) {
			printf("Failed to set direction %d!\n", pin);
			fclose(fp);
			return 1;
		}
	}

	fclose(fp);
	return 0;
}

static int gpio_read(int pin)
{
	char path[PATH_BUFLEN];
	char val[2];
	FILE *fp = NULL;

	snprintf(path, PATH_BUFLEN, "/sys/class/gpio/gpio%d/value", pin);
	fp = fopen(path, "r");
	if (!fp) {
		printf("Failed to open gpio value %d!\n", pin);
		return 1;
	}

	if (fread(val, 1, 1, fp) != 1) {
		printf("Failed to read value %d!\n", pin);
		fclose(fp);
		return 1;
	}
	val[1] = '\0';

	fclose(fp);
	return val[0] - '0';
}

static int gpio_write(int pin, int val)
{
	char path[PATH_BUFLEN];
	char ch;
	FILE *fp = NULL;

	snprintf(path, PATH_BUFLEN, "/sys/class/gpio/gpio%d/value", pin);
	fp = fopen(path, "r+");
	if (!fp) {
		printf("Failed to open gpio value %d!\n", pin);
		return 1;
	}

	ch = '0' + (val & 1);
	if (fwrite(&ch, 1, 1, fp) != 1) {
		printf("Failed to write value %d!\n", pin);
		fclose(fp);
		return 1;
	}

	fclose(fp);
	return 0;
}

int gpio_init_port(void)
{
	if (!gpio_export(SCL_PIN) && !gpio_export(SDA_PIN))
		return 0;

	return 1;
}

int gpio_setsda_dir(int dir)
{
	return gpio_dir(SDA_PIN, dir);
}

int gpio_setsda_val(int val)
{
	return gpio_write(SDA_PIN, val);
}

int gpio_getsda_val(void)
{
	return gpio_read(SDA_PIN);
}

int gpio_setscl_dir(int dir)
{
	return gpio_dir(SCL_PIN, dir);
}

int gpio_setscl_val(int val)
{
	return gpio_write(SCL_PIN, val);
}

int gpio_deinit_port(void)
{
	if (!gpio_unexport(SCL_PIN) && !gpio_unexport(SDA_PIN))
		return 0;

	return 1;
}
