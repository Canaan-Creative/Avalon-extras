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
#include <stdlib.h>
#include <unistd.h>
#include <getopt.h>
#include "lcd.h"

static struct option opts[] = {
	{ "help", no_argument, NULL, 'h' },
	{ "control", required_argument, NULL, 'c' },
	{ "string", required_argument, NULL, 's' },
	{ "init", no_argument, NULL, 'i' },
	{ NULL, 0, NULL, 0 }
};

static void help(void)
{
	printf("Usage: lcd-tools [options] ...\n"
		"  -h --help\t\t\tPrint this help message\n"
		"  -c --control\t\t\tTurn off or on (0/1)\n"
		"  -s --string\t\t\tDisplay string\n"
		"  -i --init\t\t\tInit LCD\n"
	);
}

static void display(char *str)
{
	int row = 0;

	lcd_home();
	while (*str) {
		/* process \n */
		if ((*str == '\\') && (*(str + 1) == 'n')) {
			row++;
			lcd_setcursor(0, row);
			str += 2;
			continue;
		}
		lcd_write(*str);
		str++;
	}
}

int main(int argc, char *argv[])
{
	int c, option_index = 0;

	c = getopt_long(argc, argv, "hc:s:i", opts, &option_index);
	switch (c) {
		case 'h':
			help();
			break;
		case 'c':
			if (atoi(optarg))
				lcd_on();
			else
				lcd_off();
			break;
		case 's':
			display(optarg);
			break;
		case 'i':
			lcd_init();
			break;
		default:
			help();
			break;
	}

	return 0;
}
