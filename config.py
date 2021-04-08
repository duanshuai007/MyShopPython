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
		self.config.read(configfilename, encoding="utf-8")
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
			with open(self.filepath, 'w', encoding="utf-8") as f:
				self.config.write(f)
			return True
		except Exception as e:
			print("Config set error:{}".format(e))
			return False

if __name__ == "__main__":
	rootdir = os.path.abspath(os.path.dirname(__file__))
	p = "{}/{}".format(rootdir, "config.ini")
	c = config(p)
	s = c.get_as_dict()
	print(s)

	r = c.get("database", "host")
	print(r)
	c.set("database", "host", "192.168.200.130")
