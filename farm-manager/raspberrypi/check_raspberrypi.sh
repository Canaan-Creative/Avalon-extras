#!/usr/bin/expect
log_user 0
set timeout 3
for {set i 21} {$i < 86} {incr i} {
	spawn telnet 192.168.1.$i 
	expect {
		"OpenWrt:" {
			send "cgminer-api -o devs | grep \"MHS\ 5s=0.00\" &> /dev/null\r"
			send "echo code=$?\r"
			set result 0 
			expect {
				"code=0" { set result 1 }
			}	
			send "exit\r"
			expect eof

			if {$result == 1} {
				puts "192.168.1.$i NG"
			}
		}
	}
}

