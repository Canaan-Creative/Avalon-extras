#!/usr/bin/env python
import ConfigParser
def readconfig(cfgfile):
	config = ConfigParser.ConfigParser()
	config.read(cfgfile)
	cfgdict = dict(config._sections)
	for k in cfgdict:
		cfgdict[k] = dict(config._defaults, **cfgdict[k])
		cfgdict[k].pop('__name__', None)
	return cfgdict
if __name__ == '__main__':
	print readconfig('./statreport.conf')