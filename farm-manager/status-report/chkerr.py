#!/usr/bin/env python
from __future__ import print_function
import sys

def chkerr(data,cfg,time):
	error_list = []
	error_log = ''
	i = 0
	for mminer in data:
		ip = mminer[0]
		dead_flag = True
		error_tmp = []
		j = 0
		for miner in mminer[1:]:
			port= miner[0]
			if miner[1] == "Dead":
				error_tmp.append({'id':ip + ':' + port,'error':[{'msg':'Connection Failed. ','color':'black'}]})
			else:
				dead_flag = False
				miss_flag = False
				if len(miner[4]) < len(cfg['dev_list'][i][j]):
					error_tmp.append({'id':ip + ':' + port,'error':[{'msg':'Missing Device. ','color':'blue'}]})
					miss_flag = True
				elif len(miner[4]) > len(cfg['dev_list'][i][j]):
					print('\033[1m\033[33mWe get more DEVs on ' + ip + ':' + port +'. Please modify your configuration file.\033[0m')
				k = 0
				for dev_stat in miner[4]:
					if not miss_flag:
						try:
							if int(dev_stat[3]) < int(cfg['dev_list'][i][j][k]):
								error_tmp.append({'id':ip + ':' + port + ' DEV#'+ str(k),'error':[{'msg':'Missing Module. ','color':'green'}]})
						except:
							pass
					for l in range(0,len(dev_stat[4])/2):
						t0 = int(dev_stat[4][l*2])
						t1 = int(dev_stat[4][l*2+1])
						error_msg = []
						if t0 >= 255 or t1 >= 255:
							error_msg.append({'msg':'Temperature 255. ','color':'purple'})
						if (t0 >= 88 and t0 < 255) or (t1 >= 88 and t1 < 255):
							error_msg.append({'msg':'Temperature over 88. ','color':'red'})
						elif (t0 >= 80 and t0 < 88) or (t1 >= 80 and t1 < 88):
							# ignore T>80 errors.
							if False:error_msg.append({'msg':'Temperature over 80. ','color':'orange'})
							else:pass
						else:pass
						if error_msg != []:
							error_tmp.append({'id':ip + ':' + port + ' DEV#' + str(k) + ', MOD#' + str(l+1),'error':error_msg})

					k += 1
			j += 1

		if dead_flag:
			error_list.append({'id':ip,'error':[{'msg':'Connection Failed. ','color':'black'}]})
		else:
			error_list += error_tmp

		i += 1
	for error in error_list:
		error_log += '\t' + error['id']+'\t'
		for msg in error['error']:
			error_log += msg['msg']
		error_log += '\n'
	print("Error List:")
	print(error_log,end="")
	sys.stdout.flush()

	logdir = cfg['General']['errlog_dir']
	filename = 'err_' + time.strftime("%Y_%m_%d_%H_%M") + '.log'
	logfile = open(logdir + filename, 'w')
	logfile.write(error_log)
	logfile.close()

	return error_list
