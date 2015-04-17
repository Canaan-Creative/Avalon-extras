#!/usr/bin/env python2.7

# This simple script was for test Avalon nano.
import usb.core
import usb.util
from optparse import OptionParser
import binascii
import sys
import time

parser = OptionParser()
parser.add_option("-S", "--static", dest="is_static", default="0", help="Static flag: 0-turn off, 1-turn on")
(options, args) = parser.parse_args()

def enum_usbdev(vendor_id, product_id):
    # Find device
    usbdev = usb.core.find(idVendor = vendor_id, idProduct = product_id)

    if not usbdev:
        sys.exit("Avalon nano cann't be found!")
    else:
        print "Find an Avalon nano"

    if usbdev.is_kernel_driver_active(0) is True:
	usbdev.detach_kernel_driver(0)

    try:
	# usbdev[iConfiguration][(bInterfaceNumber,bAlternateSetting)]
        for endp in usbdev[0][(0,0)]:
            if endp.bEndpointAddress & 0x80:
                endpin = endp.bEndpointAddress
            else:
                endpout = endp.bEndpointAddress

    except usb.core.USBError as e:
        sys.exit("Could not set configuration: %s" % str(e))

    return usbdev, endpin, endpout

nano_vid = 0x29f1
nano_pid = 0x33f1
usbdev, endpin, endpout = enum_usbdev(nano_vid, nano_pid)

TYPE_DETECT = "10"
TYPE_REQUIRE = "15"
TYPE_WORK = "13"

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
	return "4156" + cmd_type + "00" + idx + cnt + data + hex(crc)[2:].rjust(4, '0')

def run_detect(cmd):
	#version
	usbdev.write(endpout, cmd.decode("hex"))
	try:
		res_s = usbdev.read(endpin, 40)
	except:
		print "detect failed"

	if not res_s:
		print("ver:Something is wrong or modular id not correct")
	else :
		hw =  ''.join([chr(x) for x in res_s])[6:21]
		print("ver:" + hw)

# 178ab19c1e0dc9651d37418fbbf44b976dfd4571c09241c49564141267eff8d8000000000000000000000000000000000000000001d0c14a507051881a057e08
# 010f0eb6
def run_testwork():
    cmd = mm_package(TYPE_WORK, '01', '02', None, "d8f8ef6712146495c44192c07145fd6d974bf4bb8f41371d65c90d1e9cb18a17")
    usbdev.write(endpout, cmd.decode("hex"))
    cmd = mm_package(TYPE_WORK, '02', '02', None, "0000000000000000000000000000000000000000087e051a885170504ac1d001")
    usbdev.write(endpout, cmd.decode("hex"))

    nonce = None
    loop = 0
    while (nonce == None):
	try:
            nonce = usbdev.read(endpin, 40)
	except:
	    pass

        time.sleep(0.01)
	loop = loop + 1
	if loop == 3:
		break

    if nonce != None:
	    if nonce[2] == 0x24:
		    freq = (nonce[6] << 24) | (nonce[7] << 16) | (nonce[8] << 8) | (nonce[9])

		    print "Status: Freq is", freq, "Mhz"
	    else:
		    print "Nonce is " + binascii.hexlify(nonce)[12:20]
    else:
	print "Nonce is None"

def run_require(cmd):
	usbdev.write(endpout, cmd.decode("hex"))
	time.sleep(0.05)
	res_s = None
	try:
		res_s = usbdev.read(endpin, 40)
	except:
		print "require failed"

	if res_s:
		# format: freq(120), temp(40), hot(0)
		avalon_require = binascii.hexlify(res_s)
		freq = int(avalon_require[10:18], 16)
		freq = (((freq << 24) & 0xff000000) | ((freq >> 24) & 0xff) | ((freq >> 8) & 0xff00) | ((freq << 8) & 0xff0000))
		temp = int(avalon_require[18:26], 16)
		temp = (((temp << 24) & 0xff000000) | ((temp >> 24) & 0xff) | ((temp >> 8) & 0xff00) | ((temp << 8) & 0xff0000))
		hot = int(avalon_require[26:34], 16)
		hot = (((hot << 24) & 0xff000000) | ((hot >> 24) & 0xff) | ((hot >> 8) & 0xff00) | ((hot << 8) & 0xff0000))
		result = "freq(" + str(freq) + "), "
		result = result + "temp(" + str(temp) + "), "
		result = result + "hot(" + str(hot) + ")"
		print(result)

def statics():
    start = time.time()
    for i in range(0, 1000):
        run_detect(mm_package(TYPE_DETECT, module_id = None))
    print "time elapsed: %s" %(time.time() - start)


if __name__ == '__main__':
        while (1):
            print("Reading result ...")
            if options.is_static == '1':
                statics()
                break
            else:
                run_detect(mm_package(TYPE_DETECT, module_id = None))
                run_require(mm_package(TYPE_REQUIRE, module_id = None))
                run_testwork()
                raw_input('Press enter to continue:')
