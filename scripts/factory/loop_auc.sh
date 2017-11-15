#!/bin/bash
while true; do
	cd /home/factory/Avalon-extras/scripts/factory
	bash -c "$*"
	echo -e "OK OK OK OK OK OK OK OK    OK                   OK\nOK                   OK    OK                OK\nOK                   OK    OK             OK\nOK                   OK    OK          OK\nOK                   OK    OK       OK\nOK                   OK    OK    OK \nOK                   OK    OK OK\nOK                   OK    OK    OK \nOK                   OK    OK       OK\nOK                   OK    OK          OK\nOK                   OK    OK             OK\nOK                   OK    OK                OK\nOK                   OK    OK                   OK\nOK OK OK OK OK OK OK OK    OK                      OK"
	sleep 3
done
