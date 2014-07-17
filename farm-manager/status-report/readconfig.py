#!/usr/bin/env python
import os
import ConfigParser
def readconfig(cfgfile):
	config = ConfigParser.ConfigParser()
	config.read(cfgfile)
	cfg = dict(config._sections)
	for k in cfg:
		cfg[k] = dict(config._defaults, **cfg[k])
		cfg[k].pop('__name__', None)

	if cfg['General']['log_dir'][-1] != '/':
		cfg['General']['log_dir'] += '/'
	if cfg['HSplot']['img_dir'][-1] != '/':
		cfg['HSplot']['img_dir'] += '/'
	if cfg['TMplot']['img_dir'][-1] != '/':
		cfg['TMplot']['img_dir'] += '/'
	if not os.path.isdir(cfg['General']['log_dir']):
		os.makedirs(cfg['General']['log_dir'])
	if not os.path.isdir(cfg['HSplot']['img_dir']):
		os.makedirs(cfg['HSplot']['img_dir'])
	if not os.path.isdir(cfg['TMplot']['img_dir']):
		os.makedirs(cfg['TMplot']['img_dir'])

	cfg['miner_list'] = []
	cfg['port_list'] = []
	cfg['dev_list'] = []
	cfg['mod_num_list'] = []

	i = 0
	while 'Zone'+str(i+1) in cfg:
		i += 1
		zone = 'Zone' + str(i)
		miner_cfgs = list(filter(None, (x.strip() for x in cfg[zone]['miner_list'].splitlines())))
		cfg[zone]['miner_list'] = []
		cfg[zone]['port_list'] = []
		cfg[zone]['dev_list'] = []
		cfg[zone]['mod_num_list'] = []
		for miner_cfg in miner_cfgs:
			tmp = miner_cfg.split('/')
			port_cfgs = tmp[1].split(';')
			cfg[zone]['miner_list'].append(tmp[0])
			mn = 0
			port_list = []
			dev_list = []
			for port_cfg in port_cfgs:
				tmp1 = port_cfg[1:-1].split(':')
				port_list.append(tmp1[0])
				mod_list = tmp1[1].split(',')
				for m in mod_list:
					mn += int(m)
				dev_list.append(mod_list)
			cfg[zone]['dev_list'].append(dev_list)
			cfg[zone]['port_list'].append(port_list)
			cfg[zone]['mod_num_list'].append(str(mn))
		cfg['miner_list'] += cfg[zone]['miner_list']
		cfg['port_list'] += cfg[zone]['port_list']
		cfg['dev_list'] += cfg[zone]['dev_list']
		cfg['mod_num_list'] += cfg[zone]['mod_num_list']
	cfg['zone_num'] = i

	return cfg

