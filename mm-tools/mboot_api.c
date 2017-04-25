#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <pthread.h>
#include <errno.h>      /* For detailed file I/O error reporting */
#include "uthash.h"
#include "hexdump.c"
#include "crc.h"
#include "iic.h"

#define MCS1_INFO_ADDR_BASE 0xfff80
#define MCS1_INFO_LEN 16 //bytes
#define MCS1_ADDR_BASE 0x80000
#define SPI_FLASH_BLOCK 0x10000
#define SPI_FLASH_32K	0x8000
#define SPI_FLASH_SEC 0x1000
#define SPI_FLASH_PAGE 256 //byte
#define CMD_LEN 4
#define IIC_SLAVE_CTL 0x40
#define IIC_SLAVE_DAT 0x41
#define CS_ENABLE 0
#define CS_DISABLE 1
#define IIC2SPI_DISABLE 3

#define THR_NAME_LEN    10

static char *g_newmcs_filepath = NULL;

struct thread {
	pthread_t pth;
	char name[THR_NAME_LEN];
	UT_hash_handle hh;
};

struct thread *thread_pool = NULL;
static int gmcs1_len;

static unsigned char mm_type[16]; /* Firmware Type */

static void sleep_ms(unsigned int ms)
{
    usleep(ms * 1000);
}

static int enable_download(struct i2c_drv *iic)
{
	unsigned char buf[1];

	iic->i2c_setslave(IIC_SLAVE_CTL);
	/* enable download */
	buf[0] = 0x2;
	if (iic->i2c_write(buf, 1)) {
		printf("%s-%s failed!\n", iic->name, __FUNCTION__);
		return 1;
	}

	iic->i2c_setslave(IIC_SLAVE_DAT);
	return 0;
}

static int set_cs(struct i2c_drv *iic, unsigned char dat)
{
	unsigned char buf[1];

	iic->i2c_setslave(IIC_SLAVE_CTL);
	/* set cs */
	buf[0] = dat;
	if (iic->i2c_write(buf, 1)) {
		printf("%s-%s failed!\n", iic->name, __FUNCTION__);
		return 1;
	}
	iic->i2c_setslave(IIC_SLAVE_DAT);
	return 0;
}

static int set_reboot(struct i2c_drv *iic)
{
	unsigned char buf[1];

	iic->i2c_setslave(IIC_SLAVE_CTL);
	buf[0] = 4;
	if (iic->i2c_write(buf, 1)) {
		printf("%s-%s failed!\n", iic->name, __FUNCTION__);
		return 1;
	}
	return 0;
}

static int set_mosi_dat(struct i2c_drv *iic, unsigned char *buf, unsigned int len)
{
	iic->i2c_setslave(IIC_SLAVE_DAT);
	if (iic->i2c_write(buf, len)) {
		printf("%s-%s failed!\n", iic->name, __FUNCTION__);
		return 1;
	}
	return 0;
}

static int flash_prog_en(struct i2c_drv *iic)
{
	unsigned char buf_cmd[1];

	if (set_cs(iic, CS_ENABLE))
		return 1;

	buf_cmd[0] = 0x06;
	if (set_mosi_dat(iic, buf_cmd, 1))
		return 1;

	if (set_cs(iic, CS_DISABLE))
		return 1;

	sleep_ms(3);
	return 0;
}

static int flash_erase_op(struct i2c_drv *iic, unsigned int addr, unsigned char op)
{
	unsigned char buf[4];

	buf[0] = op;
	buf[1] = ((addr >> 16) & 0xff);
	buf[2] = ((addr >> 8) & 0xff);
	buf[3] = (addr & 0xff);

	if (flash_prog_en(iic))
		return 1;

	if (set_cs(iic, CS_ENABLE))
		return 1;

	if (set_mosi_dat(iic, buf, 4))
		return 1;

	if (set_cs(iic, CS_DISABLE))
		return 1;

	sleep_ms(1000);
	return 0;
}

static int flash_earse(struct i2c_drv *iic)
{
	unsigned int addr = MCS1_ADDR_BASE;
	int i;

	printf("%s-BE64 addr = %x\n", iic->name, addr);
	for (i = 0; i < 7; i++) {
		if (flash_erase_op(iic, addr, 0xd8))
			return 1;
		addr += SPI_FLASH_BLOCK;
		printf("+");
		fflush(stdout);
	}

	printf("\n");
	printf("%s-BE32 addr = %x\n", iic->name, addr);
	if (flash_erase_op(iic, addr, 0x52))
		return 1;
	addr += SPI_FLASH_32K;
	printf("+");
	fflush(stdout);

	printf("\n");
	printf("%s-SE addr = %x\n", iic->name, addr);
	for (i = 0; i < 4; i++) {
		if (flash_erase_op(iic, addr, 0x20))
			return 1;
		addr += SPI_FLASH_SEC;
		printf("+");
		fflush(stdout);
	}
	/* mboot confg reserved, 3 sectors[0xfc000 ~ 0xfe000] */
	printf("\n");
	printf("%s-SE addr = %x\n", iic->name, 0xff000);
	/* Last sector */
	if (flash_erase_op(iic, 0xff000, 0x20))
		return 1;
	printf("+");
	fflush(stdout);
	printf("\n");
	return 0;
}

static int flash_prog_page(struct i2c_drv *iic, unsigned char *buf, unsigned int addr, unsigned int len)
{
	unsigned char buf_cmd[4];

	if (flash_prog_en(iic))
		return 1;

	if (set_cs(iic, CS_ENABLE))
		return 1;

	buf_cmd[0] = 0x02;
	buf_cmd[1] = ((addr >> 16) & 0xff);
	buf_cmd[2] = ((addr >> 8) & 0xff);
	buf_cmd[3] = (addr & 0xff);
	if (set_mosi_dat(iic, buf_cmd, 4))
		return 1;

	if (set_mosi_dat(iic, buf, len))
		return 1;

	if (set_cs(iic, CS_DISABLE))
		return 1;

	sleep_ms(3);
	return 0;
}

static int flash_prog_info(struct i2c_drv *iic, unsigned short crc, unsigned int len)
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
	if (flash_prog_page(iic, mcs1_info, MCS1_INFO_ADDR_BASE, 16))
		return 1;

	return 0;
}

static char char2byte(char char0, char char1)
{
	if (char0 >= 'a' && char0 <= 'f')
		char0 = char0 - 'a' + 10;
	else if (char0 >= 'A' && char0 <= 'F')
		char0 = char0 - 'A' + 10;
	else
		char0 = char0 - '0';

	if (char1 >= 'a' && char1 <= 'f')
		char1 = char1 - 'a' + 10;
	else if (char1 >= 'A' && char1 <= 'F')
		char1 = char1 - 'A' + 10;
	else
		char1 = char1 - '0';

	return (char0 << 4) | char1;
}

static int mboot_mcs_file(char *mcs_filepath)
{
	int i, byte_num, mm_flg = 0, mm_info = 0, mcs1_len = 0;
	unsigned char tmp[1000];
	unsigned char data;
	FILE *mboot_mcs_fp;
	FILE *mboot_mcs_fp_new;

	mcs1_len = 0;
	mboot_mcs_fp = fopen(mcs_filepath, "rt");
	if (mboot_mcs_fp == NULL) {
		printf("open %s error: %s!\n", mcs_filepath, strerror(errno)); // Detailed error reporting
		exit(1);
	} else
		printf("open %s success!\n", mcs_filepath);

	g_newmcs_filepath = malloc(strlen(mcs_filepath) + 4 + 1);
	sprintf(g_newmcs_filepath, "%s_new", mcs_filepath);

	mboot_mcs_fp_new = fopen(g_newmcs_filepath, "wb");
	if (mboot_mcs_fp_new == NULL) {
		printf("open %s error: %s!\n", g_newmcs_filepath, strerror(errno));
		exit(1);
	} else
		printf("open %s success!\n", g_newmcs_filepath);

	while (1) {
		i = 0;
		while (1) {
			tmp[i] = fgetc(mboot_mcs_fp);
			if (tmp[i] == '\n')
				break;
			i++;
		}
		//:10fe0000
		if(tmp[0] == ':' && tmp[1] == '1' && tmp[2] == '0' && tmp[3] == 'f' && tmp[4] == 'e' && tmp[5] == '0' && tmp[6] == '0' && tmp[7] == '0' && tmp[8] == '0') {
			for (i = 0; i < 32; i += 2)
				mm_type[i / 2] = char2byte(tmp[9 + i], tmp[9 + i + 1]);
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
				mcs1_len++;
			}
		} else if (tmp[7] == '0' && tmp[8] == '1' && mm_flg && !mm_info)
			break;
		mm_info = 0;
	}

	fclose(mboot_mcs_fp);
	fclose(mboot_mcs_fp_new);
	return mcs1_len;
}

static void *reboot_op(void *arg)
{
	struct i2c_drv *iic = (struct i2c_drv *)arg;

	if (iic->i2c_open(I2C_DEV)) {
		printf(" %s-i2c_open failed!\n", iic->name);
		return NULL;
	}

	if (set_reboot(iic))
		printf("%s-set_reboot failed!\n", iic->name);


	iic->i2c_close();
	return NULL;
}

static void *upgrade_op(void *arg)
{
	struct i2c_drv *iic = (struct i2c_drv *)arg;
	unsigned char FLASH_PAGE[SPI_FLASH_PAGE];
	unsigned int addr = MCS1_ADDR_BASE;
	int byte_num, all_byte;
	unsigned short crc_init = 0;
	FILE *mboot_mcs_fp_new;
	int i;

	all_byte = gmcs1_len;
	if (iic->i2c_open(I2C_DEV)) {
		printf(" %s-i2c_open failed!\n", iic->name);
		return NULL;
	}

	mboot_mcs_fp_new = fopen(g_newmcs_filepath, "rt");
	printf(" (1) %s-MM Flash Erase Begin! Please Wait...\n", iic->name);
	if (enable_download(iic))
		goto ret;

	if (flash_prog_en(iic)) {
		printf("%s-flash_prog_en failed!\n", iic->name);
		goto ret;
	}

	if (flash_earse(iic)) {
		printf("%s-flash_earse failed!\n", iic->name);
		goto ret;
	}
	printf("    %s-MM Flash Erase Success!\n", iic->name);

	printf("(2) %s-Flash Program Begin! Please Wait...\n", iic->name);
	while (all_byte) {
		if (all_byte >= SPI_FLASH_PAGE) {
			byte_num = SPI_FLASH_PAGE;
			all_byte -= SPI_FLASH_PAGE;
		} else {
			byte_num = all_byte;
			all_byte = 0;
		}

		for (i = 0; i < byte_num; i++) {
			FLASH_PAGE[i] = fgetc(mboot_mcs_fp_new);
			crc_init = mboot_crc16(crc_init, &FLASH_PAGE[i], 1);
		}
		if (flash_prog_page(iic, FLASH_PAGE, addr, byte_num)) {
			printf("%s-flash_prog_page failed!\n", iic->name);
			goto ret;
		}
		addr += byte_num;
		printf("+");
		fflush(stdout);
	}
	printf("\n    %s-MM Flash Program Success!\n", iic->name);

	if (flash_prog_info(iic, crc_init, gmcs1_len)) {
		printf("%s-flash_prog_info failed!\n", iic->name);
		goto ret;
	}

	fclose(mboot_mcs_fp_new);
	printf("    %s-MM Flash Program Done!\n", iic->name);
	if (set_cs(iic, IIC2SPI_DISABLE)) {
		printf("%s-IIC2SPI_DISABLE failed!\n", iic->name);
		goto ret;
	}

	printf("(3) %s-Reboot!\n", iic->name);
	if (set_reboot(iic)) {
		printf("%s-set_reboot failed!\n", iic->name);
		goto ret;
	}

ret:
	iic->i2c_close();
	return NULL;
}

#define DRIVER_UPGRADE_MCS(X) mboot_upgrade(&X##_drv);
void mboot_upgrade(struct i2c_drv *iic)
{
	struct thread *thr = NULL;

	thr = (struct thread *)malloc(sizeof(struct thread));
	if (!thr) {
		printf("%s-Failed to malloc struct thread!", iic->name);
		exit(1);
	}
	strncpy(thr->name, iic->name, THR_NAME_LEN);

	pthread_create(&thr->pth, NULL, upgrade_op, (void *)iic);
	HASH_ADD_STR(thread_pool, name, thr);
}

#define DRIVER_REBOOT_MM(X) mm_reboot(&X##_drv);
void mm_reboot(struct i2c_drv *iic)
{
	struct thread *thr = NULL;

	thr = (struct thread *)malloc(sizeof(struct thread));
	if (!thr) {
		printf("%s-Failed to malloc struct thread!", iic->name);
		exit(1);
	}
	strncpy(thr->name, iic->name, THR_NAME_LEN);

	pthread_create(&thr->pth, NULL, reboot_op, (void *)iic);
	HASH_ADD_STR(thread_pool, name, thr);
}

#define DRIVER_CHECK_FINISH(X) mboot_finish(&X##_drv);
void mboot_finish(struct i2c_drv *iic)
{
	struct thread *thr = NULL;

	HASH_FIND_STR(thread_pool, iic->name, thr);
	if (thr) {
		pthread_join(thr->pth, NULL);
		HASH_DEL(thread_pool, thr);
		free(thr);
	}
	free(g_newmcs_filepath);
	g_newmcs_filepath = NULL;
}

void mboot(char *mcs_filepath)
{
	gmcs1_len = mboot_mcs_file(mcs_filepath);

	if ((mm_type[0] == 'M') && (mm_type[1] == 'M')) {
		mm_send_upgrade_info(&mm_type[2], 3);
		printf("mm type: %s\n", mm_type);
	}

	DRIVERS_DO(DRIVER_UPGRADE_MCS);
	DRIVERS_DO(DRIVER_CHECK_FINISH);
	printf("finished mboot!\n");
}

void mreboot()
{
	DRIVERS_DO(DRIVER_REBOOT_MM);
	DRIVERS_DO(DRIVER_CHECK_FINISH);
	printf("finished mreboot!\n");
}
