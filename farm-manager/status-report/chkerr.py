#!/usr/bin/env python2

from __future__ import print_function
import sys


def int_alt(s):
    try:
        return int(s)
    except:
        return -1


def float_alt(s):
    try:
        return float(s)
    except:
        return -1


def chkerr(data, cfg, time):
    error_list = []
    error_log = ''
    i = 0
    for mminer in data:
        ip = mminer[0]
        dead_flag = True
        error_tmp = []
        j = 0
        for miner in mminer[1:]:
            port = miner[0]
            if miner[1] == "Dead":
                if int(cfg['mod_num_list'][i]):
                    error_tmp.append({'id': ip + ':' + port,
                                      'error': [{'msg': 'Connection Failed. ',
                                                 'color': 'black'}]})
            else:
                dead_flag = False
                miss_flag = False
                if len(miner[4]) < len(cfg['dev_list'][i][j]):
                    error_tmp.append({'id': ip + ':' + port,
                                      'error': [{'msg': 'Missing Device. ',
                                                 'color': 'red'}]})
                    miss_flag = True
                elif len(miner[4]) > len(cfg['dev_list'][i][j]):
                    print('\033[1m\033[33mWe get more DEVs on ' +
                          ip + ':' + port +
                          '. Please modify your configuration file.\033[0m')

                lw_sum = 0
                lw_n = 0
                for dev_stat in miner[4]:
                    for lw_s in dev_stat[6]:
                        lw = int_alt(lw_s)
                        if lw > 0:
                            lw_sum += lw
                            lw_n += 1
                try:
                    lw_avg = float(lw_sum) / lw_n
                except:
                    lw_avg = 0

                k = 0
                for dev_stat in miner[4]:
                    if not miss_flag:
                        try:
                            if int(dev_stat[3]) < int(cfg['dev_list'][i][j][k]):
                                error_tmp.append({'id': ip + ':' + port +
                                                  ' DEV#' + str(k),
                                                  'error':
                                                  [{'msg': 'Missing Module. ',
                                                    'color': 'red'}]})
                        except:
                            pass

                    for p in range(0, len(dev_stat[4])/2):
                        t0 = int_alt(dev_stat[4][p*2])
                        t1 = int_alt(dev_stat[4][p*2+1])
                        f0 = int_alt(dev_stat[5][p*2])
                        f1 = int_alt(dev_stat[5][p*2+1])
                        lw = int_alt(dev_stat[6][p])
                        dh = float_alt(dev_stat[7][p])
                        volt = int_alt(dev_stat[8][p])
                        freq = int_alt(dev_stat[9][p])
                        error_msg = []
                        if t0 >= 255 or t1 >= 255:
                            error_msg.append({'msg': 'Temperature 255. ',
                                              'color': 'purple'})
                        if (t0 >= 88 and t0 < 255) or (t1 >= 88 and t1 < 255):
                            error_msg.append({'msg': 'Temperature over 88. ',
                                              'color': 'red'})
                        elif (t0 >= 80 and t0 < 88) or (t1 >= 80 and t1 < 88):
                            # ignore T>80 errors.
                            if False:
                                error_msg.append({'msg': 'Temperature '
                                                  'over 80. ',
                                                  'color': 'orange'})
                            else:
                                pass
                        elif t0 < 40 and t1 < 40 and t0 >= 0 and t1 >= 0:
                            error_msg.append({'msg': 'Temperature '
                                              'lower than 40. ',
                                              'color': 'blue'})
                        else:
                            pass

                        if f0 == 0 and f1 == 0:
                            error_msg.append({'msg': 'Fan stopped. ',
                                              'color': 'green'})
                        if lw >= 0 and (lw_avg - lw) / lw_avg > 0.2:
                            error_msg.append({'msg': 'Local work too low. ',
                                              'color': 'green'})
                        if dh > 5:
                            error_msg.append({'msg': 'Device hardware error '
                                              'too high. ',
                                              'color': 'green'})
                        if volt != int(cfg['General']['voltage']) and volt >= 0:
                            error_msg.append({'msg': 'Wrong voltage. ',
                                              'color': 'green'})
                        if freq != int(cfg['General']['frequency']
                                       ) and freq >= 0:
                            # ignore
                            if False:
                                error_msg.append({'msg': 'Wrong frequency. ',
                                                  'color': 'green'})
                        if error_msg != []:
                            error_tmp.append({'id': ip + ':' + port +
                                              ' DEV#' + str(k) + ', MOD#' +
                                              str(p+1),
                                              'error': error_msg})
                    k += 1
            j += 1

        if dead_flag:
            if int(cfg['mod_num_list'][i]):
                error_list.append({'id': ip,
                                   'error': [{'msg': 'Connection Failed. ',
                                              'color': 'black'}]})
        else:
            error_list += error_tmp

        i += 1
    for error in error_list:
        error_log += '\t' + error['id']+'\t'
        for msg in error['error']:
            error_log += msg['msg']
        error_log += '\n'
    print("Error List:")
    print(error_log, end="")
    sys.stdout.flush()

    logdir = cfg['General']['errlog_dir']
    filename = 'err_' + time.strftime("%Y_%m_%d_%H_%M") + '.log'
    logfile = open(logdir + filename, 'w')
    logfile.write(error_log)
    logfile.close()

    return error_list
