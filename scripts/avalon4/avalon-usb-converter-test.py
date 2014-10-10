#!/usr/bin/env python2.7

# This simple script was for test A3255 modular. there are 128 cores in one A3255 chip.
# If all cores are working the number should be 0.
# If some of them not working the number is the broken cores count.
# Note: Avalon 3.5 use usb2iic instead of uart, the usb2iic bridge expose cdc api to app.
# Depends : PyUSB 1.0 (Under Linux)
# PyUSB 1.0 Installation: https://github.com/walac/pyusb
#
#  bridge format: length[1]+transId[1]+sesId[1]+req[1]+data[60]
#  length: 4+len(data)
#  transId: 0
#  sesId: 0
#  req:
#        a0:RESET
#        a1:INIT
#        a2:DEINIT
#        a3:WRITE
#        a4:READ
#        a5:XFER
#  data: the actual payload
#        clockRate[4] + reserved[4] + payload[52] when init
#
#        xparam[4] + payload[56] when write
#            xparam: txSz[1]+rxSz[1]+options[1]+slaveAddr[1]
#
#        payload[60] when read
#

from optparse import OptionParser
import time
import binascii
import usb.core
import usb.util
import sys

parser = OptionParser()
# TODO: Module id assignment
parser.add_option("-m", "--module", dest="module_id", default="0", help="Module ID: 0 - 127, default:0")
parser.add_option("-c", "--count", dest="test_count", default="1", help="Test count: 1,2,3... ")
parser.add_option("-f", "--fastxfer", dest="fast_xfer", default="0", help="Fast Xfer switch 0-OFF/1-ON, default:0")
(options, args) = parser.parse_args()

asic_cnt = 10
miner_cnt = 5

def statics(usbdev, endpin, endpout):
    start = time.time()
    for i in range(0, int(options.test_count)):
        run_detect(usbdev, endpin, endpout, mm_package(TYPE_DETECT, module_id = options.module_id))
    print "time elapsed: %s" %(time.time() - start)

def enum_usbdev(vendor_id, product_id):
    # Find device
    usbdev = usb.core.find(idVendor = vendor_id, idProduct = product_id)

    if not usbdev:
        sys.exit("No Avalon USB Converter can be found!")
    else:
        print "Find an Avalon USB Converter"
        if usbdev.is_kernel_driver_active(0):
            try:
                usbdev.detach_kernel_driver(0)
            except usb.core.USBError as e:
                sys.exit("Could not detach kernel driver: %s" % str(e))
    try:
        usbdev.set_configuration()
        usbdev.reset()

	# usbdev[iConfiguration][(bInterfaceNumber,bAlternateSetting)]
        for endp in usbdev[0][(1,0)]:
            if endp.bEndpointAddress & 0x80:
                endpin = endp.bEndpointAddress
            else:
                endpout = endp.bEndpointAddress

    except usb.core.USBError as e:
        sys.exit("Could not set configuration: %s" % str(e))

    return usbdev, endpin, endpout

# addr : iic slaveaddr
# req : see bridge format
# data: 40 bytes payload
def auc_req(usbdev, endpin, endpout, addr, req, data):
    req = req.rjust(2, '0')

    if req == 'a1':
        data = data.ljust(120, '0')
        datalen = 12
        txdat = hex(datalen)[2:].rjust(2, '0') + \
                "0000" +    \
                req +   \
                data
        usbdev.write(endpout, txdat.decode("hex"))

    if req == 'a3':
        data = data.ljust(112, '0')
        datalen = 8 + len(data)
        txdat = hex(datalen)[2:].rjust(2, '0') +    \
                "0000" +    \
                "a3" + \
                "280000" +  \
                addr.rjust(2, '0') +    \
                data
        usbdev.write(endpout, txdat.decode("hex"))
        usbdev.read(endpin, 64)

    if req == 'a4':
        datalen = 8
        txdat = hex(datalen)[2:].rjust(2, '0') +    \
                "0000" +    \
                "a4" + \
                "002800" +  \
                addr.rjust(2, '0') +    \
                "0".ljust(112, '0')
        usbdev.write(endpout, txdat.decode("hex"))

    if req == 'a5':
        if options.fast_xfer == '1':
            data = data.ljust(112, '0')
            datalen = 8 + len(data)
            txdat = hex(datalen)[2:].rjust(2, '0') +    \
                    "0000" +    \
                    "a5" + \
                    "282800" +  \
                    addr.rjust(2, '0') +    \
                    data
            usbdev.write(endpout, txdat.decode("hex"))
        else:
            data = data.ljust(112, '0')
            datalen = 8 + len(data)
            txdat = hex(datalen)[2:].rjust(2, '0') +    \
                    "0000" +    \
                    "a5" + \
                    "280000" +  \
                    addr.rjust(2, '0') +    \
                    data
            usbdev.write(endpout, txdat.decode("hex"))
            usbdev.read(endpin, 64)

            datalen = 8
            txdat = hex(datalen)[2:].rjust(2, '0') +    \
                    "0000" +    \
                    "a5" + \
                    "002800" +  \
                    addr.rjust(2, '0') +    \
                    "0".ljust(112, '0')
            usbdev.write(endpout, txdat.decode("hex"))

def auc_read(usbdev, endpin):
    ret = usbdev.read(endpin, 64)
    if ret[0] > 4:
        return ret[4:ret[0]]
    else:
        return None

def auc_xfer(usbdev, endpin, endpout, addr, req, data):
    auc_req(usbdev, endpin, endpout, addr, req, data)
    return auc_read(usbdev, endpin)


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

def mm_package(cmd_type, idx = "01", cnt = "01", module_id = None, pdata = '0'):
	if module_id == None:
	    data = pdata.ljust(64, '0')
	else:
	    data = pdata.ljust(60, '0') + module_id.rjust(4, '0')
	crc = CRC16(data.decode("hex"))
	return "4156" + cmd_type + idx + cnt + data + hex(crc)[2:].rjust(4, '0')

def run_test(usbdev, endpin, endpout, cmd):
        auc_req(usbdev, endpin, endpout, "00", "a3", cmd)
	for count in range(0, miner_cnt):
                while True:
                    auc_req(usbdev, endpin, endpout, "00", "a4", cmd)
                    res_s = auc_read(usbdev, endpin)
                    if res_s != None:
                        break

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


def run_detect(usbdev, endpin, endpout, cmd):
	#version
        res_s = auc_xfer(usbdev, endpin, endpout, "00", "a5", cmd)
	if not res_s:
		print("ver:Something is wrong or modular id not correct")
	else :
		print("ver:" + ''.join([chr(x) for x in res_s])[3:20])

def run_require(usbdev, endpin, endpout, cmd):
        res_s = auc_xfer(usbdev, endpin, endpout, "00", "a5", cmd)
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


def run_modular_test(usbdev, endpin, endpout):
    while True:
        print("Reading result ...")
        run_detect(usbdev, endpin, endpout, mm_package(TYPE_DETECT, module_id = options.module_id))
        run_require(usbdev, endpin, endpout, mm_package(TYPE_REQUIRE, module_id = options.module_id))
        raw_input('Press enter to continue:')

if __name__ == '__main__':
    auc_vid = 0x29f1
    auc_pid = 0x33f2
    usbdev, endpin, endpout = enum_usbdev(auc_vid, auc_pid)

    ret = auc_xfer(usbdev, endpin, endpout, "00", "a1", "40420f00")
    if ret:
        print "AUC version: " +  ''.join([chr(x) for x in ret])
    else:
        print "AUC version null"

    statics(usbdev, endpin, endpout)

