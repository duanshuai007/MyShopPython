#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import threading 
import queue
import time
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from logger import LoggingProducer
from config import config

class tencent_email():

	# 发件人邮箱账号
	sender_email= ''  
	sender_name= ''
	# user登录邮箱的用户名，password登录邮箱的密码（授权码，即客户端密码，非网页版登录密码），但用腾讯邮箱的登录密码也能登录成功  
	sender_password = ''
	q = None

	confile_filename = "config.ini"
	confile_path = ""
	email_server = None
	common_message = None

	def __init__(self, subject):
		self.q = queue.Queue(32)
		self.logger = LoggingProducer().get_logger()
		# SMTP服务器，腾讯企业邮箱端口是465，腾讯邮箱支持SSL(不强制)， 不支持TLS
		# qq邮箱smtp服务器地址:smtp.qq.com,端口号：456
		# 163邮箱smtp服务器地址：smtp.163.com，端口号：25
		# 登录服务器，括号中对应的是发件人邮箱账号、邮箱密码
		self.email_subject = subject
		time.sleep(0.1)
		self.confile_path = "{}/{}".format(os.path.abspath(os.path.dirname(__file__)), self.confile_filename)
		t = threading.Thread(target = self.email_task, args = [])
		t.setDaemon(False)
		t.start()
		pass
	
	def email_task(self):
		while True:
			try:
				if not self.q.empty():
					self.email_server = smtplib.SMTP_SSL("smtp.exmail.qq.com", 465)  
					self.email_server.login(self.sender_email, self.sender_password)
					while True:
						msgdict = self.q.get()
						self.q.task_done()
						message = "{}:{}".format(msgdict["sn"], msgdict["message"])
						sendmsg = MIMEText(message, 'plain', 'utf-8')
						sendmsg['From'] = formataddr([self.sender_name, self.sender_email])
						#单独发送给个人时可以配置该选项
						#sendmsg['To'] = formataddr([msgdict['rname'], msgdict['remail']])
						sendmsg['Subject'] = self.email_subject
						self.email_server.sendmail(self.sender_email, msgdict['remail'], sendmsg.as_string())
						if self.q.empty():
							break;
					self.email_server.quit() 
				time.sleep(1)
				pass
			except Exception as e:
				self.logger.error("email_task error{}".format(e))

	def send_email(self, receiver_email:list, receiver_name:list, device_sn:str, email_message:str):
		try:
			self.sender_email = config(self.confile_path).get('email', 'sender_email')
			self.sender_password = config(self.confile_path).get('email', 'sender_password')
			self.sender_name = config(self.confile_path).get('email', 'sender_name')
			#self.logger.info("self.sender_email={} self.sender_name={} self.sender_password={}".format(self.sender_email, self.sender_password, self.sender_name))
			if len(self.sender_email) != 0 and len(self.sender_password) != 0:
				self.q.put({"remail":receiver_email, "rname":receiver_name, "sn" : device_sn, "message" : email_message})
		except Exception as e:
			self.logger.error("send_email error:{}".format(e))
	
if __name__ == '__main__':
	e = tencent_email("测试邮箱")
	time.sleep(1)
	s = ['duanshuai@iotwonderful.com', 'duanbixing@163.com']
	n = ['duanshuai', 'duanshuai']
	e.send_email(s, n, '1234567890', 'hello test')
#e.send_email("duanshuai@iotwonderful.com", "段帅", "15841658367", "测试邮件= = ")
#	e.send_email("duanshuai@iotwonderful.com", "段帅", "15841658368", "测试邮件= = ")
#	e.send_email("duanshuai@iotwonderful.com", "段帅", "15841658369", "测试邮件= = ")
#	e.send_email("duanshuai@iotwonderful.com", "段帅", "15841658360", "测试邮件= = ")
