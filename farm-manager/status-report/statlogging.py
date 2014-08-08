#!/usr/bin/env python
from __future__ import print_function
import xml.dom.minidom
import datetime
import sys


def writelog(data,cfg,filename):
    # write XML log file
    logdir = cfg['General']['log_dir']

    print('Logging into ' + logdir + filename + ' ... ', end="")
    sys.stdout.flush()
    log = '<?xml version="1.0"?>\n'
    time = filename.strip("log-").strip(".xml")

    log += "<data>\n\t<time>" + time + "</time>\n"

    for mminer in data:
        log += "\t<miner>\n"
        log += "\t\t<IP>" + mminer[0] + "</IP>\n"
        for miner in mminer[1:]:
            log += "\t\t<subminer>\n"
            log += "\t\t\t<Port>" + miner[0] + "</Port>\n"
            log += "\t\t\t<Status>" + miner[1] + "</Status>\n"
            log += "\t\t\t<Elapsed>" + miner[2] + "</Elapsed>\n"
            log += "\t\t\t<TotalMH>" + miner[3] + "</TotalMH>\n"
            for dev_stat in miner[4]:
                log += "\t\t\t<dev>\n"
                log += "\t\t\t\t<DeviceElapsed>" + (
                    dev_stat[0] + "</DeviceElapsed>\n")
                log += "\t\t\t\t<TotalMH>" + dev_stat[1] + "</TotalMH>\n"
                log += "\t\t\t\t<MaxTemperature>" + (
                    dev_stat[2] + "</MaxTemperature>\n")
                log += "\t\t\t\t<ModuleNumber>" + (
                    str(dev_stat[3]) + "</ModuleNumber>\n")
                for temp in dev_stat[4]:
                    log += "\t\t\t\t<Temperature>" + temp + "</Temperature>\n"
                for fan in dev_stat[5]:
                    log += "\t\t\t\t<FanSpeed>" + fan + "</FanSpeed>\n"
                for localWork in dev_stat[6]:
                    log += "\t\t\t\t<LocalWork>" + localWork + "</LocalWork>\n"
                for dhError in dev_stat[7]:
                    log += "\t\t\t\t<DeviceHardwareError>" + (
                        dhError + "</DeviceHardwareError>\n")
                for voltage in dev_stat[8]:
                    log += "\t\t\t\t<Voltage>" + voltage + "</Voltage>\n"
                for frequency in dev_stat[9]:
                    log += "\t\t\t\t<Frequency>" + frequency + "</Frequency>\n"
                log += "\t\t\t</dev>\n"
            for pool_stat in miner[5]:
                log += "\t\t\t<pool>\n"
                log += "\t\t\t\t<URL>" + pool_stat[0] + "</URL>\n"
                log += "\t\t\t\t<Status>" + pool_stat[1] + "</Status>\n"
                log += "\t\t\t</pool>\n"
            log += "\t\t\t<MHS15min>" + miner[6] + "</MHS15min>\n"
            log += "\t\t</subminer>\n"
        log += "\t</miner>\n"
    log += "</data>"

    logfile = open(logdir + filename, 'w')
    logfile.write(log)
    logfile.close()
    print('Done.')


def readlog(logdir,filename):

    # read XML log file
    data = []
    DOMTree = xml.dom.minidom.parse(logdir + filename)
    log = DOMTree.documentElement
    time = datetime.datetime.strptime(
        log.getElementsByTagName("time")[0].childNodes[0].data,
        "%Y_%m_%d_%H_%M")

    for mminerXML in log.getElementsByTagName("miner"):
        mminer = []
        mminer.append(mminerXML.getElementsByTagName
                      ("IP")[0].childNodes[0].data)
        for minerXML in mminerXML.getElementsByTagName("subminer"):
            dev = []
            pool = []
            miner = []
            miner.append(minerXML.getElementsByTagName
                         ("Port")[0].childNodes[0].data)
            miner.append(minerXML.getElementsByTagName
                         ("Status")[0].childNodes[0].data)
            miner.append(minerXML.getElementsByTagName
                         ("Elapsed")[0].childNodes[0].data)
            miner.append(minerXML.getElementsByTagName
                         ("TotalMH")[0].childNodes[0].data)
            for dev_statXML in minerXML.getElementsByTagName("dev"):
                dev_stat = []
                dev_stat.append(dev_statXML.getElementsByTagName
                                ("DeviceElapsed")[0].childNodes[0].data)
                dev_stat.append(dev_statXML.getElementsByTagName
                                ("TotalMH")[0].childNodes[0].data)
                dev_stat.append(dev_statXML.getElementsByTagName
                                ("MaxTemperature")[0].childNodes[0].data)
                dev_stat.append(dev_statXML.getElementsByTagName
                                ("ModuleNumber")[0].childNodes[0].data)
                temp = []
                for tempXML in dev_statXML.getElementsByTagName("Temperature"):
                    temp.append(tempXML.childNodes[0].data)
                dev_stat.append(temp)
                fan = []
                for fanXML in dev_statXML.getElementsByTagName("FanSpeed"):
                    fan.append(fanXML.childNodes[0].data)
                dev_stat.append(fan)
                localWork = []
                for lwXML in dev_statXML.getElementsByTagName("LocalWork"):
                    localWork.append(lwXML.childNodes[0].data)
                dev_stat.append(localWork)
                dhError = []
                for dhXML in dev_statXML.getElementsByTagName(
                        "DeviceHardwareError"):
                    dhError.append(dhXML.childNodes[0].data)
                dev_stat.append(dhError)
                voltage = []
                for voltageXML in dev_statXML.getElementsByTagName("Voltage"):
                    fan.append(voltageXML.childNodes[0].data)
                dev_stat.append(voltage)
                freq = []
                for freqXML in dev_statXML.getElementsByTagName("Frequency"):
                    freq.append(freqXML.childNodes[0].data)
                dev_stat.append(freq)
                dev.append(dev_stat)
            for pool_statXML in minerXML.getElementsByTagName("pool"):
                pool_stat = []
                pool_stat.append(pool_statXML.getElementsByTagName
                                 ("Status")[0].childNodes[0].data)
                pool_stat.append(pool_statXML.getElementsByTagName
                                 ("URL")[0].childNodes[0].data)
                pool.append(pool_stat)
            miner.append(dev)
            miner.append(pool)
            try:
                miner.append(minerXML.getElementsByTagName
                             ("MHS15min")[0].childNodes[0].data)
            except:
                miner.append('0')
            mminer.append(miner)
        data.append(mminer)

    return (data, time)

if __name__ == '__main__':
    logdir = './log/'
    logname = 'log-example.xml'
    (data, time) = readlog(logdir, logname)

    for miner in data:
        print(miner[0] + ': ' + miner[1] + ' ' + miner[2] + ' ' + miner[3])
        i = 1
        for dev_stat in miner[4]:
            print('\tModule #' + str(i) + ':')
            print('\t\tDevice Elapsed: ' + dev_stat[0])
            print('\t\tTotal MH: ' + dev_stat[1])
            print('\t\tTemperature: ' + dev_stat[2])
            print('\t\tModules Number: ' + str(dev_stat[3]))
            print('\t\tTemperature List: ' + ','.join(dev_stat[4]))
            print('\t\tFan Speed List: ' + ','.join(dev_stat[5]))
            i += 1

        i = 1
        for pool_stat in miner[5]:
            print('\tPool #' + str(i) + ':')
            print('\t\tURL: ' + pool_stat[0])
            print('\t\tStatus: ' + pool_stat[1])
            i += 1
        print("---------------------------------------------------------------")
