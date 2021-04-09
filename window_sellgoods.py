#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import tkinter as tk
import global_variable

class windos_sell_goods():
	def __init__(self, root, db, check_input, msgbox, queue, logger):
		self.logger = logger
		self.root = root
		self.db = db
		self.check_input = check_input
		self.msgbox = msgbox
		self.exists = False
		self.toplevel = None
		self.queue = queue

	def __button_cancel_callback(self, screenid):
		screenid.destroy()
		global_variable.child_exists = False

	def __button_confirm_callback(self, scrrenid):
		try:
			if flag == 1:
				# 售出货物界面按下确认键
				self.logger.info("售出货物")
				name = self.sell_name_entry.get()
				number_str = self.sell_number_entry.get()
				money_str = self.sell_monery_entry.get()
				if not name or not number_str or not money_str:
					self.msgbox.show(scrrenid, 240, 80,  '请输入有效数据')
					return
				self.logger.info("售出:name = {} number = {} money = {}".format(name, number_str, money_str))
	 
				flag = False
				for display_item in global_variable.goods_list:
					if name == display_item[1]:
						name_pinyin = display_item[2]
						product_id = display_item[0]
						flag = True
						break
				if flag is False:
					#没在goodnamelist中找到对应货物，视其为新货物
					self.logger.error("can not find good name")
					self.msgbox.show(scrrenid, 240, 80, '没能发现对应的货物')
					return

				input_number = int(number_str, 10) 
				input_money = float(money_str)

				# 需要知道历史上数据库中保存的商品库存情况
				record_list = [[product_id, name, name_pinyin, 1, input_number, input_money],]
				self.db.update(record_list)
				self.queue.put('update')
			elif flag == 2:
				num = self.sell_mull_result_listbox.size()
				# print 'have %d' % num
				if num < 2:
					# tkm.showinfo('警告','请确认数据输入是否正确!')
					self.ShowMessageBox('数据有错误')
					self.msgbox.show(scrrenid, 240, 80, '数据有错误')
					return

				for val in self.sell_mull_result_listbox.get(0, last='end'):
					if val.startswith('total'):
						print('date right')
						return

				# tkm.showinfo('警告','请确认数据输入是否正确!')
				self.msgbox.show(scrrenid, 240, 80, '数据有错误')
				self.queue.put('update')
			else:
				self.logger.info('other widget button')
		except Exception as e:
			self.logger.error("__button_confirm_callback error:{}".format(e))

	def sellRadiobuttonFunc(self):
		who = self.sell_radiobutton_var.get()
		if who == '1':
			self.sell_flag = False
			self.sell_name_entry.__setitem__('state', 'normal')
			self.sell_number_entry.__setitem__('state', 'normal')
			self.sell_monery_entry.__setitem__('state', 'normal')
			self.sell_name_listbox.__setitem__('state', 'normal')
			self.sell_YesButton.__setitem__('state', 'normal')
			self.sell_CancelButton.__setitem__('state', 'normal')

			self.sell_mull_name_entry.__setitem__('state', 'disabled')
			self.sell_mull_number_entry.__setitem__('state', 'disabled')
			self.sell_mull_money_entry.__setitem__('state', 'disabled')
			self.sell_mull_AddButtonOne.__setitem__('state', 'disabled')
			self.sell_mull_AddButtonTwo.__setitem__('state', 'disabled')
			self.sell_mull_name_listbox.__setitem__('state', 'disabled')
			self.sell_mull_result_listbox.__setitem__('state', 'disabled')
			self.sell_mull_YesButton.__setitem__('state', 'disabled')
			self.sell_mull_CancelButton.__setitem__('state', 'disabled')
		else:
			self.sell_flag = True
			self.sell_name_entry.__setitem__('state', 'disabled')
			self.sell_number_entry.__setitem__('state', 'disabled')
			self.sell_monery_entry.__setitem__('state', 'disabled')
			self.sell_name_listbox.__setitem__('state', 'disabled')
			self.sell_YesButton.__setitem__('state', 'disabled')
			self.sell_CancelButton.__setitem__('state', 'disabled')

			self.sell_mull_name_entry.__setitem__('state', 'normal')
			self.sell_mull_number_entry.__setitem__('state', 'normal')
			self.sell_mull_money_entry.__setitem__('state', 'normal')
			self.sell_mull_AddButtonOne.__setitem__('state', 'normal')
			self.sell_mull_AddButtonTwo.__setitem__('state', 'normal')
			self.sell_mull_name_listbox.__setitem__('state', 'normal')
			self.sell_mull_result_listbox.__setitem__('state', 'normal')
			self.sell_mull_YesButton.__setitem__('state', 'normal')
			self.sell_mull_CancelButton.__setitem__('state', 'normal')

	def SellMullResultListboxDoubleClickFunc(self, event):
		select = self.sell_mull_result_listbox.curselection()
		if select:
			self.sell_mull_result_listbox.delete(select)

	def FuncSellComboxSelectedHander(self, args):
		if self.sell_flag == False:
			select = self.sell_name_listbox.curselection()
			if select:
				name = self.sell_name_listbox.get(select)
				self.sell_name_entry_var.set(name)
			else:
				select = self.sell_mull_name_listbox.curselection()
				if select:
					name = self.sell_mull_name_listbox.get(select)
					self.sell_mull_name_entry_var.set(name)

	def FuncButtonSellMullAdd(self, args):
		if args == 1:  # 添加条目信息
			name = self.sell_mull_name_entry.get()
			number_str = self.sell_mull_number_entry.get()
			if not name or not number_str:
				self.msgbox.show(self.toplevel, 240, 80, '请输入有效数据')
				return
            # 判断name是不是字母，如果是字母则直接提取list里的第一条信息作为name值
			for val in name:
				if val >= 'a' and val <= 'z':
					name = self.sell_mull_name_listbox.get(0)
				elif val >= 'A' and val <= 'Z':
					name = self.sell_mull_name_listbox.get(0)
				else:
					break
            # 将数据加入到右侧list中显示
			val = '%sx%s' % (name, number_str)
			self.sell_mull_result_listbox.insert('end', val)
		elif args == 2:  # 添加总金额信息
			money_str = self.sell_mull_money_entry.get()
			if not money_str:
				self.msgbox.show(self.toplevel, 240, 80, '请输入有效数据')
				return

			for val in self.sell_mull_result_listbox.get(0, last='end'):
				if val.startswith('total'):
					self.msgbox.show(self.toplevel, 240, 80, '已存在总金额信息')
					return

			val = 'total:%s' % money_str
			self.sell_mull_result_listbox.insert('end', val)
		else:
			self.msgbox.show(self.toplevel, 240, 80, '已存在总金额信息')

	def show(self, width_percent, height_percent):
		try:
			if global_variable.child_exists is True:
				self.logger.info("window sellgoods open failed!")
				return
			global_variable.child_exists = True

			self.root.update()
			xoffset = self.root.winfo_x()
			yoffset = self.root.winfo_y()
			main_width = int(global_variable.main_window['size']['w'])
			main_height = int(global_variable.main_window['size']['h'])
			child_width = int(main_width * width_percent)
			child_height = int(main_height * height_percent)
			if child_height < 160: 
				child_height = 160
			x = int(((main_width - child_width) / 2) + xoffset)
			y = int(((main_height - child_height) / 2) + yoffset)
			size = '{}x{}+{}+{}'.format(child_width, child_height, x, y)

			self.toplevel = tk.Toplevel(self.root)
			self.toplevel.geometry(size)
			self.toplevel.resizable(width=False, height=False)
			# 设置右上角的X功能
			self.toplevel.protocol("WM_DELETE_WINDOW", lambda arg=self.toplevel: self.__button_cancel_callback(arg))
			# 设置窗口始终在最上层
			self.toplevel.wm_attributes("-topmost", 1)
			self.toplevel.title('售出信息输入框')
			# radiobutton
			self.sell_flag = False  # 用来判断是单条记录还是多条记录的标志位
			self.sell_radiobutton_var = tk.StringVar()
			self.sell_radiobutton_var.set(1)  # 设置默认值为value=1的选项，即‘单条记录’
			tk.Radiobutton(self.toplevel, text='单条记录', variable=self.sell_radiobutton_var, value=1,
						   command=self.sellRadiobuttonFunc).grid(row=0, column=0, padx=10, pady=1, columnspan=3)
			tk.Radiobutton(self.toplevel, text='组合记录', variable=self.sell_radiobutton_var, value=2,
						   command=self.sellRadiobuttonFunc).grid(row=0, column=4, padx=10, pady=1, columnspan=6)
			# 画布 绘制中间的分割线
			canvas_width = 20
			canvas_height = int(global_variable.main_window['size']['h'])
			canvas = tk.Canvas(self.toplevel, width=canvas_width, height=canvas_height)
			# canvas.place(x=10,y=10, width=100, height=200)
			canvas.grid(row=0, column=3, padx=1, pady=1, rowspan=10)
			canvas.create_line(canvas_width / 2, 0, canvas_width / 2, canvas_height)
			# label
			tk.Label(self.toplevel, text='货物名称').grid(row=1, column=0, padx=1, pady=1)
			tk.Label(self.toplevel, text='货物数量').grid(row=1, column=1, padx=1, pady=1)
			tk.Label(self.toplevel, text='金 额').grid(row=1, column=2, padx=1, pady=1)
			# 输入框限制函数
			check_input_is_number_handler = self.toplevel.register(self.check_input.check_input_is_number)
			get_name_by_pinyin = self.toplevel.register(self.get_name_by_pinyin_func)
			# 货物名称输入框
			self.sell_name_entry_var = tk.StringVar()
			self.sell_name_entry = tk.Entry(self.toplevel, textvariable=self.sell_name_entry_var, validate='key',
											validatecommand=(get_name_by_pinyin, '%P'))
			self.sell_name_entry.grid(row=2, column=0, padx=1, pady=1)
			
			# 显示选项的listbox
			var1 = tk.StringVar()
			self.sell_name_listbox = tk.Listbox(self.toplevel, listvariable=var1, selectmode="browse")
			self.sell_name_listbox.grid(row=3, column=0, padx=1, pady=1)
			self.sell_name_listbox.bind("<<ListboxSelect>>", self.FuncSellComboxSelectedHander)
			# 货物数量输入框
			var2 = tk.StringVar()
			self.sell_number_entry = tk.Entry(self.toplevel, textvariable=var2, width=8, validate='key',
											  validatecommand=(check_input_is_number_handler, '%P'))  # %P代表输入框的实时内容)
			self.sell_number_entry.grid(row=2, column=1, padx=1, pady=1)
			# 货物钱数输入框（单价or总价）
			var3 = tk.StringVar()
			self.sell_monery_entry = tk.Entry(self.toplevel, textvariable=var3, width=8, validate='key',
											  validatecommand=(check_input_is_number_handler, '%P'))
			self.sell_monery_entry.grid(row=2, column=2, padx=1, pady=1)
			# 按钮
			self.sell_YesButton = tk.Button(self.toplevel, text='确认', command=lambda: self.__button_confirm_callback(self.toplevel, 1))
			self.sell_YesButton.grid(row=3, column=1, padx=1, pady=1)
			self.sell_CancelButton = tk.Button(self.toplevel, text='取消', command=lambda: self.__button_cancel_callback(self.toplevel))
			self.sell_CancelButton.grid(row=3, column=2, padx=1, pady=1)

			# 右侧多条记录的界面
			# label
			tk.Label(self.toplevel, text='货物名称').place(x=300, y=30, width=100, height=22)
			self.sell_mull_name_entry_var = tk.StringVar()
			self.sell_mull_name_entry = tk.Entry(self.toplevel, textvariable=self.sell_mull_name_entry_var, validate='key',
												 validatecommand=(get_name_by_pinyin, '%P'))
			self.sell_mull_name_entry.place(x=298, y=55, width=120, height=22)

			tk.Label(self.toplevel, text='货物数量').place(x=410, y=30, width=100, height=22)
			var_mull0 = tk.StringVar()
			self.sell_mull_number_entry = tk.Entry(self.toplevel, textvariable=var_mull0, validate='key',
												   validatecommand=(check_input_is_number_handler, '%P'))
			self.sell_mull_number_entry.place(x=430, y=55, width=50, height=22)

			tk.Label(self.toplevel, text='双击来删除对应条目', fg='red').place(x=570, y=30, width=160, height=22)

			tk.Label(self.toplevel, text='总金额').place(x=400, y=85, width=100, height=22)
			var_mull3 = tk.StringVar()
			self.sell_mull_money_entry = tk.Entry(self.toplevel, textvariable=var_mull3, validate='key',
												  validatecommand=(check_input_is_number_handler, '%P'))
			self.sell_mull_money_entry.place(x=430, y=110, width=50, height=22)

			# 添加功能按钮
			# 这个添加按钮是放在货物信息右面
			self.sell_mull_AddButtonOne = tk.Button(self.toplevel, text='添加',
													command=lambda arg=1: self.FuncButtonSellMullAdd(arg, 1))
			self.sell_mull_AddButtonOne.place(x=500, y=55, width=50, height=22)
			# 这个按钮是放在总金额的右面
			self.sell_mull_AddButtonTwo = tk.Button(self.toplevel, text='添加',
													command=lambda arg=2: self.FuncButtonSellMullAdd(arg, 2))
			self.sell_mull_AddButtonTwo.place(x=500, y=110, width=50, height=22)

			# 显示根据拼音显示出来的选项的listbox
			var_mull1 = tk.StringVar()
			self.sell_mull_name_listbox = tk.Listbox(self.toplevel, listvariable=var_mull1, selectmode="browse")
			# self.sell_mull_name_listbox.grid(row=3, column=4, padx=1, pady=1)
			self.sell_mull_name_listbox.place(x=298, y=85, width=120, height=180)
			self.sell_mull_name_listbox.bind("<<ListboxSelect>>", self.FuncSellComboxSelectedHander)
			# 显示添加结果的列表的listbox
			var_mull2 = tk.StringVar()
			self.sell_mull_result_listbox = tk.Listbox(self.toplevel, listvariable=var_mull2, selectmode="browse")
			self.sell_mull_result_listbox.place(x=580, y=55, width=140, height=200)
			self.sell_mull_result_listbox.bind("<Double-Button-1>", self.SellMullResultListboxDoubleClickFunc)

			# 确认按钮
			self.sell_mull_YesButton = tk.Button(self.toplevel, text='确认',
												 command=lambda: self.__button_confirm_callback(self.toplevel, 2))
			self.sell_mull_YesButton.place(x=430, y=200, width=50, height=22)
			# 取消按钮
			self.sell_mull_CancelButton = tk.Button(self.toplevel, text='取消',
													command=lambda: self.__button_cancel_callback(self.toplevel))
			self.sell_mull_CancelButton.place(x=490, y=200, width=50, height=22)
			# 设置右侧按钮位disable状态
			self.sell_mull_name_entry.__setitem__('state', 'disabled')
			self.sell_mull_number_entry.__setitem__('state', 'disabled')
			self.sell_mull_money_entry.__setitem__('state', 'disabled')
			self.sell_mull_AddButtonOne.__setitem__('state', 'disabled')
			self.sell_mull_AddButtonTwo.__setitem__('state', 'disabled')
			self.sell_mull_name_listbox.__setitem__('state', 'disabled')
			self.sell_mull_result_listbox.__setitem__('state', 'disabled')
			self.sell_mull_YesButton.__setitem__('state', 'disabled')
			self.sell_mull_CancelButton.__setitem__('state', 'disabled')
		except Exception as e:
			self.logger.error("windos_sell_goods show error:{}".format(e))

	
	def get_name_by_pinyin_func(self, content):
		display_list = []
		content = content.lower()  # 转换为小写
		# rule = r"^[aA-zZ]+$"
		rule = r"^[a-z]+$"
		ret = re.match(rule, content)

		self.logger.info("get_name_by_pinyin_func: ret={} content={}".format(ret, content))
		if ret or content == "":
			for proid, name, name_pinyin in global_variable.goods_list:
				name_pinyin_list = name_pinyin.split('-')
				content_len = len(content) - 1
				ch_pos = 0
				add_flag = False
				# 寻找名字符合拼音的对象项
				for ch in content:
					if len(name_pinyin_list) > ch_pos:
						if name_pinyin_list[ch_pos].startswith(ch):
							if ch_pos == content_len:
								add_flag = True
								break
						else:
							break
					else:
						break
					ch_pos += 1
				if add_flag == True:
					if name not in display_list:
						display_list.append(name)
            # self.sell_comboxlist["values"] = display_list
            # 一次性添加所有值，但是会把list的[]也添加进去
            # self.sell_name_listbox_var.set(display_list)
            # 删除listbox内全部元素
			if self.sell_flag == False:
				self.sell_name_listbox.delete(0, last='end')
				for val in display_list:
					self.sell_name_listbox.insert('end', val)
			else:
				self.sell_mull_name_listbox.delete(0, last='end')
				for val in display_list:
					self.sell_mull_name_listbox.insert('end', val)
			return True
		else:
            # 从list列表中查看当前文本框中的内容是不是list里的内容，如果是，说明是点击或手动输入的
			if self.sell_flag == False:
				for item_name in self.sell_name_listbox.get(0, last='end'):
                    # 以startswith方式判断，这样当文本框中的内容被删除一个或多个字时不回出现错误
                    #self.logger.info("item_name={} ret={} content={}".format(item_name, ret, content))
					if item_name.startswith(content):
						return True
			else:
				for item_name in self.sell_mull_name_listbox.get(0, last='end'):
					if item_name.startswith(content):
						return True

			self.msgbox.show(self.toplevel, 240, 80, '只能够输入拼音字母')
			return False

