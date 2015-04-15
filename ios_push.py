#!/usr/bin/python
# -*- coding: utf-8 -*-

import daemon
import time
import urllib2
import json

import MySQLdb
import settings

import time
from apns import APNs, Frame, Payload

def get_notifications(db):
	cur = db.cursor()
	cur.execute("SELECT * FROM controller_pushnotifications WHERE device_type = 2 AND processed = 0 LIMIT 0,100")
	notis = cur.fetchall()
	cur.close()
	db.commit()
	return notis

def send_notifications(device_id, contents):
	try:
		data = json.loads(contents)
		msg = data['author'] + ': ' + data['contents']
		apns = APNs(use_sandbox=True, cert_file=settings.CERT_PEM, key_file=settings.KEY_PEM)
		payload = Payload(alert=msg, sound="default", badge=1)
		apns.gateway_server.send_notification(device_id, payload)
	except Exception as e:
		print str(e)
	

def finish_notifications(db, noti):
	cur = db.cursor()
	cur.execute("UPDATE controller_pushnotifications SET processed = 1 WHERE id = " + str(noti[0]))
	cur.close()
	db.commit()		

def do_main():
	db = MySQLdb.connect(host=settings.DB_HOST, user=settings.DB_USER, passwd=settings.DB_PASS,db=settings.DB_NAME)
	while True:
		notis = get_notifications(db)
		print notis
		for noti in notis:
			send_notifications(noti[5], noti[6])
			finish_notifications(db, noti)
		time.sleep(1)
	db.close()

with daemon.DaemonContext():
	do_main()
