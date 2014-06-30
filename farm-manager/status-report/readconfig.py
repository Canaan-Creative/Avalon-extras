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
	cfg['mod_num_list'] = []
	i = 0
	while 'Zone'+str(i+1) in cfg:
		i += 1
		zone = 'Zone' + str(i)
		tmp = list(filter(None, (x.strip() for x in cfg[zone]['miner_list'].splitlines())))
		cfg[zone]['miner_list'] = []
		cfg[zone]['mod_num_list'] = []
		for l in tmp:
			ll = l.split(';')
			cfg[zone]['miner_list'].append(ll[0])
			cfg[zone]['mod_num_list'].append(ll[1])
		cfg['miner_list'] += cfg[zone]['miner_list']
		cfg['mod_num_list'] += cfg[zone]['mod_num_list']
	cfg['zone_num'] = i
	return cfg

