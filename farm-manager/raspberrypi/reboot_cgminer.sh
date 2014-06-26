#!/usr/bin/expect
log_user 0
spawn telnet 192.168.1.$argv
send "/etc/init.d/cgminer restart\r"
send "exit\r"
expect eof
puts "reboot 192.168.1.$argv cgminer ok"
