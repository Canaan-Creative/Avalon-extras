#!/usr/bin/env python2.7

# This simple script was for test A3255 modular. there are 128 cores in one A3255 chip.
# If all cores are working the number should be 0.
# If some of them not working the number is the broken cores count.

from serial import Serial
from optparse import OptionParser
import binascii

parser = OptionParser()
parser.add_option("-s", "--serial", dest="serial_port", default="/dev/ttyUSB0", help="Serial port")
parser.add_option("-c", "--chip_count", dest="chip_count", default="10", help="Chip count")
parser.add_option("-m", "--miner_count", dest="miner_count", default="8", help="Miner count")
(options, args) = parser.parse_args()

cmd="01"
res_rec = []

chip_count = int(options.chip_count)
miner_count = int(options.miner_count)

ser = Serial(options.serial_port, 115200, 8, xonxoff=False, rtscts=0)

while(1):
    print ("[NOTE] Starting ...")
    ser.write(cmd.decode('hex'))
    for i in range(miner_count):
        for j in range(chip_count):
            res_rec.append(0)
    while(1):
        res_s = ser.read(2)
        print("Received: " + binascii.hexlify(res_s))
        res = int(binascii.hexlify(res_s), 16)
        if(res == 0xffff):
            break
        else:
            group = (res >> 12) - 1
            chip = ((res >> 8) & 0xf) - 1
            core = res & 0xff
            res_rec[group * chip_count + chip] += 1
    print("c/m\t0\t1\t2\t3\t4\t5\t6\t7")
    for i in range(chip_count):
        res_str = str(i)
        res_str += ":\t"
        for j in range(miner_count):
            res_rec_int = res_rec[j * chip_count + i]
            res_str += str(res_rec_int)
            if res_rec_int != 0:
            	res_str += "<<<"
	    res_str += "\t"
        print(res_str)
    print ("[NOTE] End")
