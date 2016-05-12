/*
 * @brief lcd head file
 *
 * @note
 *
 * @par
 */

#ifndef __LCD_H_
#define __LCD_H_

#include <stdint.h>

void lcd_init(void);
void lcd_on(void);
void lcd_off(void);
void lcd_clear(void);
void lcd_home(void);
void lcd_setcursor(uint8_t col, uint8_t row);
void lcd_leftscroll(void);
void lcd_rightscroll(void);
void lcd_write(char c);
void lcd_puts(const char *s);

#endif /* __LCD_H_ */

