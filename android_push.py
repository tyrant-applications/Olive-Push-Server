#!/usr/bin/python
# -*- coding: utf-8 -*-

import daemon
import time
import urllib2
import json

import MySQLdb


def get_notifications(db):
	cur = db.cursor()
	cur.execute("SELECT * FROM controller_pushnotifications WHERE device_type = 1 AND processed = 0 LIMIT 0,100")
	notis = cur.fetchall()
	cur.close()
	db.commit()
	return notis

def send_notifications(reg_id, contents):
	url = "https://android.googleapis.com/gcm/send"
	apiKey = "AIzaSyDktZ4hsSv2SbwHPUhy22CJh2jcn81qdgw"
	myKey = "key=" + apiKey

	# make header
	headers = {'Content-Type': 'application/json', 'Authorization': myKey}

	# make json data
	data = {}
	data['registration_ids'] = (reg_id,)
	data['data'] = json.loads(contents)
	json_dump = json.dumps(data)
	# print json.dumps(data, indent=4)

	req = urllib2.Request(url, json_dump, headers)
	result = urllib2.urlopen(req).read()
	print json.dumps(result)

def finish_notifications(db, noti):
	cur = db.cursor()
	cur.execute("UPDATE controller_pushnotifications SET processed = 1 WHERE id = " + str(noti[0]))
	cur.close()
	db.commit()		

def do_main():
	db = MySQLdb.connect(host="localhost", user="root", passwd="",db="tyrant")
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