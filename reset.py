#!/usr/bin/env python2.7

from serial import Serial
from optparse import OptionParser
import binascii


parser = OptionParser()
parser.add_option("-s", "--serial", dest="serial_port", default="/dev/ttyUSB0", help="Serial port")
(options, args) = parser.parse_args()

ser = Serial(options.serial_port, 19200, 8)

cmd = "0100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
print("Push reset to device:\n" + cmd)
ser.write(cmd.decode('hex'))

res=ser.read(56)
print("Result:\n" + binascii.hexlify(res))
