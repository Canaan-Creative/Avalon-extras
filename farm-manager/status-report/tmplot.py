#!/usr/bin/env python
from __future__ import print_function
from statlogging import readlog
import os
import re
import datetime
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg',warn=False)
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1 import ImageGrid
from matplotlib import gridspec

def tmplot(time_now,data,cfg):
	print("Plotting into " + cfg['TMplot']['img_dir'] + "tm-"+time_now.strftime("%Y_%m_%d_%H_%M")+".png ... ",end="")
	sys.stdout.flush()
	T = [[[] for i in range(0,int(cfg['Zone'+str(j+1)]['layers']))] for j in range(0,cfg['zone_num'])]
	#Temperature[Zone # -1][Layer # -1][Shelf # -1]
	i = 0
	n = 0
	T_sum = 0
	T_err = [[]for j in range(0,cfg['zone_num'])]
	T_err_255 = [[]for j in range(0,cfg['zone_num'])]

	z = 0
	zone = 'Zone1'
	for miner_stat in data:
		if i == len(cfg[zone]['miner_list']):
			z += 1
			i = 0
		zone = 'Zone'+str(z+1)
		T_max = 0
		err = False
		for dev_stat in miner_stat[4]:
			for T_single in dev_stat[4]:
				T_single = int(T_single)
				if T_single > T_max:
					if T_single != 255:
						T_max = T_single
					else:
						err = True
				if T_single > 0 and T_single<255 :
					T_sum += T_single
					n += 1
		if cfg[zone]['up_first'] == '1':
			layer_n = int(cfg[zone]['layers']) - 1 - i % int(cfg[zone]['layers'])
		else:
			layer_n = i % int(cfg[zone]['layers'])
		shelf_n = i / int(cfg[zone]['layers'])

		if n != 0 :
			T_avg = float(T_sum) / n
		else:
			T_avg = 256
			T_err[z].append([layer_n, shelf_n])
		T_sum = 0
		n = 0

		if T_max == 0: T_max = 256
		if err: T_err_255[z].append([layer_n, shelf_n])

		if cfg['TMplot']['method'] == 'max':
			T[z][layer_n].append(T_max)
		else:
			T[z][layer_n].append(T_avg)

		i += 1
	for z in range(0,cfg['zone_num']):
		T[z] = np.ma.masked_greater(T[z], 254.5)
	cmap = matplotlib.cm.jet
	norm = matplotlib.colors.Normalize(vmin=50, vmax=80)

	fig = plt.figure(figsize=(float(cfg['TMplot']['width'])/float(cfg['TMplot']['dpi']),float(cfg['TMplot']['height'])/float(cfg['TMplot']['dpi'])), dpi=int(cfg['TMplot']['dpi']), facecolor="white")
	titlefont = {'family' : cfg['TMplot']['font_family1'],
		'weight' : 'normal',
		'size'   : int(cfg['TMplot']['font_size1']),
		}
	labelfont = {'family' : cfg['TMplot']['font_family2'],
		'weight' : 'normal',
		'size'   : int(cfg['TMplot']['font_size2']),
		}
	ticks_font = matplotlib.font_manager.FontProperties(family=cfg['TMplot']['font_family3'], style='normal', size=int(cfg['TMplot']['font_size3']), weight='normal', stretch='normal')


	#read last tm-plotted log file
	data0 = data
	for pngfile in sorted(os.listdir(cfg['TMplot']['img_dir']),reverse=True):
		if re.match(r'tm-(\d+_){4}\d+\.png',pngfile):
			if datetime.datetime.strptime(pngfile,'tm-%Y_%m_%d_%H_%M.png') >= time_now:
				continue
			(data0 , time0, hr0,hr1) = readlog(cfg['General']['log_dir'], pngfile.replace('tm','log').replace('png','xml'))
			break

	plot_num = 0
	hr=[]
	for z in range(0,cfg['zone_num']):
		zone = 'Zone'+str(z+1)
		sub_plot_num = (int(cfg[zone]['shelves'])+int(cfg[zone]['plot_split'])-1)/int(cfg[zone]['plot_split'])
		for i in range(0,sub_plot_num):hr.append(int(cfg[zone]['layers']))
		plot_num += sub_plot_num
	gs = gridspec.GridSpec(plot_num, 2, width_ratios=[97,3],height_ratios=hr)

	ii = 0
	ll = 0
	jj = 0
	for z in range(0,cfg['zone_num']):
		zone = 'Zone'+str(z+1)
		for j in range(0,(int(cfg[zone]['shelves'])+int(cfg[zone]['plot_split'])-1)/int(cfg[zone]['plot_split'])):
			ax = plt.subplot(gs[j+jj,0])
			if j==0 and z == 0:
				## only the first plotted have title
				ax.set_title(cfg['TMplot']['title'],fontdict=titlefont)
			gci = ax.pcolormesh(T[z], cmap=cmap, norm = norm, edgecolors='white', linewidths=0)
			for p in T_err[z]:
				ax.add_patch(matplotlib.patches.Rectangle((p[1],p[0]),1,1,facecolor='none',edgecolor='r',hatch = '/'))
			for p in T_err_255[z]:
				ax.add_patch(matplotlib.patches.Rectangle((p[1],p[0]),1,1,facecolor='none',edgecolor='k',hatch = '\\'))

			for i in range(j*int(cfg[zone]['plot_split'])*int(cfg[zone]['layers']),(j+1)*int(cfg[zone]['plot_split'])*int(cfg[zone]['layers'])):
				try:
					miner = data[i+ii]
					miner0 = data0[i+ii]
				except IndexError:
					## have read all data
					break
				try:
					mod_num = cfg[zone]['mod_num_list'][i]
				except IndexError:
					## have read into another zone
					i -= 1
					break

				sum_mod_num = 0
				sum_mod_num0 = 0
				for dev_stat in miner[4]:
					sum_mod_num += int(dev_stat[3])
				for dev_stat0 in miner0[4]:
					sum_mod_num0 += int(dev_stat0[3])
				text_x = i/int(cfg[zone]['layers']) + .5 + float(cfg[zone]['text_x_shift'])
				text_y = int(cfg[zone]['layers']) - .5 - i % int(cfg[zone]['layers'])
				if miner[1] == 'Alive':
					l = len(miner[6].split('.')[0])
					if l > 2 and l < 6:
						rate = "%.2f" % (float(miner[6])/1000) + 'G'
					elif l > 5 and l < 9:
						rate = "%.2f" % (float(miner[6])/1000000) + 'T'
					else:
						rate = "%.2f" % (float(miner[6])) + 'M'
					ax.text(text_x, text_y, str(sum_mod_num)+'/'+mod_num, ha='right',va='bottom',fontproperties=ticks_font,color='k')
					ax.text(text_x, text_y, rate,ha='right',va='top',fontproperties=ticks_font,color='k')
					if sum_mod_num > sum_mod_num0:
						ax.text(text_x, text_y, r'$\blacktriangle\blacktriangle$',fontproperties=ticks_font,color='k',ha='left',va='bottom')
					elif sum_mod_num < sum_mod_num0:
						ax.text(text_x, text_y, r'$\blacktriangledown\blacktriangledown$',fontproperties=ticks_font,color='m',ha='left',va='bottom')
					else:
						pass
					if float(miner[6]) > float(miner0[6])*1.5:
						ax.text(text_x, text_y, r'$\blacktriangle\blacktriangle$',fontproperties=ticks_font,color='k',ha='left',va='top')
					elif float(miner[6]) > float(miner0[6])*1.1:
						ax.text(text_x, text_y, r'$\blacktriangle$',fontproperties=ticks_font,color='k',ha='left',va='top')
					elif float(miner[6]) < float(miner0[6])*0.5:
						ax.text(text_x, text_y, r'$\blacktriangledown\blacktriangledown$',fontproperties=ticks_font,color='m',ha='left',va='top')
					elif float(miner[6]) < float(miner0[6])*0.9:
						ax.text(text_x, text_y, r'$\blacktriangledown$',fontproperties=ticks_font,color='m',ha='left',va='top')
					else:
						pass

				else:
					ax.text(text_x - float(cfg[zone]['text_x_shift']), text_y,'N/A',ha='center',va='center',fontproperties=ticks_font,color='k')

			## single zone may have multi subplots
			## split according to cfg['Zone#'][plot_split]
			## method: alway plot the full fig in one subplot**, use x/ylim to cut print area out.
			## so no need to change xticks or xticklabels
			## 	** texts(mod_num,speed) not included, which must be writen according to subplot shelves, referring to the upper if-else.
			ax.set_xticks(np.linspace(0.5, int(cfg[zone]['shelves']) - 0.5, int(cfg[zone]['shelves'])))
			xl=[]
			for a in range(1 + ll, int(cfg[zone]['shelves'])+1 + ll): xl.append(str(a))
			yl=[]
			for a in range(1, int(cfg[zone]['layers'])+1): yl.append(str(a))


			ax.set_xticklabels(tuple(xl))

			ax.set_yticks(np.linspace(0.5,int(cfg[zone]['layers'])-0.5,int(cfg[zone]['layers'])))
			ax.set_yticklabels(tuple(yl))

			for label in ax.get_xticklabels() :
				label.set_fontproperties(ticks_font)
			for label in ax.get_yticklabels() :
				label.set_fontproperties(ticks_font)

			ax.set_ylabel("Layers",fontdict=labelfont)
			ax.tick_params(tick1On = False, tick2On = False)

			ax.set_xlim(j * int(cfg[zone]['plot_split']), (j + 1) * int(cfg[zone]['plot_split']))
			ax.set_ylim(0,int(cfg[zone]['layers']))

		## zone start num : ll - shelf, ii - miner, jj - x-split
		ll += int(cfg[zone]['shelves'])
		ii += i + 1
		jj += j + 1

	## only the last plotted have x-axis label
	ax.set_xlabel("Shelves",fontdict=labelfont)

	## color bar
	ax = plt.subplot(gs[0:,1])
	cbar = plt.colorbar(gci, cax = ax)
	cbar.set_label('Temperature ($^{\circ}C$)',fontdict=labelfont)
	cbar.set_ticks(np.linspace(50,80,4))
	cbar.set_ticklabels( ('50', '60', '70', '80'))
	for tick in cbar.ax.yaxis.majorTicks:
		tick.label2.set_fontproperties(ticks_font)

	plt.tight_layout()

	plt.savefig(cfg['TMplot']['img_dir'] + "tm-"+time_now.strftime("%Y_%m_%d_%H_%M")+".png")
	plt.clf()
	print("Done.")
	return "tm-"+time_now.strftime("%Y_%m_%d_%H_%M")+".png"

