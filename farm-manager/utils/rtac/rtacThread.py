#!/usr/bin/env python2

import telnetlib
import time

import paramiko


def sshThread(hostQueue, lock, commands, passwd, retry):

    while True:
        try:
            (hostIP, hostID) = hostQueue.get(False)
        except:
            break
        for i in range(0, retry):
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            errorFlag = False
            for k in range(0, retry):
                try:
                    ssh.connect(hostIP, 22, 'root', passwd)
                    break
                except:
                    ssh.close()
                    if k < retry - 1:
                        lock.acquire()
                        print('\033[1m\033[33mCannot connect to ' +
                              hostIP + '. Try Again.\033[0m')
                        lock.release()
                    else:
                        lock.acquire()
                        print('\033[31mCannot connect to ' + hostIP +
                              '. Skip.\033[0m')
                        lock.release()
                        errorFlag = True
            if errorFlag:
                break
            try:
                for c in commands:
                    if c[0:5] == 'sleep':
                        time.sleep(int(c[6:]))
                    else:
                        stdin, stdout, stderr = ssh.exec_command(c)
            except:
                ssh.close()
                lock.acquire()
                print("\033[31mConnection to " + hostIP +
                      " lost. Extend time-out and try again.\033[0m")
                lock.release()
                continue

            ssh.close()

            lock.acquire()
            print("Update complete @" + hostIP + ".")
            lock.release()
            break


def telnetThread(hostQueue, lock, commands, flag, retry):

    while True:
        try:
            (hostIP, hostID) = hostQueue.get(False)
        except:
            break
        for i in range(0, retry):
            tn = telnetlib.Telnet()

            errorFlag = False
            for k in range(0, retry):
                # try connecting for some times
                try:
                    tn.open(hostIP, 23)
                    break
                except:
                    tn.close()
                    if k < retry - 1:
                        lock.acquire()
                        print('\033[1m\033[33mCannot connect to ' +
                              hostIP + '. Try Again.\033[0m')
                        lock.release()
                    else:
                        lock.acquire()
                        print('\033[31mCannot connect to ' + hostIP +
                              '. Skip.\033[0m')
                        lock.release()
                        errorFlag = True
            if errorFlag:
                break

            try:
                tn.read_until(flag)
                for command in commands:
                    if command[0:5] == 'sleep':
                        time.sleep(int(command[6:]))
                        continue
                    if isinstance(command, basestring):
                        tn.write(command + '\n')
                        tn.read_until(flag)
                    else:
                        tn.write(command[0] + '\n')
                        tn.read_until(command[1])
                tn.write('exit\n')
                tn.read_all()
            except:
                tn.close()
                lock.acquire()
                print("\033[31mConnection to " + hostIP +
                      " lost. Extend time-out and try again.\033[0m")
                lock.release()
                continue

            tn.close()

            lock.acquire()
            print("Update complete @" + hostIP + ".")
            lock.release()
            break
