#!/usr/bin/env python2

from __future__ import print_function
import json


def renderpage(time, data, err, tmap_data, cfg):
    info = {}
    info['time'] = time.strftime("%Y.%m.%d %H:%M")

    alivenum = 0
    for mminer in data:
        alive_flag = False
        for miner in mminer[1:]:
            if miner[1] == "Alive":
                alive_flag = True
        if alive_flag:
            alivenum += 1

    minernum = len(cfg['miner_list'])
    for i in cfg['mod_num_list']:
        if int(i) == 0:
            minernum -= 1

    info['active_ip_num'] = str(alivenum) + '/' + str(minernum)

    info['err_miner_list'] = err

    sum_mod_num = 0
    for mminer in data:
        for miner in mminer[1:]:
            for dev_stat in miner[4]:
                sum_mod_num += int(dev_stat[3])
    sum_mod_num0 = 0
    for mod_num in cfg['mod_num_list']:
        sum_mod_num0 += int(mod_num)
    info['alive_mod_num'] = str(sum_mod_num) + '/' + str(sum_mod_num0)

    info['zone'] = tmap_data['zone']

    status = json.dumps(info)
    try:
        f_s = open(cfg['Webpage']['stat_json'], 'w')
        f_s.write(status)
        f_s.close()
    except Exception, e:
        print(str(e))
