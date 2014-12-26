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
    	mm_detect();
#else
	mboot();
#endif
	return 0;
}

