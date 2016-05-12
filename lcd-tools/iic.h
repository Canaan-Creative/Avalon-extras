/*
 * @brief iic head file
 *
 * @note
 *
 * @par
 */

#ifndef __IIC_H_
#define __IIC_H_

#include <stdint.h>

void iic_init(void);
void iic_start(void);
void iic_stop(void);
void iic_write(uint8_t data);
uint8_t iic_read(void);

#endif /* __IIC_H_ */
