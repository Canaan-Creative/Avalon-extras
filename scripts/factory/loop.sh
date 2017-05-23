#!/bin/bash
while true; do
	cd /home/factory/Avalon-extras/scripts/factory
	bash -c "$*"
	echo
	read -p "Press any key to burn next"
done
