#!/usr/bin/env python2

import json
import urllib
import urllib2
import hashlib
import hmac
import time
import sys


def getjs(poolcfg, url):
    i = 0
    while i < int(poolcfg['retry']):
        try:
            nonce = '{:.0f}'.format(time.time()*1000)
            signature = hmac.new(poolcfg['api_secret_key'], msg=nonce +
                                 poolcfg['username'] + poolcfg['api_key'],
                                 digestmod=hashlib.sha256).hexdigest().upper()
            post_content = {'key': poolcfg['api_key'],
                            'signature': signature,
                            'nonce': nonce}
            param = urllib.urlencode(post_content)
            request = urllib2.Request(url, param,
                                      {'User-agent': 'bot-cex.io-' +
                                       poolcfg['username']})
            js = urllib2.urlopen(request).read()
            return json.loads(js)
        except Exception, e:
            print str(e),
            sys.stdout.flush()
            time.sleep(1)
            i += 1
    return 0


def ghash(pool_cfg):
    url2 = 'https://cex.io/api/ghash.io/workers'

    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)
    urllib2.install_opener(opener)

    dict2 = getjs(pool_cfg, url2)
    if dict2 == 0:
        hs2 = '0'
    else:
        try:
            hs2 = str(dict2[pool_cfg['username'] + '.' +
                            pool_cfg['workername']]['last1h'])
        except KeyError:
            hs2 = '0'
    return hs2


def ozco(pool_cfg):
    url = 'http://ozco.in/api.php?api_key=' + pool_cfg['api_key']
    js = urllib2.urlopen(url).read()
    dict0 = json.loads(js)
    hs2 = ''.join(dict0['worker'][pool_cfg['username'] + '.' +
                                  pool_cfg['workername']]['current_speed']
                  .split(','))
    return hs2


def poolrate(cfg):
    rate = []
    for pool_cfg in cfg['pool_list']:
        if pool_cfg['name'] == 'ghash':
            rate.append(ghash(pool_cfg))
        elif pool_cfg['name'] == 'ozco':
            rate.append(ozco(pool_cfg))
        else:
            rate.append('0')
    return rate
