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

#include <stdint.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include "iic.h"
#include "lcd.h"

#define LCD_HALFMODE	0x0
#define LCD_FULLMODE	0x1

/* LCD control RS, E, BG */
#define LCD_RS	0x1
#define LCD_EN	0x4
#define LCD_BGON	0x8

/* LCD instructions */
#define LCD_CLEAR	0x1
#define LCD_HOME	0x2
#define LCD_MODE	0x4
#define LCD_DISP	0x8
#define LCD_SHIFT	0x10
#define LCD_FUNC	0x20
#define LCD_CDIR	0x40
#define LCD_DDIR	0x80

/* LCD entry mode */
#define LCD_ENTRYL	0x2
#define LCD_ENTRYR	0x0
#define LCD_ENTRYINC	0x1
#define LCD_ENTRYDEC	0x0

/* LCD display flags */
#define LCD_DISPON	0x4
#define LCD_DISPOFF	0x0
#define LCD_CURSORON	0x2
#define LCD_CURSOROFF	0x0
#define LCD_BLINKON	0x1
#define LCD_BLINKOFF	0x0

/* LCD shift flags */
#define LCD_DISPMOVE	0x8
#define LCD_CURSORMOVE	0x0
#define LCD_SR	0x4
#define LCD_SL	0x0

/* LCD function flags */
#define LCD_4BIT	0x0
#define LCD_2LINE	0x8
#define LCD_5X8DOTS	0x0

#define DEFAULT_LCD_ADDR	0x27
static uint8_t g_lcd_bg = LCD_BGON;
static uint8_t g_lcd_dispctrl = 0;
/* Only support 7 bit address */
static uint8_t g_lcd_addr = DEFAULT_LCD_ADDR;

static void iic_write_byte(uint8_t addr, uint8_t byte)
{
	iic_start();
	iic_write(addr << 1);
	iic_write(byte);
	iic_stop();
}

static void lcd_op(uint8_t data, uint8_t mode, uint8_t rs)
{
	/* write command or high 8 bits data */
	iic_write_byte(g_lcd_addr, (data & 0xf0) | g_lcd_bg | rs);
	/* enable command */
	iic_write_byte(g_lcd_addr, (data & 0xf0) | g_lcd_bg | rs | LCD_EN);
	iic_write_byte(g_lcd_addr, (data & 0xf0) | g_lcd_bg | rs);

	if (mode == LCD_FULLMODE) {
		/* write low 8bit */
		iic_write_byte(g_lcd_addr, ((data << 4) & 0xf0) | g_lcd_bg | rs);
		/* enable command */
		iic_write_byte(g_lcd_addr, ((data << 4) & 0xf0) | g_lcd_bg | rs | LCD_EN);
		iic_write_byte(g_lcd_addr, ((data << 4) & 0xf0) | g_lcd_bg | rs);
	}
}

/* https://www.sparkfun.com/datasheets/LCD/HD44780.pdf */
void lcd_init(void)
{
	uint8_t i;
	char *lcd_addr = getenv("IIC_LCD_ADDR");

	if (lcd_addr)
		g_lcd_addr = atoi(lcd_addr);

	printf("LCD addr is %d\n", g_lcd_addr);
	iic_init();

	/* Initializing HD44780.pdf P.45 */
	lcd_op(0, LCD_HALFMODE, 0);

	for (i = 0; i < 3; i++) {
		lcd_op(0x30, LCD_HALFMODE, 0);
	}

	/* set to 4-Bit Interface */
	lcd_op(0x20, LCD_HALFMODE, 0);

	/* set line, dot */
	lcd_op(LCD_FUNC | LCD_4BIT | LCD_2LINE | LCD_5X8DOTS, LCD_FULLMODE, 0);
	/* set display, turn off cursor and blink */
	g_lcd_dispctrl = LCD_DISP | LCD_DISPON | LCD_CURSOROFF | LCD_BLINKOFF;
	lcd_op(g_lcd_dispctrl, LCD_FULLMODE, 0);

	/* clear */
	lcd_op(LCD_CLEAR, LCD_FULLMODE, 0);

	/* entry mode */
	lcd_op(LCD_MODE | LCD_ENTRYL | LCD_ENTRYDEC, LCD_FULLMODE, 0);

	/* home */
	lcd_op(LCD_HOME, LCD_FULLMODE, 0);
}

void lcd_on(void)
{
	g_lcd_bg = LCD_BGON;
	g_lcd_dispctrl |= LCD_DISPON;
	lcd_op(g_lcd_dispctrl, LCD_FULLMODE, 0);
}

void lcd_off(void)
{
	g_lcd_bg = ~LCD_BGON;
	g_lcd_dispctrl &= ~LCD_DISPON;
	lcd_op(g_lcd_dispctrl, LCD_FULLMODE, 0);
}

void lcd_clear(void)
{
	lcd_op(LCD_CLEAR, LCD_FULLMODE, 0);
}

void lcd_home(void)
{
	lcd_op(LCD_HOME, LCD_FULLMODE, 0);
}

void lcd_setcursor(uint8_t col, uint8_t row)
{
	int row_offsets[] = {0x00, 0x40, 0x14, 0x54};

	/* 16 x 2 */
	if (row > 2)
		row = 1;

	lcd_op(LCD_DDIR | (col + row_offsets[row]), LCD_FULLMODE, 0);
}

void lcd_leftscroll(void)
{
	lcd_op(LCD_SHIFT | LCD_DISPMOVE | LCD_SL, LCD_FULLMODE, 0);
}

void lcd_rightscroll(void)
{
	lcd_op(LCD_SHIFT | LCD_DISPMOVE | LCD_SR, LCD_FULLMODE, 0);
}

void lcd_write(char c)
{
	lcd_op(c, LCD_FULLMODE, LCD_RS);
}

void lcd_puts(const char *s)
{
	while (*s)
		lcd_write(*s++);
}
