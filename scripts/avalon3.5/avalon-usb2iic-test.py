#!/usr/bin/env python2.7

# This script aim to make a loopback test on cdc or hid.
# The statics is used for comparison, it is not accurate.

from serial import Serial
from optparse import OptionParser
import time
import binascii
import usb.core
import usb.util
import sys

parser = OptionParser()
parser.add_option("-M", "--Mode", dest="run_mode", default="0", help="Run Mode:0-CDC,1-HID; default:0")
(options, args) = parser.parse_args()

LOOP_CNT = 1

def statics(run_mode):
    tmp_dat = ""
    raw_dat = ""
    start = time.time()
    for i in range(62):
        tmp_dat += '{:02}'.format(i)

    for i in range(0, LOOP_CNT):
        raw_dat = tmp_dat + '{:02}'.format(64 - (i % 64))
        if run_mode == '0':
            ser.write(raw_dat.decode('hex'))
            res_s = ser.read(64)
        else:
            hiddev.write(endpout, raw_dat.decode('hex'))
            res_s = hiddev.read(endpin, 64)

        if raw_dat != binascii.hexlify(res_s):
            print "Failed:" + str(i)
            print "TX:" + raw_dat
            print "RX:" + binascii.hexlify(res_s)

    print "STATICS Begin"
    print "  Run %s times" %LOOP_CNT
    print "  Time elapsed: %s" %(time.time() - start)
    print "STATICS End"

def enum_usbhid(vendor_id, product_id):
    # Find device
    hiddev = usb.core.find(idVendor = vendor_id, idProduct = product_id)

    if not hiddev:
        sys.exit("No Avalon hid dev can be found!")
    else:
        print "Find an Avalon hid dev"
        if hiddev.is_kernel_driver_active(0):
            try:
                hiddev.detach_kernel_driver(0)
            except usb.core.USBError as e:
                sys.exit("Could not detach kernel driver: %s" % str(e))
    try:
        hiddev.set_configuration()
        hiddev.reset()
        for endp in hiddev[0][(0,0)]:
            if endp.bEndpointAddress & 0x80:
                endpin = endp.bEndpointAddress
            else:
                endpout = endp.bEndpointAddress

    except usb.core.USBError as e:
        sys.exit("Could not set configuration: %s" % str(e))

    return hiddev, endpin, endpout

if __name__ == '__main__':
    if options.run_mode == '0':
        ser = Serial("/dev/ttyACM0", 115200, 8, timeout=0.005)
    else:
        hid_vid = 0x29f1
        hid_pid = 0x33f2
        hiddev, endpin, endpout = enum_usbhid(hid_vid, hid_pid)

    statics(options.run_mode)

