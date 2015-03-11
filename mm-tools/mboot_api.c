#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include "hexdump.c"
#include "crc.h"
#include "iic.h"

#define MCS1_INFO_ADDR_BASE 0xfff80
#define MCS1_INFO_LEN 16 //bytes
#define MCS1_ADDR_BASE 0x80000
#define SPI_FLASH_PAGE 256 //byte
#define CMD_LEN 4
#define IIC_SLAVE_CTL 0x40
#define IIC_SLAVE_DAT 0x41
#define CS_ENABLE 0
#define CS_DISABLE 1
#define IIC2SPI_DISABLE 3

static int gmcs1_len;

static void sleep_ms(unsigned int ms)
{
    usleep(ms * 1000);
}

static void enable_download(void)
{
	unsigned char buf[1];

	i2c_setslave(IIC_SLAVE_CTL);
	/* enable download */
	buf[0] = 0x2;
	i2c_write(buf, 1);
	i2c_setslave(IIC_SLAVE_DAT);
}

static void set_cs(unsigned char dat)
{
	unsigned char buf[1];

	i2c_setslave(IIC_SLAVE_CTL);
	/* set cs */
	buf[0] = dat;
	i2c_write(buf, 1);
	i2c_setslave(IIC_SLAVE_DAT);
}

static void set_reboot(void)
{
	unsigned char buf[1];

	i2c_setslave(IIC_SLAVE_CTL);
	buf[0] = 4;
	i2c_write(buf, 1);
}

static void set_mosi_dat(unsigned char *buf, unsigned int len)
{
	i2c_setslave(IIC_SLAVE_DAT);
	i2c_write(buf, len);
}

static void flash_prog_en(void)
{
	unsigned char buf_cmd[1];

	set_cs(CS_ENABLE);
	buf_cmd[0] = 0x06;
	set_mosi_dat(buf_cmd, 1);
	set_cs(CS_DISABLE);
	sleep_ms(3);
}

static void flash_earse(void)
{
	unsigned char buf[4];
	unsigned int addr = MCS1_ADDR_BASE;
	int i;

	buf[0] = 0xd8;
	for (i = 0; i < 8; i++) {
		flash_prog_en();
		set_cs(CS_ENABLE);
		buf[1] = ((addr >> 16) & 0xff);
		buf[2] = ((addr >> 8) & 0xff);
		buf[3] = (addr & 0xff);

		set_mosi_dat(buf, 4);
		set_cs(CS_DISABLE);
		addr += 0x10000;
		sleep_ms(1000);
		printf("+");
		fflush(stdout);
	}
	printf("\n");
}

static void flash_prog_page(unsigned char *buf, unsigned int addr, unsigned int len)
{
	unsigned char buf_cmd[4];

	flash_prog_en();
	set_cs(CS_ENABLE);
	buf_cmd[0] = 0x02;
	buf_cmd[1] = ((addr >> 16) & 0xff);
	buf_cmd[2] = ((addr >> 8) & 0xff);
	buf_cmd[3] = (addr & 0xff);
	set_mosi_dat(buf_cmd, 4);
	set_mosi_dat(buf, len);
	set_cs(CS_DISABLE);
	sleep_ms(3);
}

static void flash_prog_info(unsigned short crc, unsigned int len)
{
	unsigned char mcs1_info[16];

        mcs1_info[0] = 0x00;
        mcs1_info[1] = 0x01;
        mcs1_info[2] = 0x02;
        mcs1_info[3] = 0x03;

        /*mcs1 crc*/
        mcs1_info[4] = crc >> 8;
        mcs1_info[5] = crc;

        /*mcs1 len = {[6],[7],[8],[9]}*/
        mcs1_info[6] = 0x00;
        mcs1_info[7] = ((len >> 16) & 0xff);
        mcs1_info[8] = ((len >> 8) & 0xff);
        mcs1_info[9] =  (len & 0xff);

        mcs1_info[10] = 0x00;
        mcs1_info[11] = 0x00;
        mcs1_info[12] = 0x00;
        mcs1_info[13] = 0x00;

        mcs1_info[14] = 0x00;
        mcs1_info[15] = 0x00;
	flash_prog_page(mcs1_info, MCS1_INFO_ADDR_BASE, 16);
}

static char char2byte(char char0, char char1)
{
	if (char0 >= 'A' && char0 <= 'F')
		char0 = char0 - 'A' + 10;
	else
		char0 = char0 - '0';

	if (char1 >= 'A' && char1 <= 'F')
		char1 = char1 - 'A' + 10;
	else
		char1 = char1 - '0';

	return (char0 << 4) | char1;
}

static int mboot_mcs_file(void)
{
	int i, byte_num, mm_flg = 0, mm_info = 0;
	unsigned char tmp[1000];
	unsigned char data;
	FILE *mboot_mcs_fp;
	FILE *mboot_mcs_fp_new;

	gmcs1_len = 0;
	mboot_mcs_fp = fopen("./mm.mcs", "rt");
	if (mboot_mcs_fp == NULL) {
	    printf("open mm.mcs error!\n");
	    exit(1);
	} else
	    printf("open mm.mcs success!\n");

	mboot_mcs_fp_new = fopen("./mm_new.mcs", "wb");
	if (mboot_mcs_fp_new == NULL) {
	    printf("open mm_new.mcs error!\n");
	    exit(1);
	} else
	    printf("open mm_new.mcs success!\n");

	while (1) {
		i = 0;
		while (1) {
			tmp[i] = fgetc(mboot_mcs_fp);
			if (tmp[i] == '\n')
				break;
			i++;
		}
		if(tmp[0] == ':' && tmp[7] == '0' && tmp[8] == '4' && tmp[11] == '0' && tmp[12] == '8')
                        mm_flg = 1;
		//:10ff8000
		if(tmp[0] == ':' && tmp[1] == '1' && tmp[2] == '0' && tmp[3] == 'f' && tmp[4] == 'f' && tmp[5] == '8' && tmp[6] == '0' && tmp[7] == '0' && tmp[8] == '0')
                        mm_info = 1;
		if (tmp[7] == '0' && tmp[8] == '0' && mm_flg && !mm_info) {
			byte_num = char2byte(tmp[1], tmp[2]);
			for (i = 0; i < byte_num * 2; i += 2) {
				data = char2byte(tmp[9 + i], tmp[9 + i + 1]);
				fputc(data, mboot_mcs_fp_new);
				gmcs1_len++;
			}
		} else if (tmp[7] == '0' && tmp[8] == '1' && mm_flg && !mm_info)
			break;
		mm_info = 0;
	}

	fclose(mboot_mcs_fp);
	fclose(mboot_mcs_fp_new);
	return 0;
}

void mboot(void)
{
	unsigned char FLASH_PAGE[SPI_FLASH_PAGE];
	unsigned int addr = MCS1_ADDR_BASE;
	int byte_num, all_byte;
	unsigned short crc_init = 0;
	FILE *mboot_mcs_fp_new;
	int j;

	mboot_mcs_file();
	all_byte = gmcs1_len;

	i2c_open(I2C_DEV);

	mboot_mcs_fp_new = fopen("./mm_new.mcs", "rt");

	printf("(1) MM Flash Erase Begin! Please Wait...\n");
	enable_download();
	flash_prog_en();
	flash_earse();
	printf("    MM Flash Erase Success!\n");

	printf("(2) Flash Program Begin! Please Wait...\n");
	while (all_byte) {
		if (all_byte >= SPI_FLASH_PAGE) {
			byte_num = SPI_FLASH_PAGE;
			all_byte -= SPI_FLASH_PAGE;
		} else {
			byte_num = all_byte;
			all_byte = 0;
		}

		for (j = 0; j < byte_num; j++) {
			FLASH_PAGE[j] = fgetc(mboot_mcs_fp_new);
			crc_init = mboot_crc16(crc_init, &FLASH_PAGE[j], 1);
		}
		flash_prog_page(FLASH_PAGE, addr, byte_num);
		addr += byte_num;
		printf("+");
		fflush(stdout);
	}
	printf("\n    MM Flash Program Success!\n");

	flash_prog_info(crc_init, gmcs1_len);
	fclose(mboot_mcs_fp_new);
	printf("    MM Flash Program Done!\n");
	set_cs(IIC2SPI_DISABLE);
	printf("(3) Reboot!\n");
	set_reboot();
	i2c_close();
}

void mm_detect(void)
{
#define I2C_SLAVE_ADDR	1
	unsigned char mmpkg[40];
	i2c_open(I2C_DEV);
	i2c_setslave(I2C_SLAVE_ADDR);

	/* MM DETECT PACKAGE */
	memset(mmpkg, 0, 40);
	mmpkg[0] = 0x43;
	mmpkg[1] = 0x4e;
	mmpkg[2] = 0x10;
	mmpkg[3] = 0x00;
	mmpkg[4] = 0x01;
	mmpkg[5] = 0x01;

	printf("Detect MM:\n");
	hexdump(mmpkg, 40);

	/* Wait mm ack */
	sleep_ms(20);

	if (!i2c_read(mmpkg, 40)) {
		printf("Ack MM:\n");
		hexdump(mmpkg, 40);
	}

	i2c_close();
}

