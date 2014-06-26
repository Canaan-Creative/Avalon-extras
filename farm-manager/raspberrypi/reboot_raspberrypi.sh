#!/usr/bin/expect
log_user 0
set timeout 1
for {set i 21} {$i < 86} {incr i} {
	spawn telnet 192.168.1.$i 
	send "reboot -f\r"
	expect eof
	puts "reboot 192.168.1.$i ok"
}

