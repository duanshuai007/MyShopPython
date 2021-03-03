#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import sys 
import configparser

#读取配置文件模块,对应的配置文件config.ini
class config():
	rootdir = ''
	config = None
	filepath = ''

	def __init__(self, configfilename:str):
		if not os.path.exists(configfilename):
			print("config file not exists, configfilename={}".format(configfilename))
			sys.exit(1)
		self.filepath = configfilename
		self.config = configparser.ConfigParser()
		self.config.read(configfilename)
		pass

	def get_as_dict(self):
		try:
			d = dict(self.config._sections)
			for k in d:
				d[k] = dict(d[k])
			return d
		except Exception as e:
			print("get_as_dict error:{}".format(e))

	def get(self:object, string:str, substring:str)->str:
		try:
			ret = self.config[string][substring]
			return ret 
		except Exception as e:
			print("config get error:{}".format(e))
		return ''
	
	def set(self:object, string:str, substring:str, value:str)->bool:
		try:
			self.config.set(string, substring, value)
			with open(self.filepath, 'w') as f:
				self.config.write(f)
			return True
		except Exception as e:
			print("Config set error:{}".format(e))
			return False

if __name__ == "__main__":
	c = config("./config.ini")
	s = c.get_as_dict()
	#print(s)
	print(s["device_doorno"]["862167051501249"])
	print(s["device_doorno"]["862167051501082"])
	print(s["device_doorno"]["862167051501413"])
	import time
	while True:
		s = config("./config.ini").get_as_dict()
		print(s["table"]["862167051501413"])
		time.sleep(1)
