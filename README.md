##shop script
带有桌面gui的脚本程序
使用mysql进行数据管理
可以查询输入输出的数据，每日销售金额统计，每月销售金额统计，
统计销售金额最高的产品。
具有用户登录功能

## 在win7 下安装mysql

下载mysql：https://dev.mysql.com/downloads/file/?id=463242

解压到D目录

新建文件my.ini

```
[mysql]
# 设置mysql客户端默认字符集
default-character-set=utf8
 
[mysqld]
# 设置3306端口
port = 3306
# 设置mysql的安装目录
basedir=D:\mysql-5.7.13-winx64
# 设置mysql数据库的数据的存放目录
datadir=C:\wamp-all\sqldata
# 允许最大连接数
max_connections=20
# 服务端使用的字符集默认为8比特编码的latin1字符集
character-set-server=utf8
# 创建新表时将使用的默认存储引擎
default-storage-engine=INNODB
```

将解压目录中的bin目录加入到系统环境变量中，然后执行`mysql --install`

然后执行`net start mysql`启动mysql服务。

如果提示出现`“错误2：系统找不到指定文件”` 那么就在cmd下输入regedit，然后打开`KEY_LOCAL_MACHINE->SYSTEM->CurrentControlSet->services->MySQL->ImagePath`修改为我们mysql解压的位置，注意是bin目录中mysqld.EXE

## 创建mysql用户

1.创建用户

`create user 'shop'@'localhost' identified by '123';`

2.设置权限

`grant all privileges on *.* to shop@'localhost';`

3.创建数据库

`create database warehouse;`



## On Ubuntu 20.04 install python mysql

apt-get install mysql-server
apt-get install libmysqlclient-dev
pip3 install mysqlclient
