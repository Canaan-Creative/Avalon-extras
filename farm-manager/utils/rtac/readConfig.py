#!/usr/bin/env python

import ConfigParser


def readConfig(cfgfile):

    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    cfg = dict(config._sections)
    for k in cfg:
        cfg[k] = dict(config._defaults, **cfg[k])
        cfg[k].pop('__name__', None)

    return cfg
