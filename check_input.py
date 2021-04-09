#!/usr/bin/env python3
#-*- coding:utf-8 -*-

#import tkinter.messagebox as tkm
import re

class check_input():
	topid = None
	def __init__(self, root, msgbox, logger):
		self.root = root
		self.logger = logger
		self.msgbox = msgbox
	
	def set_current_topid(self, topid):
		self.topid = topid

	def check_input_is_number(self, content):
		# 如果不加上==""的话，就会发现删不完。总会剩下一个数字
		if (len(content) > 10):
			self.msgbox.show(self.topid, 240, 80, '数据过长')
			return False
		rule = r"^[0-9]+\.?[0-9]?$"
		ret = re.match(rule, content)
		if ret or content == "":
			return True
		else:
			if self.topid is not None:
				self.msgbox.show(self.topid, 240, 80, '只能够输入数字')
				#tkm.showinfo('警告','ttk只能够输入数字')
			return False

	def check_input_is_not_number_and_speacil(self, content):
		if (len(content) > 20):
			self.msgbox.show(self.topid, 240, 80, '数据过长')
			return False
		rule = r"(^[\u4e00-\u9fa5]{0,}$)|(^[A-Za-z]+$)"
		ret = re.match(rule, content)
		if ret or content == "":
			return True
		else:
			if self.topid is not None:
				self.msgbox.show(self.topid, 240, 80, '只能够输入数字或字母')
			return False

