#!/usr/bin/env python
#-*- coding:utf-8 -*-

import MySQLdb
import time

#在windows下使用localhost会出现10061错误
DB_IP = '127.0.0.1'
DB_NAME = 'myshop'
DB_USER = 'root'
DB_PASSWD = '123'
TB_NAME = 'date0314'
#免费时长, 计时周期,周期单价,最大计时时间,
HISTORY_TB_NAME = ''
TABLENAME_HEAD = 'shop'
MAXNUMBER_IN_TABLE=10

gTableName = ''
gGroupID = 0

def createdb(name):
    db = MySQLdb.connect(DB_IP, DB_USER, DB_PASSWD, charset='utf8')
    cursor = db.cursor()
    db.autocommit(False)
    cursor.execute('set names utf8')
    db.commit()

    name = '%s' % name
    try:
        cursor.execute('show databases')
        rows = cursor.fetchall()
        for row in rows:
            row_name = '%s' % row
            ret = cmp(name, row_name)
            if ret == 0:
                #print "DataBase Already Exits"
                return True
        sql = 'create database %s' % name
        cursor.execute(sql)
        db.commit()
        return True
    except Exception as e:
        print e.args
        db.rollback()
        return False
    finally:
        cursor.close()
        db.close()

def connectdb(name):
    db = MySQLdb.connect(DB_IP, DB_USER, DB_PASSWD, name, charset='utf8')
    return db

#datestr = time.strftime('%Y%m%d', time.localtime(time.time()))

#参数strdate是日期格式“20190401”
def createtable(strdate):
    db = connectdb(DB_NAME)
    cursor = db.cursor()
    ret = ''
    try:
        name = '%s%s' % (TABLENAME_HEAD, strdate)
        cursor.execute('show tables')
        rows = cursor.fetchall()
        for row in rows:
            row_name = '%s' % row
            result = cmp(name, row_name)
            if result == 0:
                #print "DataBase Already Exits"
                return name

        sql = 'create table %s(\
                u32DeviceID int(1) unsigned primary key auto_increment,\
                c20Name char(20) default \'NULL\',\
                c20SName char(20) default \'NULL\',\
                InTime datetime default NULL,\
                OutTime datetime default NULL,\
                TotalNum int(1) unsigned default 0,\
                ShopNum int(1) unsigned default 0,\
                InPrice float(6,1) unsigned default 0.0,\
                OutPrice float(6,1) unsigned default 0.0,\
                GroupSellID int(1) unsigned default 0,\
                GroupMoney float(6,1) unsigned default 0.0)' % name 
        cursor.execute(sql)
        db.commit()

#sql = 'alter table %s add index IndexUpload(cInUpload(1),cOutUpload(1))' % name
#       cursor.execute(sql)
#       db.commit()
        ret = name
        print 'create tb success'
        return ret
    except Exception as e:
        print "create_table Except : %s" % e.args
        db.rollback()
    finally:
        cursor.close()
        db.close()

def get_version():
    database = connectdb(DB_NAME)
    cursor = database.cursor()
    try:
        cursor.execute('select version()')
        ret = cursor.fetchone()
        database.commit()
        return ret
    except:
        database.rollback()
    finally:
        cursor.close()
        database.close()
    
def getGroupIDLast(tbname):
    global gGroupID
    db = connectdb(DB_NAME)
    cursor = db.cursor()
    try:
        sql = 'select GroupSellID from %s' % tbname + \
              ' where GroupSellID in (select max(GroupSellID) from %s' % tbname + \
              ' order by GroupSellID)'
        #print sql
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            gGroupID = result[0]
    except Exception as e:
        print e.args
    finally:
        cursor.close()
        db.close()

#售出一件商品的情况
def sellOneItem(tbname, name, count, money):
    db = connectdb(DB_NAME)
    cursor = db.cursor()
    print 'table name:%s'%tbname
    try:
        datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        sql = 'insert into %s' % tbname + \
              '(c20Name, OutTime, ShopNum, OutPrice)' + \
              ' values(\'%s\', \'%s\', %d, %f)' % (name, datetime, count, money)
        #print 'sql:%s'%sql
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print e.args
        db.rollback()
    finally:
        cursor.close()
        db.close()
#几件商品打包售出的情况
def sellSomeItem(tbname, name_count_list, money):
    global gGroupID
    db = connectdb(DB_NAME)
    cursor = db.cursor()
    gGroupID = gGroupID + 1
    datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    #print 'gGroupID=%d' % gGroupID
    try:
        for item in name_count_list:
            item_name = item[0]
            item_count = item[1]
            sql = 'insert into %s' % tbname + \
                  '(c20Name, OutTime, ShopNum, GroupSellID, GroupMoney)' + \
                  ' values(\'%s\', \'%s\', %d, %d, %f)' % (item_name, datetime, item_count, gGroupID, money)
            cursor.execute(sql)
            db.commit()
    except Exception as e:
        print e.args
        db.rollback()
    finally:
        cursor.close()
        db.close()

def putInStorage(tbname, str_list):
    db = connectdb(DB_NAME)
    cursor = db.cursor()

    flag = str_list[0]
    name = str_list[1]
    number = str_list[2]
    money = str_list[3]
    datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  
    try:
        sql = 'insert into %s' % tbname + \
              '(c20Name, InTime, TotalNum, InPrice)' + \
              ' values(\'%s\', \'%s\', %d, %f)' % (name, datetime, number, money)
        #print sql
        cursor.execute(sql)
        db.commit()
    except Exception as e:
        print e.args
        db.rollback()
    finally:
        cursor.close()
        db.close()

def getItem(tbname):
    db = connectdb(DB_NAME)
    cursor = db.cursor()
    ret_list = []
    try:
        sql = 'select * from %s' % tbname
        cursor.execute(sql)
        while True:
            result = cursor.fetchone()
            if result:
                ret_list.append(result)
            else:
                break
    except Exception as e:
        print e.args
    finally:
        return ret_list
        cursor.close()
        db.close()

if __name__ == '__main__':
    ret = createdb(DB_NAME)
    if ret == True:
        #print 'create tb'
        datestr = time.strftime('%Y%m%d', time.localtime(time.time()))  
        gTableName = createtable(datestr)
        #print gTableName
        #sellOneItem(gTableName, "jiezhi", 20, 1500.5)
        #getGroupIDLast(gTableName)
        #print gGroupID
        #sList = [['jiezhi', 10],['xiangshui', 1],['batao', 1],['xiaodao', 3]]
        #sellSomeItem(gTableName, sList, 430)
        #sList = [['kaka', 4],['liefeng', 2],['fengbao', 1],['shandian', 4]]
        #sellSomeItem(gTableName, sList, 1090)
        #ret = getItem(gTableName)
        add_list = ['insert', '火焰风衣', 1, 1000]
        putInStorage(gTableName, add_list)

#ret = mysql_get_version()
#print 'version=%s' % ret
