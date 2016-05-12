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
#include <unistd.h>
#include "lcd.h"

int main(int argc, char *argv[])
{
	lcd_init();

	lcd_on();
	lcd_puts("Ver: 601511-f4f59c70");

	while (1) {
		lcd_setcursor(0, 1);
		lcd_puts("GHS1m: 3236.24");
		usleep(1000 * 100);
		lcd_setcursor(0, 1);
		lcd_puts("GHS1m: 3236.25");
		usleep(1000 * 100);
	}

	return 0;
}
