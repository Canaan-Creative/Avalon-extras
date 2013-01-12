#!/usr/bin/env python2.7

from serial import Serial
from optparse import OptionParser
import binascii


parser = OptionParser()
parser.add_option("-s", "--serial", dest="serial_port", default="/dev/ttyUSB0", help="Serial port")
(options, args) = parser.parse_args()

ser = Serial(options.serial_port, 19200, 8)

payload = "1c4027010000000000000000178ab19c1e0dc9651d37418fbbf44b976dfd4571c09241c49564141267eff8d801d0c14a507051881a057e08"
#result 010f0eb6

####
# 1c4027010100000000000000178ab19c1e0dc9651d37418fbbf44b976dfd4571c09241c49564141267eff8d801d0c14a507051891a057e0800000000
# nonce=1bbe7ba0
####
# 1c4027030100000000000000178ab19c1e0dc9651d37418fbbf44b976dfd4571c09241c49564141267eff8d801d0c14a5070518c1a057e0800000000
# nonce=c95d88ca
####

print("Push payload to device:\n" + payload)
ser.write(payload.decode('hex'))

res=ser.read(56)
print("Result:\n" + binascii.hexlify(res))
