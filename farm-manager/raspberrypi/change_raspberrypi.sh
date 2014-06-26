#!/usr/bin/expect
log_user 0
for {set i 98} {$i < 99} {incr i} {
	spawn telnet 192.168.1.$i 
	expect {
		"OpenWrt:" {
			send "cd /etc/config\r"
			send "wget http://$argv/raspberry/config/cgminer.avalon3\r"
			send "mv cgminer.avalon3 cgminer\r"
			send "rm system\r"
			send "wget http://$argv/raspberry/config/system\r"
			send "cd /tmp\r"
			send "wget http://$argv/raspberry/config/02-pcgminer\r"
			send "chmod +x 02-pcgminer\r"
			send "./02-pcgminer\r"
			send "rm 02-pcgminer\r"
			send "/etc/init.d/cgminer restart\r"
			send "exit\r"
			expect eof
		        puts "Change 192.168.1.$i Success!" 
		}
	}
}

