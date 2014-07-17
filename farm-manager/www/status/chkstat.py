#!/usr/bin/env python
import threading
import Queue
import socket
import json
import sys

def apiread(ip,port,command,retry):
	time_out = 0
	while True:
		time_out += 1
		if time_out > retry:
			return None
		try:
			s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.settimeout(time_out)
			s.connect((ip,int(port)))

			s.send(command)

			response = s.recv(4096)
			while True:
				recv = s.recv(4096)
				if not recv:
					break
				else:
					response += recv

			response = response.replace('\x00','')
			s.close()
			return response
		except:
			pass


def socketthread(miner_queue,data,lock,retry):
	while True:
		try:
			(miner_ip, miner_port, miner_pid) = miner_queue.get(False)

			err_conn_flag = False
			for k in range(0,retry):
				## try connecting for some times
				try:
					s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
					s.settimeout(1)
					s.connect((miner_ip,int(miner_port)))
					s.close()
					break
				except:
					s.close()
					err_conn_flag = True
			if err_conn_flag:
				continue

			else:
				tmp0 = apiread(miner_ip,miner_port,'summary',retry)
				tmp1 = apiread(miner_ip,miner_port,'devs',retry)
				tmp2 = apiread(miner_ip,miner_port,'stats',retry)
				tmp3 = apiread(miner_ip,miner_port,'pools',retry)
				lock.acquire()
				data[0][miner_pid] = tmp0
				data[1][miner_pid] = tmp1
				data[2][miner_pid] = tmp2
				data[3][miner_pid] = tmp3
				lock.release()

		except Queue.Empty:
			break

if __name__ == '__main__':

	retry = 3

	ip = sys.argv[1]
	ports = sys.argv[2:]

	threads_n = len(ports)

	miner_queue = Queue.Queue()
	lock = threading.Lock()

	for i in range(0,len(ports)):
		miner_queue.put((ip,ports[i],i))

	## data[0]: -o summary
	## data[1]: -o devs
	## data[2]: -o stats
	## data[3]: -o pools

	data = [[''for i2 in range(0,len(ports))]for i1 in range(0,4)]

	threads = []

	for i in range(0,threads_n):
		threads.append(threading.Thread( target=socketthread, args=( miner_queue, data, lock, retry, ) ))
	for t in threads:
		t.start()
	for t in threads:
		t.join()

	print json.dumps(data)

