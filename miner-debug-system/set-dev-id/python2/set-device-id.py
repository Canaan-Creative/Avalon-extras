#!/usr/bin/env python
# Author Feb 2018 xuzhenxing <xuzhenxing@canaan-creative.com>

import serial
import logging
import sys

logging.basicConfig(level=logging.INFO)

# Opening the serial port
COM_PortName = "/dev/ttyUSB0"
COM_Port = serial.Serial(COM_PortName)  # Open the COM port
logging.debug('Com Port: %s, %s', COM_PortName, 'Opened')

COM_Port.baudrate = 2400                # Set Baud rate
COM_Port.bytesize = 8                   # Number of data bits = 8
COM_Port.parity   = 'N'                 # No parity
COM_Port.stopbits = 1                   # Number of Stop bits = 1

def rs485_read():
    read_data = []

    for i in range(8):
        rx_data = COM_Port.read()
        read_data.append(hex(ord(rx_data)))
    logging.info('Read Bytes: %s', read_data)

def rs485_write(data):
    bytes_cnt  = COM_Port.write(data)   # Write data to serial port
    logging.debug('Write Count = %d. %s ', bytes_cnt, 'bytes written')

# CRC16-MODBUS
def crc16_byte(data):
    crc = data

    for i in range(8):
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

if __name__ == '__main__':
    '''
    Device addr; func: read:0x03, write:0x10(16);
    MODBUS protocol read/write
    If write func is wrong, return 0xff
    CRCMODBUS protocol write:
    device-id, func, start-reg-hi, start-reg-lo, data-reg-hi, data-reg-lo, bytecount, value-hi, value-lo, crc-lo, crc-hi
    '''
    data = [0x00, 0x10, 0x00, 0x15, 0x00, 0x01, 0x02, 0x00, 0x03]

    current_device_id = raw_input("Please input current device ID: ")
    data[0] = int(current_device_id)

    device_id = raw_input("Please input setting device ID (1 ~ 247): ")
    if (int(device_id) >= 1) and (int(device_id) <= 247):
        data[7] = int(device_id)
    else:
        logging.info("Device ID is invaild.")
        sys.exit()

    crc = crc16_bytes(data)
    low = int(crc & 0xff)
    high = int((crc >> 8) & 0xff)
    data.append(low)
    data.append(high)
    logging.debug('%s', data)

    rs485_write(data)
    rs485_read()

    logging.info("Setting Device ID success, new device ID is %d", data[7])
    COM_Port.close()
