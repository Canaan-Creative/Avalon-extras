# Miner-Automate-Test-Scripts

## Usage:

	(1) Set DDS238-2 ZN/S Power instrument ID value:
	cd ./set-dev-id/python2/3

	sudo ./set-device-id.py
	Prompting input current device id value: 1 ~ 247
	Prompting input setting new device id value: 1 ~ 247
	After running finish it will prompt done.

	(2) Read Miner Power value and Miner debuglog messages:
	cd ./read-datas

	(3) Modify miner-options.conf setting options
	TIME option: running time for different options
	C_IP: cgminer rpi ip address
	P_IP: power rpi ip address
	More Options: cgminer configuration options

	(4) Statistical datas
	./mds.sh

	After done it will generate cvs files and log files.
