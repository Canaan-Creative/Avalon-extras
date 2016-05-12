/*
 * @brief gpio head file
 *
 * @note
 *
 * @par
 */

#ifndef __GPIO_H_
#define __GPIO_H_

#define GPIO_DIR_IN	0
#define GPIO_DIR_OUT	1

int gpio_init_port(void);
int gpio_setsda_dir(int dir);
int gpio_setsda_val(int val);
int gpio_getsda_val(void);
int gpio_setscl_dir(int dir);
int gpio_setscl_val(int val);
int gpio_deinit_port(void);

#endif /* __GPIO_H_ */
