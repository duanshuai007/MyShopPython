#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import tkinter as tk
import tkinter.font as tkfont
import xpinyin
import global_variable

class window_put_in_storage():
	def __init__(self, root, db, check_input, msgbox, queue, logger):
		self.logger = logger
		self.root = root
		self.db = db
		self.check_input = check_input
		self.msgbox = msgbox
		self.queue = queue

	def __button_sell_callback(self):
		if self.sell_mode == True:
			self.sell_price_checkbutton_name.set('单价')
			self.sell_mode = False
		else:
			self.sell_price_checkbutton_name.set('总价')
			self.sell_mode = True

	def __button_confirm_callback(self, screen_id):
		# 货物入库界面按下确认键
		self.logger.info("入库货物")
		name = self.input_name_entry.get()
		number_str = self.input_number_entry.get()
		money_str = self.input_monery_entry.get()

		if not name or not number_str or not money_str:
			self.msgbox.show(screen_id, 240, 80, '请输入有效数')
			return

		#在goodnamelist中寻找对应货物名称
		flag = False
		for display_item in global_variable.goods_list:
			if name == display_item[1]:
				name_pinyin = display_item[2]
				product_id = display_item[0]
				flag = True
				break
		if flag is False:
			#没在goodnamelist中找到对应货物，视其为新货物
			unicode_name = u'%s' % name
			name_pinyin = xpinyin.Pinyin().get_pinyin(unicode_name)
			product_id = None
		self.logger.info("id={} name={} py={}".format(product_id, name, name_pinyin))

		input_number = int(number_str, 10)
		input_money = float(money_str)

		if self.sell_mode == True:
			# print '总价格'
			money = input_money
		else:
			# print '单独价格'
			money = input_number * input_money

		record_list = [[product_id, name, name_pinyin, 0, input_number, money],]
		self.logger.info(record_list)
		self.db.update(record_list)
		self.queue.put('update')

	def __button_cancel_callback(self, screenid):
		screenid.destroy()
		global_variable.child_exists = False

	def show(self, width_percent, height_percent):
		try:
			if global_variable.child_exists is True:
				self.logger.info("window put in storage open failed")
				return
			global_variable.child_exists = True
			
			self.root.update()
			xoffset = self.root.winfo_x()
			yoffset = self.root.winfo_y()
			main_width = int(global_variable.main_window['size']['w'])
			main_height = int(global_variable.main_window['size']['h'])
			child_width = int(main_width * width_percent)
			#child_height = int(main_height * height_percent)
			child_height = 90
			#if child_height < 90:
			#	child_height = 90
			if child_width > 290:
				child_width = 290
			#if child_height > 90:
			#	child_height = 90
			x = int(((main_width - child_width) / 2) + xoffset)
			y = int(((main_height - child_height) / 2) + yoffset)
			size = '{}x{}+{}+{}'.format(child_width, child_height, x, y)

			print(size)
			inputtop = tk.Toplevel(self.root)
			inputtop.geometry(size)
			inputtop.resizable(width=False, height=False)
			# 设置右上角的X功能
			inputtop.protocol("WM_DELETE_WINDOW", lambda arg=inputtop: self.__button_cancel_callback(arg))
			# 设置窗口始终在最上层
			inputtop.wm_attributes("-topmost", 1)
			inputtop.title('入库信息输入框')
			# self.inputtop.overrideredirect(True)   #隐藏边框标题
			# self.inputtop.positionfrom(who="user")
			# 单价or总价 切换标志
			self.sell_mode = False
			# label
			tk.Label(inputtop, text='货物名称', font=("黑体", 12)).grid(row=1, column=0, padx=1, pady=1)
			tk.Label(inputtop, text='货物数量', font=("黑体", 12)).grid(row=1, column=1, padx=1, pady=1)
			
			# 点击会自动切换显示的label
			self.sell_price_checkbutton_name = tk.StringVar()
			self.sell_price_checkbutton_name.set('单价')
			tk.Checkbutton(inputtop, textvariable=self.sell_price_checkbutton_name, command=self.__button_sell_callback).grid(
					row=1, column=2, padx=1, pady=1)

			# 对输入进行限制的函数
			self.check_input.set_current_topid(inputtop)
			check_input_is_number_handler = inputtop.register(self.check_input.check_input_is_number)
			check_input_is_not_number_and_speacil_handler = inputtop.register(self.check_input.check_input_is_not_number_and_speacil)
			# 货物名称输入框
			font = tkfont.Font(family="Consolas", size=10, weight="normal")
			m_len = font.measure("0")
			total_len = int(child_width / m_len) - 3

			m = child_width - ((total_len + 3) * m_len)
			w1 = int(total_len * 0.4)
			w3 = w1
			w2 = total_len - w1 - w3
			if w1 + w2 + w3 != total_len:
				if w1 + w2 + w3 + m <= total_len - 3:
					w2 = w2 + m
			var1 = tk.StringVar()
			self.input_name_entry = tk.Entry(inputtop, textvariable=var1, width=w1, validate='key',
					validatecommand=(check_input_is_not_number_and_speacil_handler, '%P'))
			self.input_name_entry.grid(row=2, column=0, padx=1, pady=1)
			# 货物数量输入框
			var2 = tk.StringVar()
			# %P代表输入框的实时内容)
			self.input_number_entry = tk.Entry(inputtop, textvariable=var2, width=w2, validate='key',
					validatecommand=(check_input_is_number_handler, '%P')) 
			self.input_number_entry.grid(row=2, column=1, padx=1, pady=1)

			# 货物钱数输入框（单价or总价）
			var3 = tk.StringVar()
			self.input_monery_entry = tk.Entry(inputtop, textvariable=var3, width=w3, validate='key',
					validatecommand=(check_input_is_number_handler, '%P'))
			self.input_monery_entry.grid(row=2, column=2, padx=1, pady=1)
			# 按钮
			tk.Button(inputtop, text='确认', command=lambda: self.__button_confirm_callback(inputtop)).grid(row=3, column=1,
					padx=1, pady=1)
			tk.Button(inputtop, text='取消', command=lambda: self.__button_cancel_callback(inputtop)).grid(row=3, column=2,
					padx=1, pady=1)
			return inputtop
		except Exception as e:
			self.logger.error("window_put_in_storage show error:{}".format(e))


