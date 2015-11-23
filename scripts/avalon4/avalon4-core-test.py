#!/usr/bin/env python2.7

# This simple script was for test A3255 modular.
# there are 128 cores in one A3255 chip.
# If all cores are working the number should be 0.
# If some of them not working the number is the broken cores count.
# Note: Avalon 3.5 use usb2iic instead of uart,
# the usb2iic bridge expose cdc api to app.
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
#        a6:XFER
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
import struct

parser = OptionParser(version="%prog ver:20151123_1109")
# TODO: Module id assignment
parser.add_option("-m", "--module", dest="module_id", default="0", help="Module ID: 0 - 127, default:0")
parser.add_option("-c", "--count", dest="test_count", default="1", help="Test count: 1,2,3... ")
parser.add_option("-f", "--fastxfer", dest="fast_xfer", default="0", help="Fast Xfer switch 0-OFF/1-ON, default:0")
# For fast core testing, 16 is the maximum for Avalon4 mini
parser.add_option("-C", "--core", dest="test_cores", default="64", help="Test cores: 1-3968")
parser.add_option("-V", "--voltage", dest="voltage", default="7875", help="Asic voltage, default:7875")
parser.add_option("-F", "--freq", dest="freq", default="200,200,200", help="Asic freq, default:200,200,200")
parser.add_option("-s", "--statics", dest="statics", default="0", help="Statics flag, default:0")
parser.add_option("-S", "--status", dest="status", default="0", help="Only read status back, default:0")
(options, args) = parser.parse_args()
parser.print_version()

asic_cnt = 4
miner_cnt = 10
auc_vid = 0x29f1
auc_pid = 0x33f2

g_freq_table = {
         '100': '1e678447',
         '113': '22688447',
         '125': '1c470447',
         '138': '2a6a8447',
         '150': '22488447',
         '163': '326c8447',
         '175': '1a268447',
         '188': '1c270447',
         '200': '1e278447',
         '213': '20280447',
         '225': '22288447',
         '238': '24290447',
         '250': '26298447',
         '263': '282a0447',
         '275': '2a2a8447',
         '288': '2c2b0447',
         '300': '2e2b8447',
         '313': '302c0447',
         '325': '322c8447',
         '338': '342d0447',
         '350': '1a068447',
         '363': '382e0447',
         '375': '1c070447',
         '388': '3c2f0447',
         '400': '1e078447',
         '413': '40300447',
         '425': '20080447',
         '438': '44310447',
         '450': '22088447',
         '463': '48320447',
         '475': '24090447',
         '488': '4c330447',
         '500': '26098447',
         '513': '50340447',
         '525': '280a0447',
         '538': '54350447',
         '550': '2a0a8447',
         '563': '58360447',
         '575': '2c0b0447',
         '588': '5c370447',
         '600': '2e0b8447',
         '613': '60380447',
         '625': '300c0447',
         '638': '64390447',
         '650': '320c8447',
         '663': '683a0447',
         '675': '340d0447',
         '688': '6c3b0447',
         '700': '360d8447',
         '713': '703c0447',
         '725': '380e0447',
         '738': '743d0447',
         '750': '3a0e8447',
         '763': '783e0447',
         '775': '3c0f0447',
         '788': '7c3f0447',
         '800': '3e0f8447',
         '813': '3e0f8447',
         '825': '40100447',
         '838': '40100447',
         '850': '42108447',
         '863': '42108447',
         '875': '44110447',
         '888': '44110447',
         '900': '46118447',
         '913': '46118447',
         '925': '48120447',
         '938': '48120447',
         '950': '4a128447',
         '963': '4a128447',
         '975': '4c130447',
         '988': '4c130447',
         '1000': '4e138447'
}


def statics(usbdev, endpin, endpout):
    start = time.time()
    for i in range(0, int(options.test_count)):
        run_detect(usbdev, endpin, endpout, mm_package(TYPE_DETECT, module_id=options.module_id))
    print "time elapsed: %s" % (time.time() - start)


def enum_usbdev(vendor_id, product_id):
    # Find device
    usbdev = usb.core.find(idVendor=vendor_id, idProduct=product_id)

    if not usbdev:
        return None, None, None

    if (product_id == 0x40f1):
        if usbdev.is_kernel_driver_active(1) is True:
            usbdev.detach_kernel_driver(1)

    try:
        # usbdev[iConfiguration][(bInterfaceNumber,bAlternateSetting)]
        for endp in usbdev[0][(1, 0)]:
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
        txdat = hex(datalen)[2:].rjust(2, '0') + "0000" + req + data
        usbdev.write(endpout, txdat.decode("hex"))

    # FIXME: a3 not work
    if req == 'a3':
        datalen = 8 + (len(data) / 2)
        data = data.ljust(112, '0')
        txdat = hex(datalen)[2:].rjust(2, '0') + "0000" + "a5" + "280000" + addr.rjust(2, '0') + data
        usbdev.write(endpout, txdat.decode("hex"))
        usbdev.read(endpin, 64)

    # FIXME: a4 not work
    if req == 'a4':
        datalen = 8
        txdat = hex(datalen)[2:].rjust(2, '0') + "0000" + "a5" + "002800" + addr.rjust(2, '0') + "0".ljust(112, '0')
        usbdev.write(endpout, txdat.decode("hex"))

    if req == 'a5':
        if options.fast_xfer == '1':
            datalen = 8 + (len(data) / 2)
            data = data.ljust(112, '0')
            txdat = hex(datalen)[2:].rjust(2, '0') + "0000" + "a5" + "282800" + addr.rjust(2, '0') + data
            usbdev.write(endpout, txdat.decode("hex"))
        else:
            datalen = 8 + (len(data) / 2)
            data = data.ljust(112, '0')
            txdat = hex(datalen)[2:].rjust(2, '0') + "0000" + "a5" + "280000" + addr.rjust(2, '0') + data
            usbdev.write(endpout, txdat.decode("hex"))
            usbdev.read(endpin, 64)

            datalen = 8
            txdat = hex(datalen)[2:].rjust(2, '0') + "0000" + "a5" + "002800" + addr.rjust(2, '0') + "0".ljust(112, '0')
            usbdev.write(endpout, txdat.decode("hex"))

    if req == 'a6':
        datalen = 4
        txdat = hex(datalen)[2:].rjust(2, '0') + "0000" + req
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


TYPE_TEST = "32"
TYPE_DETECT = "10"
TYPE_REQUIRE = "31"
DATA_OFFSET = 6

def CRC16(message):
    # CRC-16-CITT poly, the CRC sheme used by ymodem protocol
    poly = 0x1021
    # 16bit operation register, initialized to zeros
    reg = 0x0000
    # pad the end of the message with the size of the poly
    message += '\x00\x00'
    # for each bit in the message
    for byte in message:
        mask = 0x80
        while(mask > 0):
            # left shift by one
            reg <<= 1
            # input the next bit from the message into the right hand side
            # of the op reg
            if ord(byte) & mask:
                reg += 1
            mask >>= 1
            # if a one popped out the left of the reg, xor reg w/poly
            if reg > 0xffff:
                # eliminate any one that popped out the left
                reg &= 0xffff
                # xor with the poly, this is the remainder
                reg ^= poly
    return reg


def mm_package(cmd_type, idx="01", cnt="01", module_id=None, pdata='0'):
    if module_id is None:
        data = pdata.ljust(64, '0')
    else:
        data = pdata.ljust(60, '0') + module_id.rjust(4, '0')
        crc = CRC16(data.decode("hex"))
        return "434e" + cmd_type + "00" + idx + cnt + data + hex(crc)[2:].rjust(4, '0')


def run_test(usbdev, endpin, endpout, cmd):
        global asic_cnt, miner_cnt
        global auc_pid

        if auc_pid == 0x40f1:
            usbdev.write(endpout, cmd.decode("hex"))
        else:
            auc_req(usbdev, endpin, endpout, "00", "a3", cmd)

        for count in range(0, miner_cnt + 1):
                asics = asic_cnt
                if ((count == 0) and (count != miner_cnt + 1)):
                        print "= PG", count + 1, "="

                if count != (miner_cnt):
                        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                        while asics:
                                while True:
                                        if auc_pid == 0x40f1:
                                            res_s = usbdev.read(endpin, 40)
                                        else:
                                            auc_req(usbdev, endpin, endpout,
                                                    "00",
                                                    "a4",
                                                    cmd)
                                            res_s = auc_read(usbdev, endpin)
                                        if res_s is not None:
                                                break

                                if not res_s:
                                        print(str(count) + ": Something is wrong or modular id not correct")
                                else:
                                        result = binascii.hexlify(res_s)
                                        if (asics < 4):
                                                column = asics
                                        else:
                                                column = 4

                                        for i in range(0, column + 1):
                                                if (i == 0):
                                                        number = '{:03}'.format(int(result[DATA_OFFSET*2:(DATA_OFFSET+1)*2], 16) % 5 + 1)
                                                        sys.stdout.write(number + ":\t")
                                                else:
                                                        number = '{:04}'.format(int(result[(DATA_OFFSET+1+(i-1)*4)*2:(DATA_OFFSET+5+(i-1)*4)*2], 16))
                                                        if (number != "0000"):
                                                                core = int(number, 10)
                                                                if (core <= 5):
                                                                    sys.stdout.write("\x1b[1;33m" + number + "\x1b[0m" + "\t")
                                                                else:
                                                                    sys.stdout.write("\x1b[1;31m" + number + "\x1b[0m" + "\t")
                                                        else:
                                                                sys.stdout.write(number + "\t")
                                                sys.stdout.flush()
                                        print("")
                                if (asics >= 4):
                                        asics -= 4
                                else:
                                        asics = 0
                else:
                        while True:
                                if auc_pid == 0x40f1:
                                    res_s = usbdev.read(endpin, 40)
                                else:
                                    auc_req(usbdev, endpin, endpout, "00", "a4", cmd)
                                    res_s = auc_read(usbdev, endpin)
                                if res_s is not None:
                                        break

                        # format: pass(20), all(40), percent(50%)
                        avalon_test = binascii.hexlify(res_s)
                        passcore = int(avalon_test[DATA_OFFSET*2:(DATA_OFFSET+4)*2], 16)
                        allcore = int(avalon_test[(DATA_OFFSET+4)*2:(DATA_OFFSET+8)*2], 16)
                        result = "bad(" + str(allcore - passcore) + "), "
                        result = result + "all(" + str(allcore) + "), "
                        result = result + "bad percent(" + str(round((allcore - passcore) * 100.0/allcore, 2)) + "%)"
                        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                        print("Result:" + result)

errcode = [
        'IDLE',
        '\x1b[1;31mTOOHOT\x1b[0m',
        '\x1b[1;31mLOOP0FAILED\x1b[0m',
        '\x1b[1;31mLOOP1FAILED\x1b[0m',
        '\x1b[1;31mINVALIDMCU\x1b[0m',
        'NOSTRATUM',
        'RBOVERFLOW',
        'MMCRCFAILED',
        'MCUCRCFAILED',
        '\x1b[1;31mNOFAN\x1b[0m',
        '\x1b[1;31mPG0FAILED\x1b[0m',
        '\x1b[1;31mPG1FAILED\x1b[0m',
        '\x1b[1;31mCORETESTFAILED\x1b[0m',
        '\x1b[1;31mADC0ERR\x1b[0m',
        '\x1b[1;31mADC1ERR\x1b[0m',
        '\x1b[1;31mVOLTERR\x1b[0m'
        ]

def run_testa6(usbdev, endpin, endpout, cmd):
        auc_req(usbdev, endpin, endpout, "00", "a3", cmd)
        while True:
                auc_req(usbdev, endpin, endpout,
                        "00",
                        "a4",
                        cmd)
                res_s = auc_read(usbdev, endpin)
                if res_s is not None:
                        break

        if not res_s:
                print(str(count) + ": Something is wrong or modular id not correct")
        else:
                result = binascii.hexlify(res_s)
                for i in range(0, 2):
                    sys.stdout.write("M-" + str(i) + ': ')
                    c = result[(12 + i * 10) : (12 + i * 10) + 10]
                    n = int(c, 16)
                    r = ''
                    cnt = 0;
                    for j in range(40, 0, -8):
                        for cnt in range(7, -1, -1):
                            if ((n >> cnt) & 1) == 0:
                                r = '\x1b[1;31mxx\x1b[0m {}'.format(r)
                            else:
                                r = '\x1b[1;32m{:02d}\x1b[0m {}'.format(j + cnt - 7 , r)
                        n >>= 8
                    print(r)

                passcore = int(result[32: 36], 16)
                allcore = int(result[36: 40], 16)
                ec = int(result[40:48], 16)

                display = 'bad(' + str(allcore - passcore) + '), '
                display = display + 'all(' + str(allcore) + '), '
                errstr = ''
                for i in range(0, len(errcode)):
                    if ((ec >> i) & 1):
                        errstr += errcode[i] + ' '

                display = display + 'Status ( ' + errstr + ')'
                print('Result:' + display)

def run_detect(usbdev, endpin, endpout, cmd):
    # version
    global auc_pid
    if auc_pid == 0x40f1:
        usbdev.write(endpout, cmd.decode("hex"))
        res_s = usbdev.read(endpin, 40)
    else:
        res_s = auc_xfer(usbdev, endpin, endpout, "00", "a5", cmd)
    if not res_s:
        print("ver:Something is wrong or modular id not correct")
        return None
    else:
        hw = ''.join([chr(x) for x in res_s])[DATA_OFFSET+8:DATA_OFFSET+23]
        print("ver:" + hw)
        return hw[0:2]


def run_require(usbdev, endpin, endpout, cmd):
    res_s = auc_xfer(usbdev, endpin, endpout, "00", "a5", cmd)
    if not res_s:
        print("status:Something is wrong or modular id not correct")
    else:
        # format: temp(40), fan(20), freq(300), vol(400), localwork(1),
        # g_hw_work(300), pg(0)
        avalon_require = binascii.hexlify(res_s)

        temp = struct.unpack_from(">h", res_s, DATA_OFFSET+2)[0]
        fan = int(avalon_require[(DATA_OFFSET+6)*2:(DATA_OFFSET+8)*2], 16)
        freq = int(avalon_require[(DATA_OFFSET+8)*2:(DATA_OFFSET+12)*2], 16)
        vol = avalon_require[(DATA_OFFSET+12)*2:(DATA_OFFSET+16)*2]
        localwork = int(avalon_require[(DATA_OFFSET+16)*2:(DATA_OFFSET+20)*2], 16)
        g_hw_work = int(avalon_require[(DATA_OFFSET+20)*2:(DATA_OFFSET+24)*2], 16)
        pg = avalon_require[(DATA_OFFSET+24)*2:(DATA_OFFSET+28)*2]
        result = "status:temp(" + str(temp) + "), "
        result = result + "fan(" + str(fan) + "), "
        result = result + "freq(" + str(freq) + "), "
        result = result + "vol(" + vol + "), "
        result = result + "localwork(" + str(localwork) + "), "
        result = result + "g_hw_work(" + str(g_hw_work) + "), "
        result = result + "pg(" + pg + ")"
        print(result)


def run_getinfo(usbdev, endpin, endpout):
    res_s = auc_xfer(usbdev, endpin, endpout, "00", "a6", "")
    if not res_s:
        print("getinfo:Something is wrong or modular id not correct")
    else:
        print("getinfo:" + binascii.hexlify(res_s))


def rev8(x):
    result = 0
    for i in xrange(8):
        if (x >> i) & 1:
            result |= 1 << (7 - i)
    return result

def encode_voltage_adp3208d(v):
    return rev8((0x78 - v / 125) << 1 | 1) << 8

def encode_voltage_ncp5392p(v):
    if (v == 0):
        return 0xff00

    return rev8(((0x59 - (v - 5000) / 125) & 0xff) << 1 | 1) << 8

def encode_voltage_ncp5392p_mini(v):
    if (v == 0):
        return 0xff

    return (((0x59 - (v - 5000) / 125) & 0xff) << 1 | 1)

def run_modular_test(usbdev, endpin, endpout):
    global asic_cnt, miner_cnt
    while True:
        print("Reading result ...")
        hw = run_detect(usbdev, endpin, endpout, mm_package(TYPE_DETECT, module_id=options.module_id))
        if hw == None:
            sys.exit("Could not detect mm")

        if hw == '50':
            asic_cnt = 16
            miner_cnt = 2

        if hw == '4M':
            asic_cnt = 5
            miner_cnt = 1

        tmp = hex(int(options.test_cores, 10))[2:]
        txdata = tmp.rjust(8, '0')

        if (hw == '4M'):
            tmp = hex(encode_voltage_ncp5392p_mini(int(options.voltage, 10)))[2:]
        if (hw == '41'):
            tmp = hex(encode_voltage_ncp5392p(int(options.voltage, 10)))[2:]
        if (hw == '40'):
            tmp = hex(encode_voltage_adp3208d(int(options.voltage, 10)))[2:]

        tmp = tmp.rjust(8, '0')
        txdata += tmp

        freqdata = {}
        tmp = options.freq.split(",")
        if len(tmp) == 0:
            freqdata[0] = 200
            freqdata[1] = freqdata[2] = 200

        if len(tmp) == 1:
            freqdata[2] = freqdata[1] = freqdata[0] = tmp[0]

        if len(tmp) == 2:
            freqdata[0] = tmp[0]
            freqdata[2] = freqdata[1] = tmp[1]

        if len(tmp) == 3:
            freqdata[0] = tmp[0]
            freqdata[1] = tmp[1]
            freqdata[2] = tmp[2]

        tmp = hex(int(freqdata[0], 10) | (int(freqdata[1], 10) << 10) | (int(freqdata[2], 10) << 20))[2:]
        tmp = tmp.rjust(8, '0')
        txdata += tmp
        if (hw == '41') or (hw == '4M'):
            txdata += g_freq_table[freqdata[0]]
            txdata += g_freq_table[freqdata[1]]
            txdata += g_freq_table[freqdata[2]]

        if (hw == '60'):
            run_testa6(usbdev, endpin, endpout, mm_package(TYPE_TEST, module_id=options.module_id, pdata=txdata))
        else:
            run_test(usbdev, endpin, endpout, mm_package(TYPE_TEST, module_id=options.module_id, pdata=txdata))
        if (hw == '40') or (hw == '41') or (hw == '50'):
            run_require(usbdev, endpin, endpout, mm_package(TYPE_REQUIRE, module_id=options.module_id))
        raw_input('Press enter to continue:')


if __name__ == '__main__':
    # Detect AUC
    usbdev, endpin, endpout = enum_usbdev(auc_vid, auc_pid)
    if usbdev:
        ret = auc_xfer(usbdev, endpin, endpout, "00", "a1", "801A0600")
        if ret:
            print "AUC ver: " + ''.join([chr(x) for x in ret])
        else:
            print "AUC ver null"

    if usbdev is None:
        # Try Avalon4 mini
        auc_vid = 0x29f1
        auc_pid = 0x40f1
        usbdev, endpin, endpout = enum_usbdev(auc_vid, auc_pid)

    if usbdev is None:
        print "No Avalon USB Converter or compatible device can be found!"
        sys.exit("Enum failed!")
    else:
        print "Find an Avalon USB Converter or comatible device"

    if (options.status == '1'):
        while(1):
            run_require(usbdev, endpin, endpout, mm_package(TYPE_REQUIRE, module_id=options.module_id))
        sys.exit()

    if (options.statics == '1'):
        statics(usbdev, endpin, endpout)
    else:
        run_modular_test(usbdev, endpin, endpout)
