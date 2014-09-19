#!/usr/bin/env python2.7

# This simple script was for test Avalon nano.

from serial import Serial
from optparse import OptionParser
import binascii
import sys
import time

parser = OptionParser()
parser.add_option("-s", "--serial", dest="serial_port", default="/dev/ttyACM0", help="Serial port, default: /dev/ttyACM0")
parser.add_option("-S", "--static", dest="is_static", default="0", help="Static flag: 0-turn off, 1-turn on")
(options, args) = parser.parse_args()

ser = Serial(options.serial_port, 115200, 8, timeout=2)

TYPE_DETECT = "0a"
TYPE_WORK = "1c"

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
	return "4156" + cmd_type + idx + cnt + data + hex(crc)[2:].rjust(4, '0')

def run_detect(cmd):
	#version
	print cmd
	ser.write(cmd.decode('hex'))
	res_s = ser.read(39)
	if not res_s:
		print("ver:Something is wrong or modular id not correct")
	else :
		print("ver:" + res_s[5:20])

def run_testwork():
    cmd = mm_package(TYPE_WORK, '01', '02', None, "d8f8ef6712146495c44192c07145fd6d974bf4bb8f41371d65c90d1e9cb18a17")
    ser.write(cmd.decode('hex'))
    cmd = mm_package(TYPE_WORK, '02', '02', None, "0000000000000000000000000000000000000000087e051a885170504ac1d001")
    ser.write(cmd.decode('hex'))
    nonce = ser.read(39)
    print "Nonce is " + binascii.hexlify(nonce)[10:18]

def statics():
    start = time.time()
    for i in range(0, 1000):
        run_detect(mm_package(TYPE_DETECT, module_id = None))
    print "time elapsed: %s" %(time.time() - start)

while (1):
	print("Reading result ...")
        if options.is_static == '1':
            statics()
            break
        else:
            run_detect(mm_package(TYPE_DETECT, module_id = None))
	    run_testwork()
            raw_input('Press enter to continue:')
