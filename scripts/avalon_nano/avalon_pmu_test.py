#!/usr/bin/env python2.7

from __future__ import division
from serial import Serial
from optparse import OptionParser
import binascii
import sys

parser = OptionParser()
parser.add_option("-s", "--serial", dest="serial_port", default="/dev/ttyUSB0", help="Serial port")
(options, args) = parser.parse_args()

ser = Serial(options.serial_port, 115200, 8, timeout=1) # 1 second
input_data = ""

def CRC16(message):
	#CRC-16-CITT poly, the CRC sheme used by ymodem protocol
	poly = 0x1021
	#16bit operation register, initialized to zeros
	reg = 0x0000
	#pad the end of the message with the size of the poly
	message += '\x00\x00'
	#for each bit in the message
	for byte in message:
		mask = 0x80
		while(mask > 0):
			#left shift by one
			reg<<=1
			#input the next bit from the message into the right hand side of the op reg
			if ord(byte) & mask:
				reg += 1
			mask>>=1
			#if a one popped out the left of the reg, xor reg w/poly
			if reg > 0xffff:
				#eliminate any one that popped out the left
				reg &= 0xffff
				#xor with the poly, this is the remainder
				reg ^= poly
	return reg

def mm_package(cmd_type, idx = "01", cnt = "01", module_id = None, pdata = '0'):
	if module_id == None:
		data = pdata.ljust(64, '0')
	else:
		data = pdata.ljust(60, '0') + module_id.rjust(4, '0')
	crc = CRC16(data.decode("hex"))
	return "434E" + cmd_type + "00" + idx + cnt + data + hex(crc)[2:].rjust(4, '0')

# AVAM_P_SET_VOLT:
#    One Byte Input Voltage Value:
#    First Half Byte Is The Second Power
#    Last Half Byte Is The First Power
# AVAM_P_TEST:
#    First  Byte: 01 Open Power;  02 Close Power;  03 Power Resutl
#    Second Byte: 01 First Power; 02 Second Power; 03 First And Second Power
#    Third  Byte: Same As AVAM_P_SET_VOLT
print("\nCMD_TYPE: AVAM_P_DETECT/10 | AVAM_P_POLLING/30 | AVAM_P_SET_VOLT/22 | AVAM_P_TEST/32\n")
input_cmd_type = raw_input("Please Input CMD_TYPE: ")

if (input_cmd_type != "10" and input_cmd_type != "30" and input_cmd_type != "22" and input_cmd_type != "32"):
	print("Input CMD_TYPE Error! \n")

if (input_cmd_type == "22"):
	input_data = raw_input("Please Input Voltage Value: ")

if (input_cmd_type == "32"):
	input_data = raw_input("Please Input Instructoin And Data: ")

input_str = mm_package(input_cmd_type, module_id = None, pdata = input_data)
print("Send Data: " +  input_str)

ser.flushInput()
ser.write(input_str.decode('hex'))

#read more data(nonce and test dat)
res=ser.readall()

if (input_cmd_type == "10"):
	print("AVAM_VERSION: " + res[14:29])
	print("Rece Data: " + binascii.hexlify(res))

if (input_cmd_type == "30"):
	print("NTC1:   " + '%d' %int(binascii.hexlify(res[6:8]), 16))
	print("NTC2:   " + '%d' %int(binascii.hexlify(res[8:10]), 16))
	a = int(binascii.hexlify(res[10:12]), 16)/1024.0 * 3.3 * 11
	print("V12-1:  " + '%.2f' %a)
	a = int(binascii.hexlify(res[12:14]), 16)/1024.0 * 3.3 * 11
	print("V12-2:  " + '%.2f' %a)
	a = int(binascii.hexlify(res[14:16]), 16)/1024.0 * 3.3 * 11
	print("VCORE1: " + '%.2f' %a)
	a = int(binascii.hexlify(res[16:18]), 16)/1024.0 * 3.3 * 11
	print("VCORE2: " + '%.2f' %a)
	a = binascii.hexlify(res[18:19])
	if (a == "00"):
		print("PG1 Good")
		print("PG2 Good")
	if (a == "01"):
		print("PG1 Bad")
		print("PG2 Good")
	if (a == "02"):
		print("PG1 Good")
		print("PG2 Bad")
	if (a == "03"):
		print("PG1 Bad")
		print("PG2 Bad")
	print("Rece Data: " + binascii.hexlify(res))

sys.exit(0)
