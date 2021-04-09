#!/usr/bin/env python
# -*- coding:utf-8 -*-

# from tkinter import *
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tkm
import time
import re
import threading
import xpinyin
import queue

from warehouse import warehouse
from logger import LoggingConsumer, LoggingProducer
from window_putinstorage import window_put_in_storage
from window_sellgoods import windos_sell_goods
from msgbox import msgbox
import check_input
import global_variable 

# 登陆功能 https://www.cnblogs.com/wwf828/p/7418181.html#autoid-15-0-0
# py3.7 MySQLdb https://www.cnblogs.com/SH170706/p/10082987.html, https://pypi.org/project/mysqlclient/#files
class FindLocation(object):
	def __init__(self):
		# 创建主窗口,用于容纳其它组件
		try:
			#初始化log接口
			self.logger = LoggingProducer().get_default_logger()
			#初始化数据库接口
			self.db = warehouse()
			#初始化显示接口
			self.root = tk.Tk()
			# 给主窗口设置标题内容
			self.root.update()
			root_width = self.root.winfo_screenwidth()
			root_height = self.root.winfo_screenheight()

			global_variable.main_window['screen']['w'] = root_width
			global_variable.main_window['screen']['h'] = root_height

			percent = int(global_variable.main_window['percent'])
			if percent < 50:
				percent = 50
				global_variable.main_window['percent'] = 50
			main_widht = int(root_width * percent / 100)
			main_height = int(root_height * percent / 100)
			main_xoffset = int((root_width - main_widht) / 2)
			main_yoffset = int((root_height - main_height) / 2)
			global_variable.main_window['size']['w'] = main_widht
			global_variable.main_window['size']['h'] = main_height 
			global_variable.main_window['size']['x'] = main_xoffset
			global_variable.main_window['size']['y'] = main_yoffset

			self.root.title("收货记账小工具")
			self.root.geometry("{}x{}+{}+{}".format(main_widht, main_height, main_xoffset, main_yoffset))
			self.root.resizable(width=False, height=False)

			self.toplevel_id = 0
			# 查询是否有今日的表，如果没有就创建今日表
			self.db.create_db()
			self.update_queue = queue.Queue(4)

			self.msgbox = msgbox(self.root, self.logger)
			self.check_input = check_input.check_input(self.root, self.msgbox, self.logger)
			self.window_putinstorage = window_put_in_storage(self.root, self.db, self.check_input, self.msgbox, self.update_queue, self.logger)
			self.windos_sellgoods = windos_sell_goods(self.root, self.db, self.check_input, self.msgbox, self.update_queue, self.logger)

			#每个按钮的大小
			w = int(int(global_variable.main_window['size']['w']) / 10)
			h = int(int(global_variable.main_window['size']['h']) / 10)
			#按钮的起始位置
			x = int(w / 10)
			y = x
			#s表示连个按钮上下之间的距离
			s = x
			font_size = int(w / 6)
			self.sell_button = tk.Button(self.root, command=self.FuncSell, text="售出", bd=10, bg='white', font=("黑体", font_size))
			self.input_button = tk.Button(self.root, command=self.FuncInput, text="入库", bd=10, bg='white', font=("黑体", font_size))
			self.tongji_day_button = tk.Button(self.root, command=self.FuncTJDay, text="当日", bd=10, bg='white',font=("黑体", font_size))
			self.tongji_month_button = tk.Button(self.root, command=self.FuncTJMonth, text="当月", bd=10, bg='white',font=("黑体", font_size))

			self.sell_button.place(x=x, y=y, width=w, height=h)
			y = y + h + s
			self.input_button.place(x=x, y=y, width=w, height=h)
			y = y + h + s
			self.tongji_day_button.place(x=x, y=y, width=w, height=h)
			y = y + h + s
			self.tongji_month_button.place(x=x, y=y, width=w, height=h)

			#计算主窗口显示商品信息窗口的长宽高
			display_start_x = x + w + s
			display_start_y = x
			# 两侧留出 x 大小的空余空间
			display_width = int(global_variable.main_window['size']['w']) - display_start_x - x
			# 底部留出 x 大小的空余空间
			display_height = int(global_variable.main_window['size']['h']) - display_start_y - x

			# 参考自https://cloud.tencent.com/developer/ask/130543
			# 参考自https://www.cnblogs.com/qwangxiao/p/9940972.html
			clos = ('编号', '商品名称', '入库数量', '已卖数量', '库存剩余', '总成本', '总收入')
			self.display_info = ttk.Treeview(self.root, columns=clos, show='headings')
			for col in clos:
				self.display_info.heading(col, text=col)
			self.display_info.grid(row=1, column=0, columnspan=2)
			# 设置列的宽度和对齐方式
			w = int(display_width / 10)
			self.display_info.column('0', width=w,		anchor='center')
			self.display_info.column('1', width=w*2,	anchor='center')
			self.display_info.column('2', width=w,		anchor='center')
			self.display_info.column('3', width=w,		anchor='center')
			self.display_info.column('4', width=w,		anchor='center')
			self.display_info.column('5', width=w*2,	anchor='center')
			self.display_info.column('6', width=w*2,	anchor='center')
			self.display_info.place(x=display_start_x, y=display_start_y, width=display_width, height=display_height)

			# 创建刷新显示的线程
			t1 = threading.Thread(target=self.ThreadUpdateDisplay, args=())
			t1.setDaemon(True)
			t1.start()
		except Exception as e:
			self.logger.error("class init error:{}".format(e))

	def ThreadUpdateDisplay(self):
		while True:
			try:
				if not self.update_queue.empty():
					msg = self.update_queue.get()
					dbmsg_list = self.db.getall()
					dbmsg_list.sort(key=lambda e: e[0], reverse=False)
					alreadyExitsItem = self.display_info.get_children()
					for dbitem in dbmsg_list:
						in_display = False
						for displayitem in alreadyExitsItem:
							displayitem_text = self.display_info.item(displayitem, "values")
							if dbitem[0] == int(displayitem_text[0]):
								in_display = True
								#更新总库存数量显示
								if  dbitem[3] != int(displayitem_text[2]):
									self.display_info.set(displayitem, 2, dbitem[3])
								#更新已售出数量显示
								if dbitem[4] != int(displayitem_text[3]):
									self.display_info.set(displayitem, 3, dbitem[4])
								#更新总成本显示
								if dbitem[5] != float(displayitem_text[5]):
									self.display_info.set(displayitem, 5, dbitem[5])
								#更新总收入显示
								if dbitem[6] != float(displayitem_text[6]):
									self.display_info.set(displayitem, 6, dbitem[6])
								#更新剩余库存数量显示
								self.display_info.set(displayitem, 4, dbitem[3] - dbitem[4])
								break
						if in_display is False:
							#id, 商品名, 商品名拼音, 总库存, 总售出数量, 库存剩余, 总成本, 总收入
							item = [dbitem[0], dbitem[1], dbitem[3], dbitem[4], dbitem[3] - dbitem[4], dbitem[5], dbitem[6]]
							self.display_info.insert("", "end", values=item)
							global_variable.goods_list.append([dbitem[0], dbitem[1], dbitem[2]])
			except Exception as e:
				self.logger.error("ThreadUpdateDisplay error:{}".format(e))

	def FuncSell(self):
		self.windos_sellgoods.show(0.6, 0.4)

	def FuncInput(self):
		self.window_putinstorage.show(0.3, 0.1)

	def FuncTJDay(self):
		'''
		self.inputtop = tk.Toplevel(self.root)
		self.inputtop.geometry(size)
		self.inputtop.resizable(width=False, height=False)
		# 设置右上角的X功能
		self.inputtop.protocol("WM_DELETE_WINDOW", lambda arg=self.inputtop: self.FuncButtonCancel(arg))
		# 设置窗口始终在最上层
		self.inputtop.wm_attributes("-topmost", 1)
		self.inputtop.title('入库信息输入框')
		# self.inputtop.overrideredirect(True)   #隐藏边框标题
		# self.inputtop.positionfrom(who="user")
		self.toplevel_id = self.inputtop
		'''
		size = self.create_window_size(800, 280)
		tkm.showinfo('警告','已存在总金额信息')

	def FuncTJMonth(self):
		print('tongji month')

	def FuncSetting(self):
		label0 = tk.Label(self.root, text="priFuncSetting")
		label0.grid(column=0)

	def FuncHelp(self):
		label0 = tk.Label(self.root, text="priFuncHelp")
		label0.grid(column=0)

	def FuncVersion(self):
		label0 = tk.Label(self.root, text="priFuncVersion")
		label0.grid(column=0)

	def FuncUserRegister(self):
		label0 = tk.Label(self.root, text="FuncUserRegister")
		label0.grid(column=0)

	def FuncUserLogin(self):
		label0 = tk.Label(self.root, text="FuncUserLogin")
		label0.grid(column=0)

	def FuncUserQuit(self):
		label0 = tk.Label(self.root, text="FuncUserQuit")
		label0.grid(column=0)

	# 完成布局
	def gui_arrang(self):
		menu = tk.Menu(self.root)
		# mb0 = Menubutton(self.root, text="用户xxx")
		cascade0 = tk.Menu(menu, tearoff=False)
		cascade0.add_command(label="注册", command=self.FuncUserRegister)
		cascade0.add_separator()
		cascade0.add_command(label="登陆", command=self.FuncUserLogin)
		cascade0.add_separator()
		cascade0.add_command(label="退出", command=self.FuncUserQuit)
		menu.add_cascade(label="用户", menu=cascade0)

		menu.add_command(label='设置', command=self.FuncSetting)
		menu.add_command(label='帮助', command=self.FuncHelp)

		cascade1 = tk.Menu(menu, tearoff=False)
		cascade1.add_command(label='版本信息', command=self.FuncVersion)
		cascade1.add_separator()
		cascade1.add_checkbutton(label='试用30天')
		cascade1.add_separator()
		cascade1.add_radiobutton(label='七七八八')
		cascade1.add_radiobutton(label='不三不四')
		menu.add_cascade(label='About', menu=cascade1)

		self.root['menu'] = menu
		#初始化完成后，主动刷新显示区域
		self.update_queue.put('update')


def main():
	# 初始化对象
	LoggingConsumer()
	FL = FindLocation()
	if FL is None:
		print("init error")
		exit(1)
	# 进行布局
	FL.gui_arrang()
	# 主程序执行
	tk.mainloop()
	pass

if __name__ == "__main__":
	main()
