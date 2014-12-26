#include <stdio.h>
#include <stddef.h>
#include <string.h>
#include "auc.h"

#define AVA4_MM_DNA_LEN 8
#define AVA4_MM_VER_LEN 15
#define AVA4_DEFAULT_MODULARS 64
#define AVA4_DEFAULT_MINERS 10

/* packet type */
#define AVA4_P_DETECT   0x10
#define AVA4_P_FINISH	0x21
#define AVA4_P_REQUIRE  0x31
#define AVA4_P_TEST     0x32

struct avalon4_pkg {
	uint8_t head[2];
	uint8_t type;
	uint8_t opt;
	uint8_t idx;
	uint8_t cnt;
	uint8_t data[32];
	uint8_t crc[2];
};

struct auc_mmpkg {
	struct cdc_i2c_header header;
	struct avalon4_pkg mm;
};

struct mmreport {
	unsigned char auc_id[20];
	unsigned short mm_id;
	unsigned char mm_ver[AVA4_MM_VER_LEN];
	unsigned char mm_dna[AVA4_MM_DNA_LEN];
	unsigned char pg1[5][30];
	unsigned char pg2[5][30];
	unsigned short bad;
	unsigned short all;
};

struct mmreport reportlist[AVA4_DEFAULT_MODULARS];

static void iic_config_init(struct i2c_config *cfg)
{

}

static void auc_mmpkg_init(struct auc_mmpkg *mmpkg, uint8_t type, uint8_t idx, uint8_t cnt, uint8_t module_id)
{

}

static int auc_mmpkg_send(const struct auc_mmpkg *mmpkg)
{
	return 0;
}

static int auc_mmpkg_receive(struct auc_mmpkg *mmpkg)
{
	return 0;
}

static int mmpkg_parse(const struct auc_mmpkg *mmpkg)
{
	return 0;
}

static void mm_corereport(AUC_HANDLE handle, uint16_t testcores, uint16_t freq[], uint16_t voltage)
{
	struct auc_mmpkg sendpkg, recvpkg;
	int i, j, miner_index = 0;

	memset(reportlist, 0, sizeof(struct mmreport));

	/* Detect new modules */
	auc_mmpkg_init(&sendpkg, AVA4_P_DETECT, 1, 1, 0);
	while (1) {
		auc_mmpkg_send(&sendpkg);
		if (auc_mmpkg_receive(&recvpkg))
			mmpkg_parse(&recvpkg);
		else
			break;
	}

	for (i = 1; i < AVA4_DEFAULT_MODULARS; i++) {
		if (reportlist[i].mm_id) {
			while (1) {
				auc_mmpkg_init(&sendpkg, AVA4_P_REQUIRE, 1, 1, reportlist[i].mm_id);
				if (auc_mmpkg_receive(&recvpkg)) {
					mmpkg_parse(&recvpkg);
					miner_index++;
				}

				if (miner_index == AVA4_DEFAULT_MODULARS + 1)
					break;

				for (j = 0; j < AVA4_DEFAULT_MODULARS; j++) {
					/* Keep other modules alive */
					if (j != i && reportlist[j].mm_id) {
						auc_mmpkg_init(&sendpkg, AVA4_P_FINISH, 1, 1, reportlist[j].mm_id);
						auc_mmpkg_send(&sendpkg);
					}
				}
			}
		}
	}

	/* Write reportlist to file */
	for (i = 1; i < AVA4_DEFAULT_MODULARS; i++) {
		/* TODO: use lib-jasson to record the reportlist */
	}
}

void mm_coretest(uint16_t testcores, uint16_t freq[], uint16_t voltage)
{
	AUC_HANDLE hauc;
	struct i2c_config iic_cfg;
	uint32_t auc_cnts;
	uint32_t i;

	auc_cnts = auc_getcounts();
	if (!auc_cnts)
		printf("No AUC found!\n");

	iic_config_init(&iic_cfg);
	for (i = 0; i < auc_cnts; i++) {
		hauc = auc_open(i);
		if (hauc) {
			auc_init(hauc, &iic_cfg);
			mm_corereport(hauc, testcores, freq, voltage);
			auc_close(hauc);
			hauc = NULL;
		}
	}
}

