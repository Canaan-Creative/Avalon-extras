#!/usr/bin/env python
from __future__ import print_function
import re
import sys
import time
import threading
import Queue
import socket
import json
from readconfig import readconfig

def apiread(ip,command,lock,retry):
	time_out = 0
	while True:
		time_out += 1
		if time_out > retry:
			return None
		try:
			s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.settimeout(time_out)
			s.connect((ip,4028))

			s.send(json.dumps({"command":command}))

			response = s.recv(4096)
			while True:
				recv = s.recv(4096)
				if not recv:
					break
				else:
					response += recv

			response = response.replace('\x00','')
			s.close()
			return json.loads(response)
		except:
			lock.acquire()
			print("\033[31mConnection to " + ip + " lost. Extend time-out and try again.\033[0m")
			lock.release()



def socketthread(miner_queue,data0,lock,retry):
	while True:
		try:
			(miner_ip, miner_id) = miner_queue.get(False)

			err_conn_flag = False
			for k in range(0,retry):
				## try connecting for some times
				try:
					s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
					s.settimeout(1)
					s.connect((miner_ip,4028))
					s.close()
					break
				except:
					s.close()
					lock.acquire()
					if k < retry -1:
						print('\033[1m\033[33mCannot connect to ' + miner_ip + '. Try Again.\033[0m')
					else:
						print('\033[31mCannot connect to ' + miner_ip + '. Skip.\033[0m')
					lock.release()
					err_conn_flag = True
			if err_conn_flag:
				lock.acquire()
				data0[0][miner_id] = None
				data0[1][miner_id] = None
				data0[2][miner_id] = None
				data0[3][miner_id] = None
				lock.release()
				continue

			else:
				tmp=[]
				tmp.append(apiread(miner_ip, 'summary',lock,retry))
				tmp.append(apiread(miner_ip, 'devs',lock,retry))
				tmp.append(apiread(miner_ip, 'stats',lock,retry))
				tmp.append(apiread(miner_ip, 'pools',lock,retry))

				lock.acquire()
				data0[0][miner_id] = tmp[0]
				data0[1][miner_id] = tmp[1]
				data0[2][miner_id] = tmp[2]
				data0[3][miner_id] = tmp[3]
				print("Complete fetching data from " + miner_ip + ".")
				lock.release()

		except Queue.Empty:
			break


def chkstat(cfg):

	miner_queue = Queue.Queue()
	lock = threading.Lock()
	for i in range(0,len(cfg['miner_list'])):
		miner_queue.put((cfg['miner_list'][i],i))
	## data0[0]: -o summary
	## data0[1]: -o devs
	## data0[2]: -o stats
	## data0[3]: -o pools
	data0 = [['' for i in range(0,len(cfg['miner_list']))]for i in range(0,4)]

	threads = []
	for i in range(0,int(cfg['Telnet']['threads_num'])):
		threads.append(threading.Thread( target=socketthread, args=( miner_queue, data0, lock, int(cfg['Telnet']['retry']), ) ))
	for t in threads:
		t.start()
	for t in threads:
		t.join()
	print("Analyzing data ...",end="")
	sys.stdout.flush()


	data=[]
	i = 0
	while i < len(cfg['miner_list']):
		miner = []
		miner.append(cfg['miner_list'][i])
		if data0[1][i] == None:
			miner.append('Dead')
			miner.append('0')
			miner.append('0')
			miner.append([])
			miner.append([])
			miner.append('0')
			miner.append('8')
		else:
			dev = []
			pool = []

			## error list:
			## 1000 unenble to connect to port 4028
			## 0100 alive module num less than 75 percent
			## 0010 some module's temperature gets 255
			## 0001 some moduls's temperature is higher than 80
			error = 0

			try:
				for dd in data0[1][i]['DEVS']:
					dev_stat = []
					dev_stat.append(str(dd['Device Elapsed']))
					dev_stat.append(str(dd['Total MH']))
					dev_stat.append(str(dd['Temperature']))
					dev.append(dev_stat)
			except:
				pass
			j = 0


			sum_mn = 0
			err_255 = 0
			err_temp = 0

			try:
				for sd in data0[2][i]['STATS']:
					if sd['ID'][0:4] == 'POOL':
						#ignore pool stat in 'stats'
						break
					mn = 0
					temp = []
					fan = []


					for key in sd:
						if key[-10:] == 'MM Version':
							mn += 1
						elif key[0:11] == 'Temperature':
							temperature = sd[key]
							if temperature == 255:
								err_255 = 1
							elif temperature >= 80:
								err_temp = 1
							else: pass
							temp.append(str(sd[key]))
						elif key[0:3] == 'Fan':
							fan.append(str(sd[key]))
						else:
							pass

					dev[j].append(str(mn))
					dev[j].append(temp)
					dev[j].append(fan)

					sum_mn += mn

					j += 1
			except:
				pass

			error += err_255 * 2 + err_temp
			if sum_mn < .75 * int(cfg['mod_num_list'][i]):
				error += 4

			## when will 'devs' & 'stats' return different device numbers?
			while j < len(dev):
				print(cfg['miner_list'][i])
				## mod num
				dev[j].append('0')
				## temperature list
				dev[j].append([])
				## fan speed list
				dev[j].append([])
				j += 1

			try:
				for pd in data0[3][i]['POOLS']:
					pool_stat = []
					pool_stat.append(pd['Status'])
					pool_stat.append(pd['URL'])
					pool.append(pool_stat)
			except:
				pass

			miner.append('Alive')

			try:
				miner.append(str(data0[0][i]['SUMMARY'][0]['Elapsed']))
			except:
				miner.append('0')

			try:
				miner.append(str(data0[0][i]['SUMMARY'][0]['Total MH']))
			except:
				miner.append('0')

			miner.append(dev)
			miner.append(pool)

			try:
				miner.append(str(data0[0][i]['SUMMARY'][0]['MHS 15m']))
			except KeyError:
				miner.append('0')

			miner.append(str(error))

		data.append(miner)
		i += 1
	print(" Done.")
	return data

if __name__ == '__main__':
	exit()
	data = chkstat(cfg)
	for miner in data:
		print(miner[0] + ': ' + miner[1] + ' ' + miner[2] + ' ' + miner[3])
		i = 1
		for dev_stat in miner[4]:
			print('\tDevice #' + str(i) + ':')
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
		print("------------------------------------------------------------------------------")

