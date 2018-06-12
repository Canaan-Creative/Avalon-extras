#!/usr/bin/env python
#
# USBTORS485 Converter, Y-1081 USB2.0 to RS485 Converter(FT232 Chip)
# lllking: DDS238-2 ZN/S
# Author Feb 2018 Zhenxing Xu <xuzhenxing@canaan.creative.com>
#
# /dev/ttyUSB0 permission
# Add /etc/udev/rules.d/99-plugdev.rules
# 99-plugdev.rules: ATTRS{idVendor}=="1d6b", ATTRS{idProduct}=="0002", SUBSYSTEMS=="usb", ACTION=="add", MODE="0666", GROUP="plugdev"
#

import logging
import serial
import time
import sys

logging.basicConfig(level=logging.INFO)

# Opening the serial port
COM_PortName = "/dev/ttyUSB0"
COM_Port = serial.Serial(COM_PortName, timeout = 1)  # Open the COM port
logging.debug('Com Port: %s, %s', COM_PortName, 'Opened')

COM_Port.baudrate = 2400                # Set Baud rate
COM_Port.bytesize = 8                   # Number of data bits = 8
COM_Port.parity   = 'N'                 # No parity
COM_Port.stopbits = 1                   # Number of Stop bits = 1

# CRC16-MODBUS
def crc16_byte(data):
    crc = data

    for k in range(8):
        if (crc & 0x01):
            crc = (crc >> 1) ^ 0xa001
        else:
            crc >>= 1

    return crc

def crc16_bytes(data):
    crc = 0xffff

    for byte in data:
        crc = crc16_byte(crc ^ byte)

    return crc

def rs485_read():
    read_data = []
    tmp_data = []

    try:
        for n in range(7):
            rx_data = COM_Port.read()
            read_data.append(hex(ord(rx_data)))
        logging.debug('Read Bytes: %s', read_data)

        valid_data = (int(read_data[3], 16) << 8) | int(read_data[4], 16)

        read_crc = (int(read_data[6], 16) << 8) | int(read_data[5], 16)
        del read_data[5:7]
        for m in range(len(read_data)):
            tmp_data.append(int(read_data[m], 16))
        tmp_crc = crc16_bytes(tmp_data)
        if (read_crc != tmp_crc):
            valid_data = -1

        return valid_data
    except:
        return -1

def rs485_write(data):
    bytes_cnt  = COM_Port.write(data)   # Write data to serial port
    logging.debug('Write Count = %d. %s ', bytes_cnt, 'bytes written')

if __name__ == '__main__':
    path = "CGMiner_Power.log"

    '''
    Device addr; func: read:0x03, write:0x10(16);
    MODBUS protocol read/write
    CRCMODBUS protocol read:
    device-id, func, start-reg-hi, start-reg-lo, data-reg-hi, data-reg-lo, crc-lo, crc-hi
    '''
    data = [0x00, 0x03, 0x00, 0x0e, 0x00, 0x01]

    # Read miner power value to file
    power_file = open(path, 'w+')

    # Read power dev id range: 1 ~ 24
    for i in range(1, 25):
        data[0] = i
        crc = crc16_bytes(data)
        low = int(crc & 0xff)
        high = int((crc >> 8) & 0xff)
        data.append(low)
        data.append(high)
        logging.debug('%s', data)

        for j in range(0, 3):
            rs485_write(data)
            power_data = rs485_read()
            if (power_data > -1):
                break

        if (power_data < 30):
            del data[6:8]
            continue

        print('Device ID:%d, Power value:%d' % (i, power_data))
        power_file.write(str(power_data))
        power_file.write('\n')
        del data[6:8]
    COM_Port.close()
