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
	  0000: close the voltage output\n\
	  8800: 7.00V\n\
	  8811: 7.14V\n\
	  8822: 7.28V\n\
	  8833: 7.42V\n\
	  8844: 7.56V\n\
	  8855: 7.70V\n\
	  8866: 7.84V\n\
	  8877: 7.98V\n\
	  8888: 8.12V\n\
	  8899: 8.26V\n\
	  88AA: 8.40V\n\
	  88BB: 8.54V\n\
	  88CC: 8.68V\n\
	  88DD: 8.82V\n\
	  88EE: 8.96V\n\
	  88FF: 9.10V\n\
3: set    the pmu led state\n\
          0000: all   led off\n\
          0101: green led on\n\
          0202: red   led on\n\
          1010: green led blink\n\
          2020: red   led blink\n\
4: get    the pmu state\n\
q: quit\n")

def judge_vol_range(vol):
	if (len(vol) != 4):
		return False
	if ((vol[0:2] != "00") and (vol[0:2] != "88") and (vol[0:2] != "80") and (vol[0:2] != "08")):
		return False
	try:
		binascii.a2b_hex(vol[2:4])
	except:
		return False
	return True

def judge_led_range(led):
	if (len(led) != 4):
		return False
	if ((led[0:1] != "0") and (led[2:3] != "0")):
		return False

	return True

def detect_version():
	input_str = mm_package("10", module_id = None)
	ser.flushInput()
	ser.write(input_str.decode('hex'))
	res=ser.readall()
        print("AVAM_DNA:" + binascii.hexlify(res[6:14]))
	print("AVAM_VERSION: " + res[14:29])

def set_voltage(vol_value):
	if (judge_vol_range(vol_value)):
		input_str = mm_package("22", module_id = None, pdata = vol_value);
		ser.flushInput()
		ser.write(input_str.decode('hex'))
		time.sleep(1)
	else:
		print("Bad voltage vaule!")

def set_led_state(led):
	if (judge_led_range(led)):
		input_str = mm_package("24", module_id = None, pdata = led);
		ser.flushInput()
		ser.write(input_str.decode('hex'))
		time.sleep(1)
	else:
		print("Bad led's state vaule!")

def get_pmu_state():
	input_str = mm_package("30", module_id = None);
	ser.flushInput()
	ser.write(input_str.decode('hex'))
        time.sleep(1);
	res=ser.readall()
	print("NTC1:   " + '%d' %int(binascii.hexlify(res[6:8]), 16))
	print("NTC2:   " + '%d' %int(binascii.hexlify(res[8:10]), 16))
	a = int(binascii.hexlify(res[10:12]), 16)
	print("V12-1:  " + '%.2f' %a)
	a = int(binascii.hexlify(res[12:14]), 16)
	print("V12-2:  " + '%.2f' %a)
	a = int(binascii.hexlify(res[14:16]), 16)
	print("VCORE1: " + '%.2f' %a)
	a = int(binascii.hexlify(res[16:18]), 16)
	print("VCORE2: " + '%.2f' %a)
	a = int(binascii.hexlify(res[18:20]), 16)
	print("VBASE:  " + '%.2f' %a)
	a = binascii.hexlify(res[20:22])
	if (a == "0001"):
		print("PG1 Good")
	if (a == "0002"):
		print("PG1 Bad")
	a = binascii.hexlify(res[22:24])
	if (a == "0001"):
		print("PG2 Good")
	if (a == "0002"):
		print("PG2 Bad")
	a = binascii.hexlify(res[24:26])
	if (a == "0000"):
		print("LED1: all led off")
	if (a == "0001"):
		print("LED1: green led on")
	if (a == "0002"):
		print("LED1: red led on")
	if (a == "0003"):
		print("LED1: all led on")
	if (a == "0004"):
		print("LED1: green led blink")
	if (a == "0008"):
		print("LED1: red led blink")
	a = binascii.hexlify(res[26:28])
	if (a == "0000"):
		print("LED2: all led off")
	if (a == "0001"):
		print("LED2: green led on")
	if (a == "0002"):
		print("LED2: red led on")
	if (a == "0003"):
		print("LED2: all led on")
	if (a == "0004"):
		print("LED2: green led blink")
	if (a == "0008"):
		print("LED2: red led blink")

def get_pmu_state_vol():
	input_str = mm_package("30", module_id = None);
	ser.flushInput()
	ser.write(input_str.decode('hex'))

	res=ser.readall()
	print("NTC1:   " + '%d' %int(binascii.hexlify(res[6:8]), 16))
	print("NTC2:   " + '%d' %int(binascii.hexlify(res[8:10]), 16))
	a = int(binascii.hexlify(res[10:12]), 16)
	print("V12-1:  " + '%.2f' %a)
	a = int(binascii.hexlify(res[12:14]), 16)
	print("V12-2:  " + '%.2f' %a)
	a = int(binascii.hexlify(res[14:16]), 16)
	print("VCORE1: " + '%.2f' %a)
	a = int(binascii.hexlify(res[16:18]), 16)
	print("VCORE2: " + '%.2f' %a)
	a = int(binascii.hexlify(res[18:20]), 16)
	print("VBASE:  " + '%.2f' %a)

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
			led = raw_input("Please input the led state:")
			set_led_state(led)
		elif (h == '4'):
                        get_pmu_state();
		else:
			show_help()

if __name__ == '__main__':
	while (1):
		if (options.is_rig == '1'):
			detect_version()
			set_voltage("88AA")
			get_pmu_state()
                        time.sleep(1)
		elif (options.is_rig == '0'):
			test_polling()
		elif (options.is_rig == '2'):
			get_pmu_state_vol()
                        time.sleep(1)
