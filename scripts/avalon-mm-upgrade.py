#!/usr/bin/env python2.7
# Depends: crcmod (https://pypi.python.org/pypi/crcmod/1.7)
# Create IRAM/DRAM use following command first,save to the same
# place with this script,then run this script
#
# sed -n '14,456p' mm.mem | sed 's/ *//g' | tr -d '\n' > IRAM
# sed -n '462,print ' mm.mem | sed 's/ *//g' | tr -d '\n' > DRAM

import crcmod.predefined
from serial import Serial
from optparse import OptionParser
import binascii
import sys

CMD_RUN="22222222"
CMD_WRITE="11111111"
CMD_RESET="33333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333"

def send_cmd(uart, cmd):
	#print("Send cmd:" + cmd)
	uart.flushInput()
	uart.write(cmd.decode('hex'))

def send_data(uart, data):
	#print("Send data:" + data)
	uart.flushInput()
	uart.write(data.decode('hex'))

def read_crc(uart):
    	crc = uart.read(1)
	print("Ack crc:" + binascii.hexlify(crc))
	return binascii.hexlify(crc)

def read_bin(ramfile):
    f = open(ramfile, 'r')
    ram = f.readline()
    f.close()
    return ram

parser = OptionParser()
parser.add_option("-s", "--serial", dest="serial_port", default="/dev/ttyUSB0", help="Serial port")

(options, args) = parser.parse_args()
ser = Serial(options.serial_port, 57600, 8, timeout=2) # 2 second

send_cmd(ser, CMD_WRITE)
crc8_func = crcmod.predefined.mkCrcFun('crc-8')

IRAM = read_bin("./IRAM")
padsize = 32768 * ((len(IRAM) / 32768) + 1)
IRAMHEX = IRAM.ljust(padsize, '0')

DRAM = read_bin("./DRAM")
padsize = 32768 * ((len(DRAM) / 32768) + 1)
DRAMHEX = DRAM.ljust(padsize, '0')

# upgrade iram
retrymax=3
retrytimes=0
mmupdate=False
while True:
    if retrytimes == retrymax:
	print("Retry failed!")
	break

    send_data(ser, IRAMHEX)
    send_data(ser, DRAMHEX)
    print("Wait mm crc8:" + hex(crc8_func(IRAMHEX+DRAMHEX)))

    if read_crc(ser) == (hex(crc8_func(IRAMHEX+DRAMHEX))[2:]):
	mmupdate = True
	send_cmd(ser, CMD_RUN)
	break
    else:
	retrytimes = retrytimes + 1
	print("CRC read failed,retry again!")

if mmupdate == False:
    print("Upgrade mm failed :(")
else:
    print("Upgrade mm success :)")

ser.close()

