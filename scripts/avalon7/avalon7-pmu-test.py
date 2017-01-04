#!/usr/bin/env python2.7

from __future__ import division
from serial import Serial
from optparse import OptionParser
import binascii
import sys
import time

parser = OptionParser()
parser.add_option("-s", "--serial", dest="serial_port", default="/dev/ttyUSB0", help="Serial port")
parser.add_option("-c", "--choose", dest="is_rig", default="0", help="0 Is For Rig Testing")
(options, args) = parser.parse_args()

ser = Serial(options.serial_port, 115200, 8, timeout=0.2) # 1 second

PMU721_TYPE = ( 'PMU721' )
PMU741_TYPE = ( 'PMU741' )

PMU721_VER = ( '75d0' )
PMU741_VER = ( '12c0' )

PMU721_PG  = { 'pg_good': '0001', 'pg_bad': '0002' }
PMU741_PG  = { 'pg_good': '0001', 'pg_bad': '0002' }

PMU721_LED = { 'led_close': '0000', 'led_green': '0001', 'led_red': '0002' }
PMU741_LED = { 'led_close': '0000', 'led_green': '0001', 'led_red': '0002' }

PMU721_ADC = { 'ntc_l': 800, 'ntc_h': 1000, 'v12_l':931, 'v12_h': 1024, 'vcore_l': 804, 'vcore_h': 889,  'vbase_l': 735, 'vbase_h': 813 }
PMU741_ADC = { 'ntc_l': 800, 'ntc_h': 1000, 'v12_l':931, 'v12_h': 1024, 'vcore_l': 927, 'vcore_h': 1024, 'vbase_l': 735, 'vbase_h': 813 }

error_message = {
    'serial_port': 'Connection failed.',
    'ntc_1': 'NTC_1 value error.',
    'ntc_2': 'NTC_2 value error.',
    'v12_1': 'V12_1 value error.',
    'v12_2': 'V12_2 value error.',
    'vcore_1': 'VCORE1 value error.',
    'vcore_2': 'VCORE2 value error.',
    'vbase': 'VBASE value error.',
    'pg_1' : 'PG1 value error.',
    'pg_2' : 'PG2 value error.' ,
    'led_1': 'LED1 status error.',
    'led_2': 'LED2 status error.'
}

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
    return "434E" + cmd_type + "00" + idx + cnt + data + hex(crc)[2:].rjust(4, '0')

def show_help():
    print("\
h: Help\n\
1: Detect The PMU Version\n\
2: Set	  The PMU Output Voltage\n\
          |-------------------------------|\n\
          |         |    Voltage Value    |\n\
          | Setting |---------------------|\n\
          |         |  PMU721  |  PMU741  |\n\
          |---------|----------|----------|\n\
          |   0000  |  0.00V   |  0.00V   |\n\
          |---------|----------|----------|\n\
          |   8800  |  6.30V   |  7.84V   |\n\
          |---------|----------|----------|\n\
          |   8811  |  6.42V   |  8.00V   |\n\
          |---------|----------|----------|\n\
          |   8822  |  6.55V   |  8.16V   |\n\
          |---------|----------|----------|\n\
          |   8833  |  6.67V   |  8.32V   |\n\
          |---------|----------|----------|\n\
          |   8844  |  6.80V   |  8.48V   |\n\
          |---------|----------|----------|\n\
          |   8855  |  6.93V   |  8.63V   |\n\
          |---------|----------|----------|\n\
          |   8866  |  7.05V   |  8.79V   |\n\
          |---------|----------|----------|\n\
          |   8877  |  7.18V   |  8.95V   |\n\
          |---------|----------|----------|\n\
          |   8888  |  7.30V   |  9.12V   |\n\
          |---------|----------|----------|\n\
          |   8899  |  7.43V   |  9.27V   |\n\
          |---------|----------|----------|\n\
          |   88aa  |  7.56V   |  9.43V   |\n\
          |---------|----------|----------|\n\
          |   88bb  |  7.68V   |  9.59V   |\n\
          |---------|----------|----------|\n\
          |   88cc  |  7.81V   |  9.75V   |\n\
          |---------|----------|----------|\n\
          |   88dd  |  7.93V   |  9.91V   |\n\
          |---------|----------|----------|\n\
          |   88ee  |  8.06V   |  10.0V   |\n\
          |---------|----------|----------|\n\
          |   88ff  |  8.19V   |  10.2V   |\n\
          |-------------------------------|\n\
3: Set    The PMU Led State\n\
          |-------------------------------|\n\
          | Setting |      Led state      |\n\
          |---------|---------------------|\n\
          |   0000  |   All   Led Off     |\n\
          |---------|---------------------|\n\
          |   0101  |   Green Led On      |\n\
          |---------|---------------------|\n\
          |   0202  |   Red   Led On      |\n\
          |---------|---------------------|\n\
          |   0404  |   Green Led Blink   |\n\
          |---------|---------------------|\n\
          |   0808  |   Red   Led Blink   |\n\
          |---------|---------------------|\n\
4: Get    The PMU State\n\
q: Quit\n")

def detect_version():
    global PMU_TYPE
    global PMU_ADC
    global PMU_LED
    global PMU_PG

    input_str = mm_package("10", module_id = None)
    ser.flushInput()
    ser.write(input_str.decode('hex'))
    res = ser.readall()
    if res == "":
        print error_message['serial_port']
        return False
    PMU_DNA = binascii.hexlify(res[6:14])
    if res[25:29] == PMU721_VER:
        PMU_TYPE = PMU721_TYPE
        PMU_VER = PMU721_VER
        PMU_ADC = PMU721_ADC
        PMU_LED = PMU721_LED
        PMU_PG  = PMU721_PG
    elif res[25:29] == PMU741_VER:
        PMU_TYPE = PMU741_TYPE
        PMU_VER = PMU741_VER
        PMU_ADC = PMU741_ADC
        PMU_LED = PMU741_LED
        PMU_PG  = PMU741_PG
    print(PMU_TYPE + " VER:" + PMU_VER)
    print(PMU_TYPE + " DNA:" + PMU_DNA)
    return True

def judge_vol_range(vol):
    if len(vol) != 4:
        return False
    if (vol[0:2] != "00") and (vol[0:2] != "88") and (vol[0:2] != "80") and (vol[0:2] != "08"):
        return False
    try:
        binascii.a2b_hex(vol[2:4])
    except:
        return False

    return True

def judge_led_range(led):
    if len(led) != 4:
        return False
    if (led[0:1] != "0") and (led[2:3] != "0"):
        return False

    return True

def set_vol_value(vol_value):
    if judge_vol_range(vol_value) == True:
        input_str = mm_package("22", module_id = None, pdata = vol_value);
        ser.flushInput()
        ser.write(input_str.decode('hex'))
    else:
        print("Bad voltage vaule!")

def set_led_state(led):
    if judge_led_range(led) == True:
        input_str = mm_package("24", module_id = None, pdata = led);
        ser.flushInput()
        ser.write(input_str.decode('hex'))
    else:
        print("Bad led's state vaule!")

def get_result():
    input_str = mm_package("30", module_id = None);
    ser.flushInput()
    ser.write(input_str.decode('hex'))
    res = ser.readall()
    if res == "":
        print error_message['serial_port']
        return False
    a = int(binascii.hexlify(res[6:8]), 16)
    if (a < PMU_ADC['ntc_l']) or (a > PMU_ADC['ntc_h']):
        print error_message['ntc_1']
        return False
    a = int(binascii.hexlify(res[8:10]), 16)
    if (a < PMU_ADC['ntc_l']) or (a > PMU_ADC['ntc_h']):
        print error_message['ntc_2']
        return False
    a = int(binascii.hexlify(res[10:12]), 16)
    if (a < PMU_ADC['v12_l']) or (a > PMU_ADC['v12_h']):
        print error_message['v12_1']
        return False
    a = int(binascii.hexlify(res[12:14]), 16)
    if (a < PMU_ADC['v12_l']) or (a > PMU_ADC['v12_h']):
        print error_message['v12_2']
        return False
    a = int(binascii.hexlify(res[14:16]), 16)
    if (a < PMU_ADC['vcore_l']) or (a > PMU_ADC['vcore_h']):
        print error_message['vcore_1']
        return False
    a = int(binascii.hexlify(res[16:18]), 16)
    if (a < PMU_ADC['vcore_l']) or (a > PMU_ADC['vcore_h']):
        print error_message['vcore_2']
        return False
    a = int(binascii.hexlify(res[18:20]), 16)
    if (a < PMU_ADC['vbase_l']) or (a > PMU_ADC['vbase_h']):
        print error_message['vbase']
        return False
    a = binascii.hexlify(res[20:22])
    if (a != PMU_PG['pg_good']):
        print error_message['pg_1']
        return False
    a = binascii.hexlify(res[22:24])
    if (a != PMU_PG['pg_good']):
        print error_message['pg_2']
        return False
    a = binascii.hexlify(res[24:26])
    if (a != PMU_LED['led_close']):
        print error_message['led_1']
        return False
    a = binascii.hexlify(res[26:28])
    if (a != PMU_LED['led_close']):
        print error_message['led_2']
        return False
    return True

pmu_state_name = (
    'NTC1:   ',
    'NTC2:   ',
    'V12-1:  ',
    'V12-2:  ',
    'VCORE1: ',
    'VCORE2: ',
    'VBASE:  '
)

pmu_pg_state  = {
    '0001': 'Good',
    '0002': 'Bad'
}

pmu_led_state = {
    '0000': 'All Led Off',
    '0001': 'Green Led On',
    '0002': 'Red Led On',
    '0004': 'Green Led Blink',
    '0008': 'Red Led Blink'
}

def get_state():
    input_str = mm_package("30", module_id = None);
    ser.flushInput()
    ser.write(input_str.decode('hex'))
    res = ser.readall()
    if res == "":
        print error_message['serial_port']
        return False
    for index in range(len(pmu_state_name)):
        a = int(binascii.hexlify(res[(index * 2 + 6):(index * 2 + 8)]), 16)
        print(pmu_state_name[index] + '%d' %a)
    a = binascii.hexlify(res[20:22])
    pmu_pg_state_key = pmu_pg_state.keys()
    for index in range(len(pmu_pg_state_key)):
        if a == pmu_pg_state_key[index]:
            print("PG1:    " + pmu_pg_state.get(pmu_pg_state_key[index]))
    a = binascii.hexlify(res[22:24])
    pmu_pg_state_key = pmu_pg_state.keys()
    for index in range(len(pmu_pg_state_key)):
        if a == pmu_pg_state_key[index]:
            print("PG2:    " + pmu_pg_state.get(pmu_pg_state_key[index]))
    a = binascii.hexlify(res[24:26])
    pmu_led_state_key = pmu_led_state.keys()
    for index in range(len(pmu_led_state_key)):
        if a == pmu_led_state_key[index]:
            print("LED1:   " + pmu_led_state.get(pmu_led_state_key[index]))
    a = binascii.hexlify(res[26:28])
    pmu_led_state_key = pmu_led_state.keys()
    for index in range(len(pmu_led_state_key)):
        if a == pmu_led_state_key[index]:
            print("LED2:   " + pmu_led_state.get(pmu_led_state_key[index]))
    return True

def test_polling():
    while (True):
        h = raw_input("Please input(1-4), h for help:")
        if (h == 'h') or (h == 'H'):
            show_help()
        elif (h == 'q') or (h == 'Q'):
            sys.exit(0)
        elif h == '1':
            detect_version()
        elif h == '2':
            vol = raw_input("Please input the voltage:")
            set_vol_value(vol)
        elif h == '3':
            led = raw_input("Please input the led state:")
            set_led_state(led)
        elif h == '4':
            if (get_state() == False):
                sys.exit(0)
        else:
            show_help()

if __name__ == '__main__':
    while (True):
        if options.is_rig == '0':
            set_led_state("0000")
            set_vol_value("88dd")
            if detect_version() == False:
                sys.exit(0)
            time.sleep(3)
            if get_result() == False:
                set_led_state("0202")
                print(PMU_TYPE + " test fail")
            else:
                set_led_state("0101")
                print(PMU_TYPE + " test pass")
            set_vol_value("0000")
            raw_input("Please enter to continue:")
        elif options.is_rig == '1':
            test_polling()
        else:
            print("Input option wrong, please try again")
            sys.exit(0)
