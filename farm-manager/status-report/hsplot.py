#!/usr/bin/env python
from __future__ import print_function
from statlogging import readlog
from readconfig import readconfig

import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import numpy as np

import datetime
import re
import os
import sys

def readhs(time0,cfg):
	deltaT = datetime.timedelta(hours=25)
	xmllog = []

	t_datetime=[]
	#find log file in range from $time-$deltaT to $time
	for logfile in sorted(os.listdir(cfg['General']['log_dir']),reverse=True):
		if re.match(r'log-(\d+_){4}\d+\.xml',logfile):
			logtime = datetime.datetime.strptime(logfile.strip('log-').strip('.xml'),"%Y_%m_%d_%H_%M")
			xmllog.append(logfile)
			if logtime + deltaT < time0:
				break
	if len(xmllog) < 3:
		print("More log files are needed for plotting.")
		raise NameError

	#read hash num & elapsed time into $h[time point(0:)][miner No][]
	#calculate hash speed into v[time point(ignore #1)]
	xmllog = xmllog[::-1]

	h = []
	t = []
	v = []
	vp = []
	vps = []

	(data,time,sum_pool_rate,pool_rate) = readlog(cfg['General']['log_dir'],xmllog[0])
	ht=[]
	for i in range(0,len(data)):
		if data[i][1] == "Alive":
			ht.append( [ float(data[i][3]),float(data[i][2]) ] )
		else:
			ht.append( [0,0] )
	h.append(ht)
	t.append((time-time0).total_seconds())

	for k in range(1,len(xmllog)):
		(data,time,sum_pool_rate,pool_rate) = readlog(cfg['General']['log_dir'],xmllog[k])
		tt = (time-time0).total_seconds()
		ht=[]
		vt=[]
		print(xmllog[k])
		for i in range(0,len(data)):
			if data[i][1] == "Dead":
				vt.append(0)
				ht.append( [0,0] )
			else:
				ht.append( [ float(data[i][3]),float(data[i][2]) ] )
				if ht[i][1] - h[k-1][i][1] > tt - t[k-1] - int(cfg['HSplot']['delay_time']):
					vt.append((ht[i][0]-h[k-1][i][0])/(ht[i][1]-h[k-1][i][1]))
				elif data[i][2] != '0':
					vt.append(ht[i][0]/ht[i][1])
				else:
					vt.append(0)
		t.append(tt)
		h.append(ht)
		v.append(vt)
		vp.append(float(pool_rate))
		vps.append(float(sum_pool_rate))


	t = t[1:]
	h = h[1:]

	return (t,h,v,vp,vps)

def hsplot(time0,cfg):


	print("Reading Logs: ")
	try:
		(t,h,v,vp,vps) = readhs(time0,cfg)
	except NameError:
		return 1
	print("Done.\nPlotting into " + cfg['HSplot']['img_dir'] + "hs-"+time0.strftime("%Y_%m_%d_%H_%M")+".png ... ",end="")
	sys.stdout.flush()

	#total hash speed
	vm = []
	for k in range(0,len(v)):
		vm.append( sum(v[k]) )
		t[k] = t[k]/3600.0


	x = np.array(t)
	y1 = np.array(vm)
	y2 = np.array(vp)
	y3 = np.array(vps)
	ymax = np.amax(np.hstack((y1,y2,y3)))

	f1 = interp1d(x, y1)
	f2 = interp1d(x, y2)
	f3 = interp1d(x, y3)

	xnew = np.linspace(t[0], t[-1], 1800)


	fig = plt.figure(figsize=(float(cfg['HSplot']['width'])/float(cfg['HSplot']['dpi']),float(cfg['HSplot']['height'])/float(cfg['HSplot']['dpi'])), dpi=int(cfg['HSplot']['dpi']), facecolor="white")
	titlefont = {'family' : cfg['HSplot']['font_family1'],
		 'weight' : 'normal',
		 'size'   : int(cfg['HSplot']['font_size1']),
		 }
	ticks_font = matplotlib.font_manager.FontProperties(family=cfg['HSplot']['font_family2'], style='normal', size=int(cfg['HSplot']['font_size2']), weight='normal', stretch='normal')

	p1, = plt.plot(xnew,f1(xnew),'b-')
	p2, = plt.plot(xnew,f2(xnew),'g-')
	p3, = plt.plot(xnew,f3(xnew),'r-')
	plt.legend((p1,p2,p3),('Local','Worker','Pool'), loc = 2, prop = ticks_font)
	# x axis tick label
	xticklabel = []
	xmax = time0 - datetime.timedelta(seconds = (time0.hour - (time0.hour/2)*2)*3600 + time0.minute*60)
	xmin = xmax
	xticklabel.append(xmin.strftime("%H:%M"))
	for i in range(0,12):
		xmin = xmin - datetime.timedelta(seconds=7200)
		xticklabel.append(xmin.strftime("%H:%M"))
	xticklabel = xticklabel[::-1]


	# y axis tick label
	ymax_s = str(int(ymax))
	flag = int(ymax_s[0])
	yticklabel = ['0']
	if flag == 1:
		#0.1;0.2;0.3....
		ystep = 1*(10**(len(ymax_s)-2))
		ylim = int(ymax + ystep -1) / ystep * ystep
		for i in range(1,int(ylim/ystep) ):
			yticklabel.append("{:,}".format(i*(10 ** (len(ymax_s)-2))))
	elif flag >= 2 and flag <= 3:
		#0.2;0.4;0.6...
		ystep = 2*(10**(len(ymax_s)-2))
		ylim = int(ymax + ystep -1) / ystep * ystep
		for i in range(1,int(ylim/ystep) ):
			yticklabel.append("{:,}".format(i*2*(10 ** (len(ymax_s)-2))))
	elif flag >= 4 and flag <= 6:
		#0.25;0.50;0.75...
		ystep = 25*(10**(len(ymax_s)-3))
		ylim = int(ymax + ystep -1) / ystep * ystep
		for i in range(1,int(ylim/ystep) ):
			yticklabel.append("{:,}".format(i*25*(10 ** (len(ymax_s)-3))))
	else:
		#0.5;1.0;1.5...
		ystep = 5*(10**(len(ymax_s)-2))
		ylim = int(ymax + ystep -1) / ystep * ystep
		for i in range(1,int(ylim/ystep) ):
			yticklabel.append("{:,}".format(i*5*(10 ** (len(ymax_s)-2))))

	ax=plt.gca()
	ax.set_xticks(np.linspace((xmin-time0).total_seconds()/3600.0,(xmax-time0).total_seconds()/3600.0,13))
	ax.set_xticklabels( tuple(xticklabel) )
	ax.set_yticks(np.linspace(0,ylim-ystep,len(yticklabel)))
	ax.set_yticklabels( tuple(yticklabel) )

	ax.tick_params(tick1On = False, tick2On = False)
	ax.spines['right'].set_visible(False)
	ax.spines['top'].set_visible(False)

	ax.set_title(cfg['HSplot']['title'],fontdict=titlefont)

	for label in ax.get_xticklabels() :
		label.set_fontproperties(ticks_font)
	for label in ax.get_yticklabels() :
		label.set_fontproperties(ticks_font)

	plt.axis([-24, 0, 0, ylim])

	plt.grid(color = '0.75', linestyle='-')
	plt.tight_layout()


	plt.savefig(cfg['HSplot']['img_dir'] + "hs-"+time0.strftime("%Y_%m_%d_%H_%M")+".png")
	print("Done.")
	plt.clf()
	return "hs-"+time0.strftime("%Y_%m_%d_%H_%M")+".png"



if __name__ == '__main__':
	exit()
	cfg['Miner']['miner_list'] = list(filter(None, (x.strip() for x in cfg['Miner']['miner_list'].splitlines())))
	plot(datetime.datetime.now(),cfg)
