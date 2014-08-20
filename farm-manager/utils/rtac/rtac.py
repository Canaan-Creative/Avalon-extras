#!/usr/bin/env python2

import threading
import argparse
import Queue

from readConfig import readConfig
from rtacThread import sshThread, telnetThread

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Them on All Controllers.')
    parser.add_argument('-s', '--ssh', help='Use ssh instead of telnet.',
                        action='store_true')
    parser.add_argument('-m', '--commands', type=str,
                        help='Command-to-run list file.', default='./commands')
    parser.add_argument('-o', '--hosts', type=str,
                        help='Host-to-login list file.', default='./hosts')
    parser.add_argument('-c', '--configuration', type=str,
                        help='Configuration file.', default='./rtac.conf')
    args = parser.parse_args()

    cfg = readConfig(args.configuration)
    threadnum = int(cfg['General']['threadnumber'])
    retry = int(cfg['General']['retry'])

    commands = filter(None, [line.rstrip() for line in open(args.commands)])
    for i in range(0, len(commands)):
        if '[*flag*]' in commands[i]:
            commands[i] = commands[i].split('[*flag*]')

    hosts = filter(None, [line.rstrip() for line in open(args.hosts)])

    lock = threading.Lock()
    hostQueue = Queue.Queue()
    for i in range(0, len(hosts)):
        hostQueue.put((hosts[i], i))

    threads = []
    if args.ssh:
        passwd = cfg['SSH']['passwd']
        for i in range(0, threadnum):
            threads.append(threading.Thread
                           (target=sshThread,
                            args=(hostQueue, lock, commands, passwd, retry)))
    else:
        flag = cfg['Telnet']['flag']
        for i in range(0, threadnum):
            threads.append(threading.Thread
                           (target=telnetThread,
                            args=(hostQueue, lock, commands, flag, retry)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()
