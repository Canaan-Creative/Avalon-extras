#!/usr/bin/env python
from sendmail import sendmail
from chkstat import chkstat
from statlogging import writelog
from statlogging import readlog
from hsplot import hsplot
from readconfig import readconfig
from tmplot import tmplot
import datetime
import argparse
import os
import re

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Generate miner status report.")
	parser.add_argument("-n","--nolog", help="do not write xml log; will use former generated log files to plot hashrate graph if '-p' is selected.", action="store_true")
	parser.add_argument("-m","--email", help="send email.", action="store_true")
	parser.add_argument("-p","--hsplot", help="plot hash speed graph.", action="store_true")
	parser.add_argument("-t", "--tmplot", help="plot temperature map.", action="store_true")
	parser.add_argument("-c","--config", type=str, help="use another config file rather than ./statreport.conf.")
	args = parser.parse_args()


	if args.config:
		cfg = readconfig(args.config)
	else:
		cfg = readconfig("./statreport.conf")
	if cfg['Log']['directory'][-1] != '/':
		cfg['Log']['directory'] += '/'
	if cfg['HSplot']['img_dir'][-1] != '/':
		cfg['HSplot']['img_dir'] += '/'
	if cfg['TMplot']['img_dir'][-1] != '/':
		cfg['TMplot']['img_dir'] += '/'
	if not os.path.isdir(cfg['Log']['directory']):
		os.makedirs(cfg['Log']['directory'])
	if not os.path.isdir(cfg['HSplot']['img_dir']):
		os.makedirs(cfg['HSplot']['img_dir'])
	if not os.path.isdir(cfg['TMplot']['img_dir']):
		os.makedirs(cfg['TMplot']['img_dir'])
	cfg['Miner']['miner_list'] = list(filter(None, (x.strip() for x in cfg['Miner']['miner_list'].splitlines())))



	time_now = datetime.datetime.now()

	if not args.nolog:
		data = chkstat(cfg)
		writelog(data,cfg['Log']['directory'],"log-" + time_now.strftime("%Y_%m_%d_%H_%M") + ".xml")

	if args.hsplot:
		hspng = hsplot(time_now,cfg)
		if hspng != 1:
			cfg['Email']['hsimg_dir'] = cfg['HSplot']['img_dir']
			cfg['Email']['hsimg'] = hspng

	if args.tmplot:
		if args.nolog:
			for logfile in sorted(os.listdir(cfg['Log']['directory']),reverse=True):
				if re.match(r'log-(\d+_){4}\d+\.xml',logfile):
					(data , time_now) = readlog(cfg['Log']['directory'], logfile)
					break
		tmpng = tmplot(time_now,data,cfg)
		cfg['Email']['tmimg_dir'] = cfg['TMplot']['img_dir']
		cfg['Email']['tmimg'] = tmpng
	if args.email:
		if args.nolog:
			for logfile in sorted(os.listdir(cfg['Log']['directory']),reverse=True):
				if re.match(r'log-(\d+_){4}\d+\.xml',logfile):
					(data , time_now) = readlog(cfg['Log']['directory'], logfile)
					break
		sendmail(time_now.strftime("%Y-%m-%d %H:%M"),data,cfg)

