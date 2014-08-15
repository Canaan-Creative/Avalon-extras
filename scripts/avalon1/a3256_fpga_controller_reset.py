#!/usr/bin/env python2.7

from serial import Serial
from optparse import OptionParser
import binascii


parser = OptionParser()
parser.add_option("-s", "--serial", dest="serial_port", default="/dev/ttyUSB0", help="Serial port")
(options, args) = parser.parse_args()

ser = Serial(options.serial_port, 115200, 8)

cmd = "ad98320801000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000009999991932333333cbcccc4c64666666fdffff7f969999992f3333b3c8cccccc616666e6"

print("Push reset to device:\n" + cmd)
ser.write(cmd.decode('hex'))

res=ser.read(64)
print("Result:\n" + binascii.hexlify(res))
