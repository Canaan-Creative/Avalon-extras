#include <stdio.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>
#include "crc.h"
#include "auc.h"
#include "jansson.h"

#define AVA4_MM_DNA_LEN 8
#define AVA4_MM_VER_LEN 15
#define AVA4_DEFAULT_MODULARS 64
#define AVA4_DEFAULT_MINERS 10
#define AVA4_H1 'C'
#define AVA4_H2 'N'
#define AVA4_P_COUNT	40
#define AVA4_P_DATA_LEN 32

/* packet type */
#define AVA4_P_DETECT	0x10
#define AVA4_P_FINISH	0x21
#define AVA4_P_REQUIRE	0x31
#define AVA4_P_TEST	0x32
#define AVA4_P_ACKDETECT	0x40
#define AVA4_P_UPGRADE_INFO	0x18

#define AVA4_MODULE_BROADCAST	0

struct avalon4_pkg {
	uint8_t head[2];
	uint8_t type;
	uint8_t opt;
	uint8_t idx;
	uint8_t cnt;
	uint8_t data[32];
	uint8_t crc[2];
};

struct mmreport {
	char auc_id[20];
	uint16_t mm_enable;
	uint8_t mm_ver[AVA4_MM_VER_LEN + 1];
	uint8_t mm_dna[AVA4_MM_DNA_LEN + 1];
	uint8_t pg1[5][30];
	uint8_t pg2[5][30];
	uint16_t bad;
	uint16_t all;
};

static struct mmreport reportlist[AVA4_DEFAULT_MODULARS];
static uint32_t g_auc_id;

static void avalon4_pkg_init(struct avalon4_pkg *mmpkg, uint8_t type, uint8_t idx, uint8_t cnt)
{
	uint16_t crc = 0;

	mmpkg->head[0] = AVA4_H1;
	mmpkg->head[1] = AVA4_H2;
	mmpkg->type = type;
	mmpkg->opt = 0;
	mmpkg->idx = idx;
	mmpkg->cnt = cnt;
	crc = mboot_crc16(0, mmpkg->data, AVA4_P_DATA_LEN);

	mmpkg->crc[0] = (crc >> 8) & 0xff;
	mmpkg->crc[1] = crc & 0xff;
}

static int32_t avalon4_pkg_send(AUC_HANDLE handle, const struct avalon4_pkg *mmpkg, uint8_t module_id)
{
	return auc_xfer(handle, module_id, (uint8_t *)mmpkg, AVA4_P_COUNT, NULL, 0, NULL);
}

static int32_t avalon4_pkg_receive(AUC_HANDLE handle, struct avalon4_pkg *mmpkg, uint8_t module_id)
{
	return auc_xfer(handle, module_id, NULL, 0, (uint8_t *)mmpkg, AVA4_P_COUNT, NULL);
}

static int32_t mmpkg_parse(const struct avalon4_pkg *mmpkg, uint8_t module_id)
{
	switch (mmpkg->type) {
		case AVA4_P_ACKDETECT:
			sprintf(reportlist[module_id].auc_id, "AV4-%d", g_auc_id);
			reportlist[module_id].mm_enable = 1;
			memcpy(reportlist[module_id].mm_dna, mmpkg->data, AVA4_MM_DNA_LEN);
			reportlist[module_id].mm_dna[AVA4_MM_DNA_LEN] = '\0';
			memcpy(reportlist[module_id].mm_ver, mmpkg->data + AVA4_MM_DNA_LEN, AVA4_MM_VER_LEN);
			break;

		default:
			printf("unhandle packge type = 0x%x\n", mmpkg->type);
			break;
	}
	return 0;
}

static void mm_detect(AUC_HANDLE handle)
{
	struct avalon4_pkg sendpkg, recvpkg;
	int32_t i;

	/* Detect new modules */
	i = 1;
	while (1) {
		memset(sendpkg.data, 0, AVA4_P_DATA_LEN);
		sendpkg.data[28] = (i >> 24) & 0xff;
		sendpkg.data[29] = (i >> 16) & 0xff;
		sendpkg.data[30] = (i >> 8) & 0xff;
		sendpkg.data[31] = i & 0xff;
		avalon4_pkg_init(&sendpkg, AVA4_P_DETECT, 1, 1);
		avalon4_pkg_send(handle, &sendpkg, AVA4_MODULE_BROADCAST);
		if (avalon4_pkg_receive(handle, &recvpkg, AVA4_MODULE_BROADCAST)) {
			mmpkg_parse(&recvpkg, i);
			i++;
		} else
			break;
	}
}

extern void hexdump(const uint8_t *p, uint32_t len);
static void mm_test(AUC_HANDLE handle, uint16_t testcores, uint16_t freq[], uint16_t voltage)
{
	struct avalon4_pkg sendpkg, recvpkg;
	int32_t i, j, miner_index = 0;

	memset(sendpkg.data, 0, AVA4_P_DATA_LEN);
	sendpkg.data[0] = 0; /* test core cnt */
	sendpkg.data[1] = 0;
	sendpkg.data[2] = 0;
	sendpkg.data[3] = 64;

	/* TODO: covert voltage */
	sendpkg.data[4] = 0; /* voltage */
	sendpkg.data[5] = 0;
	sendpkg.data[6] = 0xc1;
	sendpkg.data[7] = 0;

	/* TODO: covert freq */
	sendpkg.data[8] = 0; /* freq */
	sendpkg.data[9] = 0;
	sendpkg.data[10] = 0;
	sendpkg.data[11] = 0;

	sendpkg.data[12] = 0; /* freq pll1 */
	sendpkg.data[13] = 0;
	sendpkg.data[14] = 0;
	sendpkg.data[15] = 0;


	sendpkg.data[16] = 0; /* freq pll2 */
	sendpkg.data[17] = 0;
	sendpkg.data[18] = 0;
	sendpkg.data[19] = 0;


	sendpkg.data[20] = 0; /* freq pll3 */
	sendpkg.data[21] = 0;
	sendpkg.data[22] = 0;
	sendpkg.data[23] = 0;

	for (i = 1; i < AVA4_DEFAULT_MODULARS; i++) {
		if (reportlist[i].mm_enable) {
			miner_index = 0;
			avalon4_pkg_init(&sendpkg, AVA4_P_TEST, 1, 1);
			avalon4_pkg_send(handle, &sendpkg, i);
			while (1) {
				if (avalon4_pkg_receive(handle, &recvpkg, i)) {
					/* TODO: miner_index[1], result[4] * 4 */
					hexdump(recvpkg.data, AVA4_P_DATA_LEN);

					miner_index++;
				}

				if (miner_index == AVA4_DEFAULT_MINERS + 1) {
					/* TODO: pass[4], all[4] */
					hexdump(recvpkg.data, AVA4_P_DATA_LEN);
					break;
				}

				for (j = 1; j < AVA4_DEFAULT_MODULARS; j++) {
					/* Keep other modules alive */
					if (j != i && reportlist[j].mm_enable) {
						avalon4_pkg_init(&sendpkg, AVA4_P_FINISH, 1, 1);
						avalon4_pkg_send(handle, &sendpkg, j);
					}
				}
			}
		}
	}
}

void mm_send_upgrade_info(uint8_t *buf, uint8_t len)
{
	struct avalon4_pkg sendpkg;
	AUC_HANDLE hauc;
	uint32_t auc_cnts;
	uint32_t i;

	auc_cnts = auc_getcounts();
	if (!auc_cnts)
		printf("No AUC found!\n");

	for (i = 0; i < auc_cnts; i++) {
		hauc = auc_open(i);
		if (hauc) {
			g_auc_id = i;
			auc_init(hauc, I2C_CLK_1M, 9600);
			printf("auc-%d, ver:%s\n", i, auc_version(i));

			memset(sendpkg.data, 0, AVA4_P_DATA_LEN);
			memcpy(sendpkg.data, buf, len);
			avalon4_pkg_init(&sendpkg, AVA4_P_UPGRADE_INFO, 1, 1);
			avalon4_pkg_send(hauc, &sendpkg, 0);

			auc_close(hauc);
			hauc = NULL;
		}
	}
}

static void write_jansson(struct mmreport mm_report, uint32_t mm_report_mm_id, FILE *fp)
{
	char tmp[31];
	json_t *report = json_object();
	json_t *auc_id = json_string(mm_report.auc_id);
	json_t *mm_id = json_integer(mm_report_mm_id);
	snprintf(tmp, AVA4_MM_VER_LEN, "%s", mm_report.mm_ver);
	json_t *mm_ver = json_string(tmp);
	snprintf(tmp, AVA4_MM_DNA_LEN, "%s", mm_report.mm_dna);
	json_t *mm_dna = json_string(tmp);
	json_t *bad = json_integer(mm_report.bad);
	json_t *all = json_integer(mm_report.all);
	int percent = (int)(((double)mm_report.bad / (double)mm_report.all) * 100);
	sprintf(tmp, "%d%%", percent);
	json_t *bad_percent = json_string(tmp);

	json_t *PG1 = json_array();
	snprintf(tmp, 30, "%s", mm_report.pg1[0]);
	json_t *PG1_0 = json_string(tmp);
	snprintf(tmp, 30, "%s", mm_report.pg1[1]);
	json_t *PG1_1 = json_string(tmp);
	snprintf(tmp, 30, "%s", mm_report.pg1[2]);
	json_t *PG1_2 = json_string(tmp);
	snprintf(tmp, 30, "%s", mm_report.pg1[3]);
	json_t *PG1_3 = json_string(tmp);
	snprintf(tmp, 30, "%s", mm_report.pg1[4]);
	json_t *PG1_4 = json_string(tmp);

	json_t *PG2 = json_array();
	snprintf(tmp, 30, "%s", mm_report.pg2[0]);
	json_t *PG2_0 = json_string(tmp);
	snprintf(tmp, 30, "%s", mm_report.pg2[1]);
	json_t *PG2_1 = json_string(tmp);
	snprintf(tmp, 30, "%s", mm_report.pg2[2]);
	json_t *PG2_2 = json_string(tmp);
	snprintf(tmp, 30, "%s", mm_report.pg2[3]);
	json_t *PG2_3 = json_string(tmp);
	snprintf(tmp, 30, "%s", mm_report.pg2[4]);
	json_t *PG2_4 = json_string(tmp);

	json_array_insert_new(PG1, 0, PG1_0);
	json_array_insert_new(PG1, 1, PG1_1);
	json_array_insert_new(PG1, 2, PG1_2);
	json_array_insert_new(PG1, 3, PG1_3);
	json_array_insert_new(PG1, 4, PG1_4);

	json_array_insert_new(PG2, 0, PG2_0);
	json_array_insert_new(PG2, 1, PG2_1);
	json_array_insert_new(PG2, 2, PG2_2);
	json_array_insert_new(PG2, 3, PG2_3);
	json_array_insert_new(PG2, 4, PG2_4);

	json_object_set_new(report, "AUC ID", auc_id);
	json_object_set_new(report, "MM ID", mm_id);
	json_object_set_new(report, "MM VER", mm_ver);
	json_object_set_new(report, "MM DNA", mm_dna);
	json_object_set_new(report, "PG1", PG1);
	json_object_set_new(report, "PG2", PG2);
	json_object_set_new(report, "bad", bad);
	json_object_set_new(report, "all", all);
	json_object_set_new(report, "bad_percent", bad_percent);

	json_dumpf(report, fp, 0);
}

static void jansson_test()
{
	uint32_t i;
	FILE *fp = NULL;
	memset(reportlist, 0, sizeof(struct mmreport) * AVA4_DEFAULT_MODULARS);

	sprintf(reportlist[1].auc_id, "%s", "AV4-1");
	for (i = 0; i < AVA4_MM_VER_LEN; i++)
		reportlist[1].mm_ver[i] = 65 + i;

	for (i = 0; i < AVA4_MM_DNA_LEN; i++)
		reportlist[1].mm_dna[i] = 97 + i;

	for (i = 0; i < 30; i++) {
		reportlist[1].pg1[0][i] = 66 + i;
		reportlist[1].pg1[1][i] = 67 + i;
		reportlist[1].pg1[2][i] = 68 + i;
		reportlist[1].pg1[3][i] = 69 + i;
		reportlist[1].pg1[4][i] = 70 + i;
		reportlist[1].pg2[0][i] = 71 + i;
		reportlist[1].pg2[1][i] = 72 + i;
		reportlist[1].pg2[2][i] = 73 + i;
		reportlist[1].pg2[3][i] = 74 + i;
		reportlist[1].pg2[4][i] = 75 + i;
	}
	reportlist[1].bad = 1;
	reportlist[1].all = 100;

	fp = fopen("/tmp/coretest.log", "wt");
	if(fp == NULL) {
		printf("Open FILE failed\r\n");
		return;
	}

	write_jansson(reportlist[1], i, fp);
	printf("Write report test success\r\n");
	fclose(fp);
}

static void mm_corereport(AUC_HANDLE handle, uint16_t testcores, uint16_t freq[], uint16_t voltage)
{
	uint32_t i;
	FILE *fp = NULL;

	memset(reportlist, 0, sizeof(struct mmreport) * AVA4_DEFAULT_MODULARS);

	mm_detect(handle);
	mm_test(handle, testcores, freq, voltage);

	/* Write reportlist to file */
	fp = fopen("/tmp/coretest.log", "wt");
	if(fp == NULL) {
		printf("Open FILE failed\r\n");
		return;
	}

	for (i = 1; i < AVA4_DEFAULT_MODULARS; i++) {
		/* TODO: use lib-jansson to record the reportlist */
		write_jansson(reportlist[i], i, fp);
	}
	printf("Write report success\r\n");
	fclose(fp);
}

void mm_coretest(uint16_t testcores, uint16_t freq[], uint16_t voltage)
{
	AUC_HANDLE hauc;
	uint32_t auc_cnts;
	uint32_t i;

	jansson_test();
	auc_cnts = auc_getcounts();
	if (!auc_cnts)
		printf("No AUC found!\n");

	for (i = 0; i < auc_cnts; i++) {
		hauc = auc_open(i);
		if (hauc) {
			g_auc_id = i;
			auc_init(hauc, I2C_CLK_1M, 9600);
			printf("auc-%d, ver:%s\n", i, auc_version(i));
			mm_corereport(hauc, testcores, freq, voltage);
			auc_close(hauc);
			hauc = NULL;
		}
	}
}

void set_radiator_mode()
{
	AUC_HANDLE hauc[AUC_DEVCNT];
	uint32_t auc_cnts;
	uint32_t i;
	struct avalon4_pkg sendpkg;

	memset(hauc, 0, AUC_DEVCNT);
	auc_cnts = auc_getcounts();
	if (!auc_cnts) {
		printf("No AUC found!\n");
		return;
	} else
		printf("Find %d auc\n", auc_cnts);

	for (i = 0; i < auc_cnts; i++) {
		hauc[i] = auc_open(i);
		if (hauc[i]) {
			auc_init(hauc[i], I2C_CLK_1M, 9600);
			printf("auc-%d, ver:%s\n", i, auc_version(i));
		}
	}

	while(1) {
		for (i = 0; i < auc_cnts; i++) {
			avalon4_pkg_init(&sendpkg, AVA4_P_FINISH, 1, 1);
			avalon4_pkg_send(hauc[i], &sendpkg, 0);
		}
		sleep(2);
	}

	for (i = 0; i < auc_cnts; i++)
		auc_close(hauc[i]);
}

