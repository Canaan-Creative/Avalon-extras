#!/usr/bin/env python2.7

from serial import Serial
from optparse import OptionParser
import binascii
import sys

parser = OptionParser()
parser.add_option("-s", "--serial", dest="serial_port", default="/dev/ttyACM0", help="Serial port")
parser.add_option("-d", "--data", dest="data", default="d8f8ef6712146495c44192c07145fd6d974bf4bb8f41371d65c90d1e9cb18a170000000000000000000000000000000000000000087e051a885170504ac1d001", help="Testing data")
parser.add_option("-n", "--nonce", dest="nonce", default="null", help="nonce")

(options, args) = parser.parse_args()

ser = Serial(options.serial_port, 57600, 8, timeout=2) # 2 second
payload = options.data

print("Push payload to device: " + payload)
ser.flushInput()
ser.write(payload.decode('hex'))

#read more data(nonce and test dat)
res=ser.read(100)

ret=1
if binascii.hexlify(res)[0:8] == options.nonce:
    ret=0
else:
    if binascii.hexlify(res)[0:8] == "" and options.nonce == "null":
	ret=0

if ret == 0:
    print("Result: " + binascii.hexlify(res))
    print("Nonce:  " + options.nonce)
    sys.exit(0)
else:
    print("\033[0;31mResult: " + binascii.hexlify(res) + "\033[0m")
    print("Nonce:  " + options.nonce)
    sys.exit(1)

