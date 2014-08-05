#!/usr/bin/env python2.7

# This simple script was for test A3255 modular. there are 128 cores in one A3255 chip.
# If all cores are working the number should be 0.
# If some of them not working the number is the broken cores count.
# Note: Avalon 3.5 use usb2iic instead of uart, the usb2iic bridge expose hid api to app.
# Depends : PyUSB 1.0 (Under Linux)
# PyUSB 1.0 Installation: https://github.com/walac/pyusb
#
#  bridge format: length[1]+transId[1]+sesId[1]+req[1]+data[60]
#  length: 4+len(data)
#  transId: 0
#  sesId: 0
#  req:
#        0:RESET
#        1:INIT
#        2:DEINIT
#        3:WRITE
#        4:READ
#        5:XFER
#  data: the actual payload
#        clockRate[4] + reserved[4] + payload[52] when init
#        xparam[4] + payload[56] when write
#            xparam: txSz[1]+rxSz[1]+options[1]+slaveAddr[1]
#        payload[60] when read
#

import sys
import usb.core
import usb.util
import binascii

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

# addr : iic slaveaddr
# req : see bridge format
# data: 40 bytes payload
def hid_req(hiddev, endpin, endpout, addr, req, data):
    req = req.rjust(2, '0')

    if req == '01':
        data = data.ljust(120, '0')
        datalen = 12
        txdat = hex(datalen)[2:].rjust(2, '0') + \
                "0000" +    \
                req +   \
                data
    else:
        data = data.ljust(112, '0')
        datalen = 8 + len(data)
        txdat = hex(datalen)[2:].rjust(2, '0') +    \
                "0000" +    \
                req + \
                "280000" +  \
                addr.rjust(2, '0') +    \
                data
        hiddev.write(endpout, txdat.decode("hex"))
        hiddev.read(endpin, 64, 100)

        datalen = 8
        txdat = hex(datalen)[2:].rjust(2, '0') +    \
                "0000" +    \
                req + \
                "002800" +  \
                addr.rjust(2, '0') +    \
                "0".ljust(112, '0')

    hiddev.write(endpout, txdat.decode("hex"))

def hid_read(hiddev, endpin):
    ret = hiddev.read(endpin, 64, 100)
    if ret[0] > 4:
        return ret[4:ret[0]]
    else:
        return None

def hid_xfer(hiddev, endpin, endpout, addr, req, data):
    hid_req(hiddev, endpin, endpout, addr, req, data)
    return hid_read(hiddev, endpin)

def run_loopback():
    hid_vid = 0x1fc9
    hid_pid = 0x0088

    hiddev, endpin, endpout = enum_usbhid(hid_vid, hid_pid)

    ret = hid_xfer(hiddev, endpin, endpout, "00", "01", "40420f00")
    if ret:
        print "Device version: " +  ''.join([chr(x) for x in ret])
    else:
        print "Devcie Ver null"

    # addressing 0x18
    ret = hid_xfer(hiddev, endpin, endpout, "00", "05", "0000000000000018")
    if ret:
        rxdat = binascii.hexlify(ret)
        print "DNA = " + rxdat[:16]
    else:
        print "Read DNA Failed!"

    # loopback on 0x18
    txdat = "000000011234567890123456789012345678901234567890123456789012345678901234567890"
    for i in range(1, 4):
        ret = hid_xfer(hiddev, endpin, endpout, "18", "05", txdat +  str(i).rjust(2,'0'))
        if ret:
            rxdat = binascii.hexlify(ret)
            if rxdat == (txdat +  str(i).rjust(2,'0')):
                print "Loopback success " + str(i)
            else:
                print "txdat = " + txdat
                print "rxdat = " + rxdat
                print "Loopback failed"

        else:
            print "Read None"

if __name__ == '__main__':
    run_loopback()

