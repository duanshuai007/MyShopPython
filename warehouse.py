#!/usr/bin/env python
#-*- coding:utf-8 -*-

import MySQLdb
import time
import os

#import operator

from logger import LoggingProducer, LoggingConsumer
from config import config

class warehouse():

	#在windows下使用localhost会出现10061错误
	#DATABASE_IPADDRESS = '127.0.0.1'
	TABLE_IN_HEAD = 'in'
	TABLE_OUT_HEAD = 'out'

	def __init__(self):
		try:
			self.logger = LoggingProducer().get_default_logger()
			rootdir = os.path.abspath(os.path.dirname(__file__))
			cfgpath = "{}/{}".format(rootdir, "config.ini")
			self.config = config(cfgpath)
			self.DATABASE_IPADDRESS = self.config.get("database", "host")
			self.DATABASE_NAME = self.config.get("database", "databasename")
			self.DATABASE_USERNAME = self.config.get("database", "username")
			self.DATABASE_PASSWORD = self.config.get("database", "password")
		except Exception as e:
			print("warehouse init failed:{}".format(e))

	'''创建数据库'''
	def create_db(self):
		self.db = MySQLdb.connect(self.DATABASE_IPADDRESS, self.DATABASE_USERNAME, self.DATABASE_PASSWORD, charset='utf8')
		self.cursor = self.db.cursor()
		self.db.autocommit(False)
		self.cursor.execute('set names utf8')
		self.db.commit()
		try:
			self.cursor.execute('show databases')
			rows = self.cursor.fetchall()
			for row in rows:
				if self.DATABASE_NAME == row[0]:
					#self.logger.info("DataBase Already Exits")
					return True
			sql = 'create database {}'.format(self.DATABASE_NAME)
			self.cursor.execute(sql)
			self.db.commit()
			#self.logger.info("create db ok")
			return True
		except Exception as e:
			self.logger.error("db create error:{}".format(e))
			self.db.rollback()
			return False
		finally:
			self.cursor.close()
			self.db.close()

	def create_tb(self):
		self.db = MySQLdb.connect(self.DATABASE_IPADDRESS, self.DATABASE_USERNAME, self.DATABASE_PASSWORD, self.DATABASE_NAME, charset='utf8')
		self.cursor = self.db.cursor()
		will_create_tb = ['warehouse', "{}{}".format(self.TABLE_IN_HEAD, time.strftime('%Y%m')), "{}{}".format(self.TABLE_OUT_HEAD, time.strftime('%Y%m'))]
		need_create_tb = []
		try:
			#name = '{}{}'.format(self.TABLENAME_HEAD, name)
			self.cursor.execute('show tables')
			rows = self.cursor.fetchall()
			
			for tbname in will_create_tb:
				flag = False
				for row in rows:
					if tbname == row[0]:
						#self.logger.info("Table[{}] Already Exits".format(tbname))
						flag = True
						break
				if flag is False:
					need_create_tb.append(tbname)

			if len(need_create_tb) == 0:
				return True
			else:
				for tbname in need_create_tb:
					if tbname == 'warehouse':
						sql = "create table {}(\
							   u32ProductID int(1) unsigned primary key auto_increment,\
							   c64ProductName varchar(64) character set utf8 collate utf8_general_ci default \'null\',\
							   c64PinyinName varchar(64) character set utf8 collate utf8_general_ci default \'null\',\
							   u32Inventory int(1) unsigned default 0,\
							   u32Sold int(1) unsigned default 0,\
							   fCost float(10,1) unsigned default 0.0,\
							   fIncome float(10,1) unsigned default 0.0)".format(tbname)
						pass
					elif tbname.startswith(self.TABLE_OUT_HEAD):
						sql = "create table {}(\
							   u32Id int(1) unsigned primary key auto_increment,\
							   time datetime default NULL,\
							   u32ProductID int(1) unsigned default 0,\
							   u32Sold int(1) unsigned default 0,\
							   fIncome float(10,1) unsigned default 0.0)".format(tbname)
						pass
					elif tbname.startswith(self.TABLE_IN_HEAD):
						sql = "create table {}(\
							   u32Id int(1) unsigned primary key auto_increment,\
							   time datetime default NULL,\
							   u32ProductID int(1) unsigned default 0,\
							   u32Inventory int(1) unsigned default 0,\
							   fCost float(10,1) unsigned default 0.0)".format(tbname)
						pass
					else:
						continue
					self.cursor.execute(sql)
					self.db.commit()
			'''
			sql = "create table {}(\
					u32DeviceID int(1) unsigned primary key auto_increment,\
					c20Name varchar(20) character set utf8 collate utf8_general_ci default \'NULL\',\
					c20SName varchar(20) character set utf8 collate utf8_general_ci default \'NULL\',\
					InTime datetime default NULL,\
					OutTime datetime default NULL,\
					TotalNum int(1) unsigned default 0,\
					ShopNum int(1) unsigned default 0,\
					InPrice float(10,1) unsigned default 0.0,\
					OutPrice float(10,1) unsigned default 0.0,\
					GroupSellID int(1) unsigned default 0,\
					GroupMoney float(10,1) unsigned default 0.0)".format(name)
			self.cursor.execute(sql)
			self.db.commit()
			'''
			#sql = 'alter table %s add index IndexUpload(cInUpload(1),cOutUpload(1))' % name
			#cursor.execute(sql)
			#db.commit()
			#self.logger.info('create tb success')
			return True
		except Exception as e:
			self.logger.error("create table error:{}".format(e))
			self.db.rollback()
			return False
		finally:
			self.cursor.close()
			self.db.close()

	def get_version(self):
		self.db = MySQLdb.connect(self.DATABASE_IPADDRESS, self.DATABASE_USERNAME, self.DATABASE_PASSWORD, self.DATABASE_NAME, charset='utf8')
		self.cursor = self.db.cursor()
		try:
			self.cursor.execute('select version()')
			ret = self.cursor.fetchone()
			self.db.commit()
			return ret
		except Exception as e:
			self.logger.error("get_version error:{}".format(e))
			self.db.rollback()
		finally:
			self.cursor.close()
			self.db.close()
	'''	
	def getGroupIDLast(self, tbname):
		self.db = MySQLdb.connect(self.DATABASE_IPADDRESS, self.DATABASE_USERNAME, self.DATABASE_PASSWORD, self.DATABASE_NAME, charset='utf8')
		self.cursor = self.db.cursor()
		try:
			sql = 'select GroupSellID from %s' % tbname + \
				  ' where GroupSellID in (select max(GroupSellID) from %s' % tbname + \
				  ' order by GroupSellID)'
			self.cursor.execute(sql)
			result = self.cursor.fetchone()
			if result:
				self.gGroupID = result[0]
		except Exception as e:
			self.logger.error("getGroupIDLast error:{}".format(e))
		finally:
			self.cursor.close()
			self.db.close()

	#售出一种商品的情况
	def sellOneItem(self, tbname, name, count, money):
		self.db = MySQLdb.connect(self.DATABASE_IPADDRESS, self.DATABASE_USERNAME, self.DATABASE_PASSWORD, self.DATABASE_NAME, charset='utf8')
		self.cursor = self.db.cursor()
		self.logger.info('table name:{}'.format(tbname))
		try:
			#datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
			datetime = time.strftime('%Y-%m-%d %H:%M:%S')
			sql = 'insert into %s' % tbname + \
				  '(c20Name, OutTime, ShopNum, OutPrice)' + \
				  ' values(\'%s\', \'%s\', %d, %f)' % (name, datetime, count, money)
			self.cursor.execute(sql)
			self.db.commit()
		except Exception as e:
			self.logger.error("sellOneItem error:{}".format(e))
			self.db.rollback()
		finally:
			self.cursor.close()
			self.db.close()

	#几件商品打包售出的情况
	def sellSomeItem(self, tbname, name_count_list, money):
		self.db = MySQLdb.connect(self.DATABASE_IPADDRESS, self.DATABASE_USERNAME, self.DATABASE_PASSWORD, self.DATABASE_NAME, charset='utf8')
		self.cursor = self.db.cursor()
		self.gGroupID = self.gGroupID + 1
		#datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
		datetime = time.strftime('%Y-%m-%d %H:%M:%S')
		try:
			for item in name_count_list:
				item_name = item[0]
				item_count = item[1]
				sql = 'insert into %s' % tbname + \
					  '(c20Name, OutTime, ShopNum, GroupSellID, GroupMoney)' + \
					  ' values(\'%s\', \'%s\', %d, %d, %f)' % (item_name, datetime, item_count, self.gGroupID, money)
				self.cursor.execute(sql)
				self.db.commit()
		except Exception as e:
			self.logger.error("sellSomeItem error:{}".format(e))
			self.db.rollback()
		finally:
			self.cursor.close()
			self.db.close()
	'''
	
	def __update_warehouse(self, productid, flag:int, number:int, money:float, productname:str, pinyinname:str):
		try:
			if productid is None:
				if flag == 0:
					#入库
					sql = 'insert into warehouse(c64ProductName, c64PinyinName, u32Inventory, fCost) values(\'{}\', \'{}\', {}, {})'.format(
							productname, pinyinname, number, money)
				else:
					sql = 'insert into warehouse(c64ProductName, c64PinyinName, u32Sold, fIncome) values(\'{}\', \'{}\', {}, {})'.format(
							productname, pinyinname, number, money)
				self.cursor.execute(sql)
				self.db.commit()

				sql = 'select u32ProductID from warehouse where c64PinyinName=\'{}\''.format(pinyinname)
				self.cursor.execute(sql)
				result = self.cursor.fetchone()
				print(result)
				return result[0]
			else:
				sql = "select * from warehouse where u32ProductID={}".format(productid)
				find = False
				self.cursor.execute(sql)
				while True:
					result = self.cursor.fetchone()
					if result is not None:
#					print("result0={} type={}".format(result[0], type(result[0])))
						if result[0] == productid:
							find = True
							if flag == 0:
								#入库
								u32Inventory = result[3]
#							print("u32Inventory={} type={}".format(u32Inventory, type(u32Inventory)))
								fCost = result[5]
#							print("fCost={} type={}".format(fCost, type(fCost)))
								u32Inventory = u32Inventory + number
								fCost = fCost + money
								sql = "update warehouse set u32Inventory={},fCost={} where u32ProductID={}".format(u32Inventory, fCost, productid)
							else:
								#售出
								u32Sold = result[4]
								fIncome = result[6]
								u32Sold = u32Sold + number
								fIncome = fIncome + money
								sql = "update warehouse set u32Sold={},fIncome={} where u32ProductID={}".format(u32Sold, fIncome, productid)
							self.cursor.execute(sql)
							self.db.commit()
					else:
						break
				return None
		except Exception as e:
			self.logger.error("__update_warehouse error:{}".format(e))
			self.db.rollback()

	'''
	name_count_list = [[ 商品ID, 商品名, 商品拼音名, 入库出库标志位, 数量, 金额 ], ]
	'''
	def update(self, record_list:list):
		self.create_tb()
		self.db = MySQLdb.connect(self.DATABASE_IPADDRESS, self.DATABASE_USERNAME, self.DATABASE_PASSWORD, self.DATABASE_NAME, charset='utf8')
		self.cursor = self.db.cursor()
		intb = "{}{}".format(self.TABLE_IN_HEAD, time.strftime('%Y%m'))
		outtb = "{}{}".format(self.TABLE_OUT_HEAD, time.strftime('%Y%m'))
		try:
			for record in record_list:
				productid = record[0]
				productname = record[1]
				pinyinname = record[2]
				flag = record[3]
				number = record[4]
				money = record[5]

				proid = self.__update_warehouse(productid, flag, number, money, productname, pinyinname)
				if proid:
					productid = proid

				if flag == 0:
					#入库标志
					sql = 'insert into {}(time, u32ProductID, u32Inventory, fCost) values(\'{}\', {}, {}, {})'.format(
							intb, time.strftime('%Y-%m-%d %H:%M:%S'), productid, number, money)
					self.cursor.execute(sql)
					self.db.commit()
				else:
					#售出标志
					sql = 'insert into {}(time, u32ProductID, u32Sold, fIncome) values(\'{}\', {}, {}, {})'.format(
							outtb, time.strftime('%Y-%m-%d %H:%M:%S'), productid, number, money)
					self.cursor.execute(sql)
					self.db.commit()

				'''
				sql = 'insert into %s' % tbname + \
					  '(c20Name, OutTime, ShopNum, OutPrice)' + \
					  ' values(\'%s\', \'%s\', %d, %f)' % (item[0], datetime, item[1], money)
				'''
		except Exception as e:
			self.logger.error("update error:{}".format(e))
			self.db.rollback()
		finally:
			self.cursor.close()
			self.db.close()
	'''
	def putInStorage(self, tbname, str_list):
		self.db = MySQLdb.connect(self.DATABASE_IPADDRESS, self.DATABASE_USERNAME, self.DATABASE_PASSWORD, self.DATABASE_NAME, charset='utf8')
		self.cursor = self.db.cursor()

		name = str_list[0]
		name_pinyin = str_list[1]
		number = str_list[2]
		money = str_list[3]
		#datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  
		datetime = time.strftime('%Y-%m-%d %H:%M:%S')
		try:
			sql = 'insert into %s' % tbname + \
				  '(c20Name, c20SName, InTime, TotalNum, InPrice)' + \
				  ' values(\'%s\', \'%s\', \'%s\', %d, %f)' % (name, name_pinyin, datetime, number, money)
			self.logger.info(sql)
			self.cursor.execute(sql)
			self.db.commit()
		except Exception as e:
			self.logger.error("putInStorage error:{}".format(e))
			self.db.rollback()
		finally:
			self.cursor.close()
			self.db.close()
	'''

	def getall(self):
		self.db = MySQLdb.connect(self.DATABASE_IPADDRESS, self.DATABASE_USERNAME, self.DATABASE_PASSWORD, self.DATABASE_NAME, charset='utf8')
		self.cursor = self.db.cursor()
		ret_list = []
		try:
			sql = 'select * from warehouse'
			self.cursor.execute(sql)
			while True:
				result = self.cursor.fetchone()
				if result:
					ret_list.append(result)
				else:
					break
		except Exception as e:
			self.logger.error("getall error:{}".format(e))
		finally:
			self.cursor.close()
			self.db.close()
			return ret_list

if __name__ == '__main__':
	print('create db')
	LoggingConsumer()
	r = warehouse()
	ret = r.create_db()
	ret = r.create_tb()
	r.get_version()

	s = [[1, "斧子", "fu-zi", 0, 3, 100],]
	r.update(s)

	ret = r.getall()
	print(ret)

