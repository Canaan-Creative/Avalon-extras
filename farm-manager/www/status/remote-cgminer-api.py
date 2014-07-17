#!/usr/bin/env python
import socket
import json
import sys

def linesplit(socket):
	buffer = socket.recv(4096)
	while True:
		more = socket.recv(4096)
		if not more:
			break
		else:
			buffer = buffer+more
	if buffer:
		return buffer

api_command = sys.argv[1].split('|')

if len(sys.argv) < 3:
	api_ip = '127.0.0.1'
	api_port = 4028
else:
	api_ip = sys.argv[2]
	api_port = sys.argv[3]

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((api_ip,int(api_port)))
if len(api_command) == 2:
	s.send(json.dumps({"command":api_command[0],"parameter":api_command[1]}))
else:
	s.send(json.dumps({"command":api_command[0]}))

response = linesplit(s)
response = response.replace('\x00','')
response = json.loads(response)
print response
s.close()

