#!/usr/bin/env python
from __future__ import print_function
import telnetlib
import sys
import time

def restart_cgminer(ip,ports):
	retry = 3
	flag = "root@OpenWrt:/# "
	for i in range(0,retry):
		tn = telnetlib.Telnet()
		err_conn_flag = False
		for k in range(0,retry):
			## try connecting for some times
			try:
				tn.open( ip , 23 )
				break
			except:
				tn.close()
				if k < retry -1:
					print('\033[1m\033[33mCannot connect to ' + ip + '. Try Again.\033[0m')
				else:
					print('\033[31mCannot connect to ' + ip + '. Skip.\033[0m')
				err_conn_flag = True
		if err_conn_flag:
			break
		try:
			tn.read_until(flag)
			if ports != None:
				tn.write('/etc/init.d/cgminer restart ' + ' '.join(ports) + '\n')
			else:
				tn.write('/etc/init.d/cgminer restart\n')
			tn.read_until(flag)
			tn.write('exit\n')
			tn.read_all()
		except:
			tn.close()
			print("\033[31mConnection to " + ip + " lost. Extend time-out and try again.\033[0m")
			continue
		tn.close()
		print("Update complete @" + ip + ".")
		break

if __name__ == '__main__':

	ip = sys.argv[1]
	if len(sys.argv) < 2: ports = None
	else:
		ports=[]
		for i in range(2,len(sys.argv)):
			port = int(sys.argv[i])
			if port < 6000 or port > 6020:
				ports = None
				break
			else:
				ports.append( str( port - 6000 ) )
	restart_cgminer(ip,ports)
