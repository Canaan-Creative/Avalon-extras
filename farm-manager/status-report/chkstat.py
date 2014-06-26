#!/usr/bin/env python
import telnetlib
import re
import time
import threading
import Queue
from readconfig import readconfig

def telnetthread(miner_queue,data0,lock,retry):
	while True:
		try:
			(miner_ip, miner_id) = miner_queue.get(False)
			time_out = 0
			while True:
				time_out += 1
				tn = telnetlib.Telnet()

				err_conn_flag = False
				for k in range(0,retry):
					## try connecting for some times
					try:
						tn.open( miner_ip,23, time_out )
						break
					except:
						tn.close()
						lock.acquire()
						if k < retry -1:
							print '\033[1m\033[33mCannot connect to ' + miner_ip + '. Try Again.\033[0m'
						else:
							print '\033[31mCannot connect to ' + miner_ip + '. Skip.\033[0m'
						lock.release()
						err_conn_flag = True
				if err_conn_flag:
					lock.acquire()
					data0[0][miner_id] = ''
					data0[1][miner_id] = ''
					data0[2][miner_id] = ''
					data0[3][miner_id] = ''
					lock.release()
					break

				try:
					## read summary ##
					tn.write('cgminer-api -o summary\n')

					## read devs ##
					tn.write('cgminer-api -o devs\n')

					## read stats ##
					tn.write('cgminer-api -o stats\n')

					## read pools ##
					tn.write('cgminer-api -o pools\n')

					tn.write('exit\n')

					tmp = tn.read_all().split('cgminer-api')

				except:
					tn.close()
					lock.acquire()
					print "\033[31mConnection to " + miner_ip + " lost. Extend time-out and try again.\033[0m"
					lock.release()
					continue

				tn.close()

				##!!!!!!!!! Bug Warning: very small chance...
				##!!!!!!!!! Condition: Some dev gets down between running these 'cgminer-api' commands
				##!!!!!!!!! Result: Different dev num in dev_data & stat_data
				lock.acquire()
				data0[0][miner_id] = tmp[-4]
				data0[1][miner_id] = tmp[-3]
				data0[2][miner_id] = tmp[-2]
				data0[3][miner_id] = tmp[-1]
				print "Complete fetching data from " + miner_ip + "."
				lock.release()
				break
		except Queue.Empty:
			break


def chkstat(cfg):

	elapsed_time_flag       = re.compile('Device Elapsed=(.*)$')
	total_Mh_flag           = re.compile('Total MH=([^,]*),')
	temperature_d_flag      = re.compile('Temperature=([^,]*),')
	module_id_flag          = re.compile('ID\d MM Version')
	temperature_s_flag      = re.compile('Temperature(\d=[^,]*),')
	fan_flag                = re.compile('Fan(\d=[^,]*),')
	pool_url_flag           = re.compile('URL=([^,]*),')
	pool_alive_flag         = re.compile('Status=([^,]*),')
	miner_15m_flag          = re.compile('MHS 15m=([^,]*),')
	## ignore pool stat in ' -o stats'
	stat_pool_flag          = re.compile('ID=POOL')

	miner_queue = Queue.Queue()
	lock = threading.Lock()
	for i in range(0,len(cfg['Miner']['miner_list'])):
		miner_queue.put((cfg['Miner']['miner_list'][i],i))
	## data0[0]: -o summary
	## data0[1]: -o devs
	## data0[2]: -o stats
	## data0[3]: -o pools
	data0 = [['' for i in range(0,len(cfg['Miner']['miner_list']))]for i in range(0,4)]

	threads = []
	for i in range(0,int(cfg['Telnet']['threads_num'])):
		threads.append(threading.Thread( target=telnetthread, args=( miner_queue, data0, lock, int(cfg['Telnet']['retry']), ) ))
	for t in threads:
		t.start()
	for t in threads:
		t.join()
	print "Analyzing data ...",
	data=[]
	i = 0
	while i < len(cfg['Miner']['miner_list']):
		miner = []
		miner.append(cfg['Miner']['miner_list'][i])
		if data0[1][i] == '':
			miner.append('Dead')
			miner.append('0')
			miner.append('0')
			miner.append([])
			miner.append([])
		else:
			dev = []
			pool = []
			for dd in data0[1][i].split('|')[1:-1]:
				dev_stat = []
				dev_stat.append(elapsed_time_flag.search(dd).group(1))
				dev_stat.append(total_Mh_flag.search(dd).group(1))
				dev_stat.append(temperature_d_flag.search(dd).group(1))
				dev.append(dev_stat)

			j = 0
			for sd in data0[2][i].split('|')[1:-1]:
				if stat_pool_flag.search(sd) != None:
					#ignore pool stat in ' -o stats'
					break

				dev[j].append(len(module_id_flag.findall(sd)))

				temp = []
				for t in temperature_s_flag.findall(sd):
					temp.append(t.split('=')[1])
				dev[j].append(temp)

				fan = []
				for f in fan_flag.findall(sd):
					fan.append(f.split('=')[1])
				dev[j].append(fan)

				j += 1

			for pd in data0[3][i].split('|')[1:-1]:
				pool_stat = []
				pool_stat.append(pool_url_flag.search(pd).group(1))
				pool_stat.append(pool_alive_flag.search(pd).group(1))
				pool.append(pool_stat)

			miner.append('Alive')
			try:
				miner.append(re.search(r'Elapsed=([^,]*),',data0[0][i]).group(1))
			except AttributeError:
				print cfg['Miner']['miner_list'][i]
				print data0[0][i]
				print data0[1][i]
				print data0[2][i]
				print data0[3][i]
				miner.append('0')
			try:
				miner.append(total_Mh_flag.search(data0[0][i]).group(1))
			except AttributeError:
				miner.append('0')
			miner.append(dev)
			miner.append(pool)
			try:
				miner.append(miner_15m_flag.search(data0[0][i]).group(1))
			except AttributeError:
				miner.append('0')
		data.append(miner)
		i += 1
	print " Done."
	return data

if __name__ == '__main__':
	cfg = readconfig("./statreport.conf")
	if cfg['Log']['directory'][-1] == '/':
		cfg['Log']['directory'] += '/'
	cfg['Miner']['miner_list'] = list(filter(None, (x.strip() for x in cfg['Miner']['miner_list'].splitlines())))
	data = chkstat(cfg)
	for miner in data:
		print miner[0] + ': ' + miner[1] + ' ' + miner[2] + ' ' + miner[3]
		i = 1
		for dev_stat in miner[4]:
			print '\tDevice #' + str(i) + ':'
			print '\t\tDevice Elapsed: ' + dev_stat[0]
			print '\t\tTotal MH: ' + dev_stat[1]
			print '\t\tTemperature: ' + dev_stat[2]
			print '\t\tModules Number: ' + str(dev_stat[3])
			print '\t\tTemperature List: ' + ','.join(dev_stat[4])
			print '\t\tFan Speed List: ' + ','.join(dev_stat[5])
			i += 1

		i = 1
		for pool_stat in miner[5]:
			print '\tPool #' + str(i) + ':'
			print '\t\tURL: ' + pool_stat[0]
			print '\t\tStatus: ' + pool_stat[1]
			i += 1
		print "------------------------------------------------------------------------------"

