#!/usr/bin/env python

import json
import urllib
import urllib2
import hashlib
import hmac
import time

def getjs(poolcfg,url):
	i = 0
	while i < int(poolcfg['retry']):
		try:
			nonce = '{:.0f}'.format(time.time()*1000)
			signature = hmac.new(poolcfg['api_secret_key'], msg = nonce + poolcfg['username'] + poolcfg['api_key'], digestmod=hashlib.sha256).hexdigest().upper()
			post_content = { 'key': poolcfg['api_key'], 'signature': signature, 'nonce': nonce}
			param = urllib.urlencode(post_content)
			request = urllib2.Request(url, param, {'User-agent': 'bot-cex.io-' + poolcfg['username']})
			js = urllib2.urlopen(request).read()
			return json.loads(js)
		except Exception, e:
			print(str(e))
			time.sleep(1)
			i += 1
	return 0


def poolrate(cfg):
	url1 = 'https://cex.io/api/ghash.io/hashrate'
	url2 = 'https://cex.io/api/ghash.io/workers'

	proxy_handler = urllib2.ProxyHandler({})
	opener = urllib2.build_opener(proxy_handler)
	urllib2.install_opener(opener)

	dict1 = getjs(cfg['Pool'],url1)
	if dict1 == 0:
		hs1 = '0'
	else:
		hs1 = str(dict1['last1h'])
	time.sleep(1)

	dict2 = getjs(cfg['Pool'],url2)
	if dict2 == 0:
		hs2 = '0'
	else:
		try:
			hs2 = str(dict2[cfg['Pool']['username']+'.'+cfg['Pool']['workername']]['last1h'])
		except KeyError:
			hs2 = '0'
	return (hs1,hs2)

