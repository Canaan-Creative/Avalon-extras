#!/usr/bin/env python2.7

from serial import Serial
from optparse import OptionParser
import binascii

parser = OptionParser()
parser.add_option("-s", "--serial", dest="serial_port", default="/dev/ttyACM0", help="Serial port")
parser.add_option("-d", "--data", dest="data", default="178ab19c1e0dc9651d37418fbbf44b976dfd4571c09241c49564141267eff8d8000000000000000000000000000000000000000001d0c14a507051881a057e08", help="Testing data")

(options, args) = parser.parse_args()

ser = Serial(options.serial_port, 115200, 8, timeout=0.6) # 0.6 second
payload = options.data

print("Push payload to device: " + payload)
ser.write(payload.decode('hex'))

res=ser.read(4)
print("Result: " + binascii.hexlify(res))
