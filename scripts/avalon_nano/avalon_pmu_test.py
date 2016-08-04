#!/usr/bin/env python2.7

from __future__ import division
from serial import Serial
from optparse import OptionParser
import binascii
import sys
import time

parser = OptionParser()
parser.add_option("-s", "--serial", dest="serial_port", default="/dev/ttyUSB0", help="Serial port")
parser.add_option("-c", "--choose", dest="is_rig", default="1", help="1 Is For Rig Testing")
(options, args) = parser.parse_args()

ser = Serial(options.serial_port, 115200, 8, timeout=1) # 1 second

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

def show_help():
	print("\
h: help\n\
1: detect the pmu version\n\
2: set	  the pmu output voltage\n\
	  0100: close the voltage output\n\
	  0000: 7.00V\n\
	  0011: 7.14V\n\
	  0022: 7.28V\n\
	  0033: 7.42V\n\
	  0044: 7.56V\n\
	  0055: 7.70V\n\
	  0066: 7.84V\n\
	  0077: 7.98V\n\
	  0088: 8.12V\n\
	  0099: 8.26V\n\
	  00AA: 8.40V\n\
	  00BB: 8.54V\n\
	  00CC: 8.68V\n\
	  00DD: 8.82V\n\
	  00EE: 8.96V\n\
	  00FF: 9.10V\n\
3: get	  the voltage and temperature\n\
4: test	  the process of power on\n\
q: quit\n")

def judge_vol_range(vol):
	if (len(vol) != 4):
		return False
	if ((vol[0:2] != "00") and (vol[0:2] != "01")):
		return False
	try:
		binascii.a2b_hex(vol[2:4])
	except:
		return False
	return True

def detect_version():
	input_str = mm_package("10", module_id = None)
	ser.flushInput()
	ser.write(input_str.decode('hex'))
	res=ser.readall()
	print("AVAM_VERSION: " + res[14:29])

def set_voltage(vol_value):
	if (judge_vol_range(vol_value)):
		input_str = mm_package("22", module_id = None, pdata = vol_value);
		ser.flushInput()
		ser.write(input_str.decode('hex'))
		time.sleep(1)
	else:
		print("Bad voltage vaule!")

def get_voltage_tem():
	input_str = mm_package("30", module_id = None);
	ser.flushInput()
	ser.write(input_str.decode('hex'))

	res=ser.readall()
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

# TODO : finish this test_init_process fuction
def test_init_process():
	print("Please Waiting, PMU Init Process Is Testing\n")
	input_str = mm_package("32", module_id = None, pdata = '0103ff')
	ser.flushInput()
	ser.write(input_str.decode('hex'))
	input_str = mm_package("30", module_id = None, pdata = '0')
	ser.flushInput()
	ser.write(input_str.decode('hex'))
	res=ser.readall()
	a1 = int(binascii.hexlify(res[10:12]), 16)/1024.0 * 3.3 * 11
	a2 = int(binascii.hexlify(res[12:14]), 16)/1024.0 * 3.3 * 11
	c1 = int(binascii.hexlify(res[14:16]), 16)/1024.0 * 3.3 * 11
	c2 = int(binascii.hexlify(res[16:18]), 16)/1024.0 * 3.3 * 11
	cz = ''
	if (abs(a2 - 12) > 1):
		cz += '1'
	else:
		cz += '0'
	if (abs(a1 - 12) > 1):
		cz += '1'
	else:
		cz += '0'
	input_str = mm_package("32", module_id = None, pdata = "04" + "03" + cz)
	ser.flushInput()
	ser.write(input_str.decode('hex'))
	input_str = mm_package("32", module_id = None, pdata = "0203")
	ser.flushInput()
	ser.write(input_str.decode('hex'))
	print("V12-1:  " + '%.2f' %a1)
	print("V12-2:  " + '%.2f' %a2)

def test_polling():
	while (1):
		h = raw_input("Please input(1-4), h for help:")
		if ((h == 'h') or (h == 'H')):
			show_help()
		elif ((h == 'q') or (h == 'Q')):
			sys.exit(0)
		elif (h == '1'):
			detect_version()
		elif (h == '2'):
			vol = raw_input("Please input the voltage:")
			set_voltage(vol)
		elif (h == '3'):
			get_voltage_tem()
		elif (h == '4'):
			test_init_process()
		else:
			show_help()

if __name__ == '__main__':
	while (1):
		if (options.is_rig == '1'):
			detect_version()
			set_voltage("00AA")
			get_voltage_tem()
		elif (options.is_rig == '0'):
			test_polling()
		raw_input('Press Enter to continue')
