#!/usr/bin/env python
#-*- coding:utf-8 -*-

import MySQLdb
import time
import operator


from logger import LoggingProducer, LoggingConsumer


class db():

	#在windows下使用localhost会出现10061错误
	DB_IP = '127.0.0.1'
	DB_NAME = 'myshop'
	DB_USER = 'shop'
	DB_PASSWD = '123'
	
	TABLENAME_HEAD = 'shop'

	gGroupID = 0

	def create(self, name):
		self.DB_NAME = name
		self.logger = LoggingProducer().get_default_logger()
		self.db = MySQLdb.connect(self.DB_IP, self.DB_USER, self.DB_PASSWD, charset='utf8')
		self.cursor = self.db.cursor()
		self.db.autocommit(False)
		self.cursor.execute('set names utf8')
		self.db.commit()
		try:
			self.cursor.execute('show databases')
			rows = self.cursor.fetchall()
			for row in rows:
				#row_name = '%s' % row
				row_name = "{}".format(row[0])
				#ret = operator.eq(name, row_name)
				#if ret == 0:
				if name == row_name:
					self.logger.info("DataBase Already Exits")
					return True
			sql = 'create database {}'.format(name)
			self.cursor.execute(sql)
			self.db.commit()
			return True
		except Exception as e:
			self.logger.error("db create error:{}".format(e))
			self.db.rollback()
			return False
		finally:
			self.cursor.close()
			self.db.close()

	def connect(self, name):
		self.db = MySQLdb.connect(self.DB_IP, self.DB_USER, self.DB_PASSWD, name, charset='utf8')
		return self.db

	#参数strdate是日期格式“20190401”
	def createtable(self, strdate):
		self.db = self.connect(self.DB_NAME)
		self.cursor = self.db.cursor()
		try:
			name = '{}{}'.format(self.TABLENAME_HEAD, strdate)
			self.cursor.execute('show tables')
			rows = self.cursor.fetchall()
			for row in rows:
				#row_name = '%s' % row
				row_name = "{}".format(row[0])
				#result = operator.eq(name, row_name)
				#if result == 0:
				if name == row_name:
					self.logger.info("DataBase Already Exits")
					return name

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

			#sql = 'alter table %s add index IndexUpload(cInUpload(1),cOutUpload(1))' % name
			#cursor.execute(sql)
			#db.commit()
			self.logger.info('create tb success')
			return name
		except Exception as e:
			self.logger.error("createtable error:{}".format(e))
			self.db.rollback()
			return None
		finally:
			self.cursor.close()
			self.db.close()

	def get_version(self):
		self.db = self.connect(self.DB_NAME)
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
			
	def getGroupIDLast(self, tbname):
		self.db = self.connect(self.DB_NAME)
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

	#售出一件商品的情况
	def sellOneItem(self, tbname, name, count, money):
		self.db = self.connect(self.DB_NAME)
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
		self.db = self.connect(self.DB_NAME)
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

	def putInStorage(self, tbname, str_list):
		self.db = self.connect(self.DB_NAME)
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

	def getItem(self, tbname):
		self.db = self.connect(self.DB_NAME)
		self.cursor = self.db.cursor()
		ret_list = []
		try:
			sql = 'select * from {}'.format(tbname)
			self.cursor.execute(sql)
			while True:
				result = self.cursor.fetchone()
				if result:
					ret_list.append(result)
				else:
					break
		except Exception as e:
			self.logger.error("getItem error:{}".format(e))
		finally:
			self.cursor.close()
			self.db.close()
			return ret_list

if __name__ == '__main__':
	print('create db')
	LoggingConsumer()
	r = db()
	ret = r.create("ppp")
	
	if ret == True:
		datestr = time.strftime('%Y%m%d')
		gTableName = r.createtable(datestr)
		print(gTableName)
		#r.sellOneItem(gTableName, "jiezhi", 20, 1500.5)
		#r.getGroupIDLast(gTableName)
		#print gGroupID
#sList = [['jiezhi', 10],['xiangshui', 1],['batao', 1],['xiaodao', 3]]
#sellSomeItem(gTableName, sList, 430)
#sList = [['kaka', 4],['liefeng', 2],['fengbao', 1],['shandian', 4]]
#sellSomeItem(gTableName, sList, 1090)
#ret = getItem(gTableName)
		add_list = ['火焰风衣', "huoyanfengyi", 1, 1000]
		r.putInStorage(gTableName, add_list)
