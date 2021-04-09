#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import tkinter as tk
import global_variable

class msgbox():
	def __init__(self, root, logger):
		self.root = root
		self.logger = logger
		self.exists = False

	def __button_cancel_callback(self, screenid):
		# print 'button cancel'
		screenid.destroy()
		if self.exists == True:
			self.exists = False

	def show(self, toplevel_id, width, height, msg):
		if self.exists == True:
			return
		try:
			self.exists = True

			self.root.update()
			xoffset = self.root.winfo_x()
			yoffset = self.root.winfo_y()
			child_width = int(((global_variable.main_window['size']['w'] - width) / 2) + xoffset)
			child_height = int(((global_variable.main_window['size']['h'] - height) / 2) + yoffset)
			size = '{}x{}+{}+{}'.format(width, height, child_width, child_height)
			thisTop = tk.Toplevel(toplevel_id)
			thisTop.resizable(False, False)
			thisTop.geometry(size)
			thisTop.wm_attributes('-topmost', True)
			# 设置右上角的X功能
			thisTop.protocol("WM_DELETE_WINDOW", lambda arg=thisTop: self.__button_cancel_callback(arg))
			# 设置窗口始终在最上层
			# self.selltop.wm_attributes("-topmost", 1)
			thisTop.title('Warning')
			tk.Label(thisTop, text=msg, fg='red', bg='blue', font=('黑体', 18)).pack()
			tk.Button(thisTop, text='确认', font=('黑体', 14), command=lambda: self.__button_cancel_callback(thisTop)).pack()
		except Exception as e:
			self.logger.error("msgbox show error:{}".format(e))
