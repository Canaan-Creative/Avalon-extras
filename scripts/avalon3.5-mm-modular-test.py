#!/usr/bin/env python2.7

# This simple script was for test A3255 modular. there are 128 cores in one A3255 chip.
# If all cores are working the number should be 0.
# If some of them not working the number is the broken cores count.
# Note: Avalon 3.5 use usb2iic instead of uart, the usb2iic bridge expose hid api to app.
# Depends : PyUSB 1.0 (Under Linux)
# PyUSB 1.0 Installation: https://github.com/walac/pyusb

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

# usb2iic data
# init: 0c00670140420f000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# tx1: Address 0x18 30016705280000000000000000000018000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# tx2: Read DNA 08026705002800000000000000000018000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# tx3: Send [04,26] to 0x18 3003670528000018000000010405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425260000000000000000000000000000000000
# tx4: Read from 0x18 0804670500280018000000010405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425260000000000000000000000000000000000
def run_loopback():
    hid_vid = 0x1fc9
    hid_pid = 0x0088

    hiddev, endpin, endpout = enum_usbhid(hid_vid, hid_pid)
    # init usb2iic bridge
    txdat = "0c00670140420f000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    hiddev.write(endpout, txdat.decode("hex"))
    ret = hiddev.read(endpin, 64, 100)
    version = ret[4:ret[0]]
    print "Device version: " +  ''.join([chr(x) for x in version])

    # tx1 usb2iic addressing test
    txdat = "30016705280000000000000000000018000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    hiddev.write(endpout, txdat.decode("hex"))
    ret = hiddev.read(endpin, 64, 100)
    txdat = "08026705002800000000000000000018000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    hiddev.write(endpout, txdat.decode("hex"))
    ret = hiddev.read(endpin, 64, 100)
    rxdat = binascii.hexlify(ret)
    if ret[0] > 4:
        print "DNA = " + rxdat[8:24]
    else:
        print "Read DNA Failed!"

    # tx2 loopback testing
    txdat_orig = "3003670528000018000000010405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425260000000000000000000000000000000000"
    hiddev.write(endpout, txdat_orig.decode("hex"))
    ret = hiddev.read(endpin, 64, 100)
    txdat = "08046705002800180000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    hiddev.write(endpout, txdat.decode("hex"))
    ret = hiddev.read(endpin, 64, 100)
    rxdat = binascii.hexlify(ret)
    if ret[0] > 4:
        if rxdat[8:ret[0]*2] == txdat_orig[16:96]:
            print "Loopback success"
        else:
            print "txdat = " + txdat_orig[16:96]
            print "rxdat = " + rxdat[8:88]
            print "Loopback failed"
    else:
        print "Read none!"

if __name__ == '__main__':
        run_loopback()

