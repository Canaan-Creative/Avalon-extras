#!/usr/bin/env python2.7

# This simple script was for test A3255 modular. there are 128 cores in one A3255 chip.
# If all cores are working the number should be 0.
# If some of them not working the number is the broken cores count.

from serial import Serial
from optparse import OptionParser
import binascii
import sys
import time

parser = OptionParser()
parser.add_option("-s", "--serial", dest="serial_port", default="/dev/ttyUSB0", help="Serial port, default: /dev/ttyUSB0")
parser.add_option("-t", "--type", dest="chip_type", default="3", help="Module type should be: 2 or 3")
parser.add_option("-m", "--module", dest="module_id", default="0", help="Module ID: 0 - 3")
parser.add_option("-S", "--static", dest="is_static", default="0", help="Static flag: 0-turn off, 1-turn on")
(options, args) = parser.parse_args()

if options.chip_type == '2':
	asic_cnt = 7
	miner_cnt = 10
	ser = Serial(options.serial_port, 115200, 8, timeout=2)
else:
	asic_cnt = 10
	miner_cnt = 5
	ser = Serial(options.serial_port, 115200, 8, timeout=8)

TYPE_TEST = "14"
TYPE_DETECT = "0a"
TYPE_REQUIRE = "12"

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

def mm_package(cmd_type, module_id):
	data = "000000000000000000000000000000000000000000000000000000000000" + module_id.rjust(4, '0')
	crc = CRC16(data.decode("hex"))
	return "4156" + cmd_type + "0101" + data + hex(crc)[2:].rjust(4, '0')

def run_test(cmd):
	ser.write(cmd.decode('hex'))
	for count in range(0, miner_cnt):
		res_s = ser.read(39)
		if not res_s:
			print(str(count) + ": Something is wrong or modular id not correct")
		else :
			result = binascii.hexlify(res_s)
			for i in range(0, asic_cnt+1):
				number = '{:03}'.format(int(result[10 + i * 2:12 + i * 2], 16))
				if (i == 0):
					sys.stdout.write(number + ":\t")
				else :
					sys.stdout.write(number + "\t")
				sys.stdout.flush()
			print("")

def run_detect(cmd):
	#version
	ser.write(cmd.decode('hex'))
	res_s = ser.read(39)
	if not res_s:
		print("ver:Something is wrong or modular id not correct")
	else :
		print("ver:" + res_s[5:20])


def run_require(cmd):
	ser.write(cmd.decode('hex'))
	res_s = ser.read(39)
	if not res_s:
		print("status:Something is wrong or modular id not correct")
	else :
		# format: temp(40|50), fan(20|30), freq(300), vol(400), localwork(1), g_hw_work(300), pg(0)
		avalon_require = binascii.hexlify(res_s)
		temp1 = int(avalon_require[10:14], 16)
		temp2 = int(avalon_require[14:18], 16)
		fan1 = int(avalon_require[18:22], 16)
		fan2 = int(avalon_require[22:26], 16)
		freq = int(avalon_require[26:34], 16)
		vol = int(avalon_require[34:42], 16)
		localwork = int(avalon_require[42:50], 16)
		g_hw_work = int(avalon_require[50:58], 16)
		pg = int(avalon_require[58:66], 16)
		result = "status:temp(" + str(temp1) + "," + str(temp2) + "), "
		result = result + "fan1(" + str(fan1) + "," + str(fan2) + "), "
		result = result + "freq(" + str(freq) + "), "
		result = result + "vol(" + str(vol) + "), "
		result = result + "localwork(" + str(localwork) + "), "
		result = result + "g_hw_work(" + str(g_hw_work) + "), "
		result = result + "pg(" + str(pg) + ")"
		print(result)

def statics():
    start = time.time()
    for i in range(0, 1000):
        run_detect(mm_package(TYPE_DETECT, options.module_id))
    print "time elapsed: %s" %(time.time() - start)

while (1):
	print("Reading result ...")
	print("module id:" + options.module_id)
        if options.is_static == '1':
            statics()
            break
        else:
            run_detect(mm_package(TYPE_DETECT, options.module_id))
            run_require(mm_package(TYPE_REQUIRE, options.module_id))
            run_test(mm_package(TYPE_TEST, options.module_id))
            run_require(mm_package(TYPE_REQUIRE, options.module_id))
            run_require(mm_package(TYPE_REQUIRE, options.module_id))
            raw_input('Press enter to continue:')
