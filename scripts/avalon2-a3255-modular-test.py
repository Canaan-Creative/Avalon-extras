#!/usr/bin/env python2.7

# This simple script was for test A3255 modular. there are 128 cores in one A3255 chip.
# If all cores are working the number should be 0.
# If some of them not working the number is the broken cores count.

from serial import Serial
from optparse import OptionParser
import binascii
import sys

parser = OptionParser()
parser.add_option("-s", "--serial", dest="serial_port", default="/dev/ttyUSB0", help="Serial port")
(options, args) = parser.parse_args()

ser = Serial(options.serial_port, 115200, 8, timeout=2)

cmd="415614010100000000000000000000000000000000000000000000000000000000000000000000"
#cmd="415614010100000000000000000000000000000000000000000000000000000000000000011021"
#cmd="415614010100000000000000000000000000000000000000000000000000000000000000022042"
while (1):
	print ("Reading result ...")
	ser.write(cmd.decode('hex'))
	count = 0
	while (1):
		res_s = ser.read(39)
		if not res_s:
			print(str(count) + ": Something is wrong or modular id not correct")
		else :
			result = binascii.hexlify(res_s)
			for i in range(0, 8):
				number = '{:03}'.format(int(result[11 + i:12 + i]))
				if (i == 0):
					sys.stdout.write(number + ":\t")
				else :
					sys.stdout.write(number + "\t")
				sys.stdout.flush()
			print("")

		count = count + 1
		if (count == 10):
			raw_input('Press enter to continue:')
			break
