#!/usr/bin/env python2

import datetime
import argparse
import os
import re

from sendmail import sendmail
from chkstat import chkstat
from statlogging import writelog
from statlogging import readlog
from hsplot import hsplot
from readconfig import readconfig
from tmplot import tmplot
from renderpage import renderpage
from chkerr import chkerr
from chkrate import chkrate
from chkblock import chkblock


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate "
                                     "miner status report.")
    parser.add_argument("-n", "--nolog", help="do not write xml log; will use "
                        "former generated log files to plot hashrate graph "
                        "if '-p' is selected.", action="store_true")
    parser.add_argument("-r", "--nopoolhashrate", help="do not fetch "
                        "pool hashrate.", action="store_true")
    parser.add_argument("-m", "--email", help="send email.",
                        action="store_true")
    parser.add_argument("-w", "--webpage", help="render webpage.",
                        action="store_true")
    parser.add_argument("-p", "--hsplot", help="plot hash speed graph.",
                        action="store_true")
    parser.add_argument("-t", "--tmplot", help="plot temperature map.",
                        action="store_true")
    parser.add_argument("-c", "--config", type=str, help="use another config "
                        "file rather than ./statreport.conf.")
    args = parser.parse_args()

    if args.config:
        cfg = readconfig(args.config)
    else:
        cfg = readconfig("./statreport.conf")

    time_now = datetime.datetime.now()

    data0 = None
    time_old = None
    for logfile in sorted(os.listdir(cfg['General']['log_dir']), reverse=True):
        if re.match(r'log-(\d+_){4}\d+\.xml', logfile):
            (data0, time_old) = readlog(cfg['General']['log_dir'], logfile)
            break

    luckyID = []
    if not args.nolog:
        data = chkstat(cfg)
        (data, luckyID) = chkblock(data, data0)
        if not args.nopoolhashrate:
            hashrate = chkrate(data, data0, cfg, time_now, time_old)
        err = chkerr(data, cfg, time_now, data0)
        writelog(data, cfg,
                 "log-" + time_now.strftime("%Y_%m_%d_%H_%M") + ".xml")
    if args.hsplot:
        if args.nolog:
            time_now = time_old
        if args.nolog or args.nopoolhashrate:
            hashrate = chkrate(None, None, cfg, time_now, time_old)
        hspng = hsplot(hashrate, cfg, time_now)
        if hspng != 1:
            cfg['Email']['hsimg_dir'] = cfg['HSplot']['img_dir']
            cfg['Email']['hsimg'] = hspng

    if args.webpage or args.email or args.tmplot:
        if args.nolog:
            data = data0
            time_now = time_old
            err = chkerr(data, cfg, time_now)

    if args.tmplot:
        (tmpng, tmap_data) = tmplot(time_now, data, cfg)
        cfg['Email']['tmimg_dir'] = cfg['TMplot']['img_dir']
        cfg['Email']['tmimg'] = tmpng

    if args.webpage:
        renderpage(time_now, data, err, tmap_data, cfg)
    if args.email or luckyID:
        sendmail(time_now.strftime("%Y-%m-%d %H:%M"), data, err, cfg, luckyID)
