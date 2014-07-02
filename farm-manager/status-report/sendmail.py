#!/usr/bin/env python
from __future__ import print_function
import smtplib
import uuid
import urllib2
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.image     import MIMEImage
import os
import sys
from django.template import loader, Context
from django.conf import settings

def post(mail,template_var):
	me=mail['user']+"<"+mail['from_address']+">"
	msg = MIMEMultipart('related')
	msg['Subject'] = mail['subject']
	msg['From'] = me
	msg['To'] = mail['to_list']
	to_list = mail['to_list'].split(';')
	msg_alternative = MIMEMultipart('alternative')
	msg.attach(msg_alternative)

	if 'tmimg' in mail:
		tmimg = dict(path=mail['tmimg_dir'] + mail['tmimg'], cid=str(uuid.uuid4()))

		with open(tmimg['path'], 'rb') as file:
			msg_tmimage = MIMEImage(file.read(), name=os.path.basename(tmimg['path']))
			msg.attach(msg_tmimage)
		template_var['tmimg_cid'] = tmimg['cid']
		msg_tmimage.add_header('Content-ID', '<{}>'.format(tmimg['cid']))
	if 'hsimg' in mail:
		hsimg = dict(path=mail['hsimg_dir'] + mail['hsimg'], cid=str(uuid.uuid4()))

		with open(hsimg['path'], 'rb') as file:
			msg_hsimage = MIMEImage(file.read(), name=os.path.basename(hsimg['path']))
			msg.attach(msg_hsimage)
		template_var['hsimg_cid'] = hsimg['cid']
		msg_hsimage.add_header('Content-ID', '<{}>'.format(hsimg['cid']))
	tmp = mail['template'].split('/')
	template_dir = '/'.join(tmp[:-1])
	settings.configure(TEMPLATE_DIRS = (template_dir if template_dir else './'))
	t = loader.get_template(tmp[-1])
	c = Context(template_var)
	mail['content'] = t.render(c)
	msg_html = MIMEText(mail['content'],'HTML')
	msg_alternative.attach(msg_html)
	try:
		s = smtplib.SMTP()
		s.connect(mail['smtp_server'])
		s.login(mail['user'],mail['password'])
		s.sendmail(me, to_list, msg.as_string())
		s.close()
		return True
	except Exception, e:
		print(str(e),end="")
		sys.stdout.flush()
		return False


def sendmail(time,data,cfg):

	mail = cfg['Email']

	mail['user'] = mail['from_address'].split('@')[0]
	mail['subject'] = "[Miner Status " + cfg['General']['server_code'] + "] Report " + time

	template_var={}

	print('Fetching balance data:')
	proxy_handler = urllib2.ProxyHandler({})
	opener = urllib2.build_opener(proxy_handler)
	urllib2.install_opener(opener)
	url_list = list(filter(None, (x.strip() for x in cfg['Pool']['balance_url'].splitlines())))
	template_var['balance_list']=[]

	b = 0
	err = 0
	for url in url_list:
		print(url+' ... ',end="")
		sys.stdout.flush()
		retry = 0
		fail = 1
		while retry < int(cfg['Pool']['retry']):
			try:
				s = urllib2.urlopen(url).read()
				balance = s.split('Final Balance')[1].split(' BTC')[0].split('>')[-1]
				b += float(balance)
				fail = 0
				break
			except Exception, e:
				print(str(e),end="")
				sys.stdout.flush()
				retry += 1
		if fail == 1:
			err = 1
			balance = 'Connection Failed'
		template_var['balance_list'].append({'addr' : url.split('/')[-1] , 'num':balance, 'url':url})
		print("Done.")
	if err == 1:
		template_var['sum_balance'] = 'N/A'
	else:
		template_var['sum_balance'] = str(b)

	print("Sending email to " + cfg['Email']['to_list'].replace(';',' & ') + ' ...',end="")
	sys.stdout.flush()
	template_var['server_code'] = cfg['General']['server_code']
	template_var['time'] = time
	alivenum = 0
	for miner in data:
		if miner[1] == "Alive":
			alivenum += 1
	template_var['active_ip_num'] = str(alivenum) + '/' + str(len(cfg['miner_list']))

	template_var['err_miner_list']=[]
	for miner in data:
		if miner[7] != '0':
			error = int(miner[7])
			error_r = []
			if error|8 == error:
				error_r.append('Unable to connect')
			if error|4 == error:
				error_r.append('Alive module number too low')
			if error|2 == error:
				error_r.append('Temperature 255')
			if error|1 == error:
				error_r.append('Too hot')
			template_var['err_miner_list'].append({'ip':miner[0], 'error':'. '.join(error_r)+'.'})

	sum_mod_num = 0
	for miner in data:
		for dev_stat in miner[4]:
			sum_mod_num += int(dev_stat[3])
	sum_mod_num0 = 0
	for mod_num in cfg['mod_num_list']:
		sum_mod_num0 += int(mod_num)
	template_var['alive_mod_num'] = str(sum_mod_num) + '/' + str(sum_mod_num0)
	if 'tmimg' in mail:
		template_var['tmimg'] = True
	if 'hsimg' in mail:
		template_var['hsimg'] = True

	if post(mail,template_var):
		print(" Successed.")
	else:
		print(" Failed.")

