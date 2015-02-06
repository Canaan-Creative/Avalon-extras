/*
 * MM Upgrade program for avalon4
 *
 * Upgrade MM firmware through i2c
 *
 * By Mikeqin, 2014
 */
#include "stdio.h"
#include "getopt.h"
#include "api.h"

static void help(void)
{
	printf("Usage: mm-tools [options] ...\n"
	       "  -h --help\t\t\tPrint this help message\n"
	       "  -c --coretest\t\t\tEnter coretest function\n"
	       "  -r --radiator\t\t\tEnter radiator mode\n"
	       " <run without options will enter the basic function>\n\n"
		);
}

static struct option opts[] = {
	{ "help", 0, 0, 'h' },
	{ "coretest", 0, 0, 'c' },
	{ "radiator", 0, 0, 'r' },
	{ 0, 0, 0, 0 }
};

int main(int argc, char **argv)
{
	int c, option_index = 0;
	uint16_t freq[3], voltage = 200;
	c = getopt_long(argc, argv, "hcr", opts, &option_index);
	switch (c) {
		case 'h':
			help();
			break;
		case 'c':
			printf("Enter coretest function\r\n");
			mm_coretest(64, freq, voltage);
			break;
		case 'r':
			printf("Enter radiator mode\r\n");
			set_radiator_mode();
			break;
		default:
			printf("Enter mboot mode\r\n");
			mboot();
			break;
	}

	return 0;
}

