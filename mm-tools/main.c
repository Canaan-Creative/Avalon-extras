/*
 * MM Upgrade program for avalon4
 *
 * Upgrade MM firmware through i2c
 *
 * By Mikeqin, 2014
 */
#include "api.h"

int main(int argc, char **argv)
{
#ifdef MM_TEST
	uint16_t freq[3], voltage = 200;

	mm_coretest(64, freq, voltage);
#else
	mboot();
#endif
	return 0;
}

