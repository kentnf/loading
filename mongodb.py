#!/usr/bin/python3

import time

#connection = pymongo.MongoClient('127.0.0.1',27017)
#tdb = connection.alpha87
#post = tdb.test
#post.insert({'name':"libai", "age":"30", "skill":"Python"})
#print("done")
#ISOTIMEFORMAT='%Y-%m-%d %X'
#start_time = time.strftime( ISOTIMEFORMAT, time.localtime( time.time() ) )
#print(start_time)
import pymongo
import json
import datetime,time
import copy
import sys, os

def getTimestampFromDatetime(d=None):
	if d is None:
		d = datetime.datetime.now()
	return time.mktime(d.timetuple())

if __name__ == '__main__':	
	start = getTimestampFromDatetime()
	client = pymongo.MongoClient("localhost", 27017, maxPoolSize=50)
	db = client.testdb

	saveData = []
	for i in range(0, 100000):
		saveData.append({
			'count':i
		})

	db.test2.insert(saveData)
	end = getTimestampFromDatetime()
	print('time: {0}s'.format(end-start))
