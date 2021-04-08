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

from warehouse import warehouse
from logger import LoggingConsumer, LoggingProducer

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
			self.RootWidth = int(self.root.winfo_screenwidth() * 3 / 4)
			self.RootHeight = int(self.root.winfo_screenheight() * 3 / 4)
			self.Root_xoffset = self.root.winfo_x()
			self.Root_yoffset = self.root.winfo_y()

			self.root.title("收货记账小工具")
			set_screen_string = "{}x{}".format(self.RootWidth, self.RootHeight)
			self.root.geometry(set_screen_string)
			self.root.resizable(width=False, height=False)

			self.child_screen_exits = False
			self.messagebox_exits = False
			self.sell_flag = False  # 用来判断是单条记录还是多条记录的标志位
			self.toplevel_id = 0
			# 查询是否有今日的表，如果没有就创建今日表
			self.db.create_db()
			#self.db.create_tb()

			self.goodsNameList = []

			# 参考自https://cloud.tencent.com/developer/ask/130543
			# 参考自https://www.cnblogs.com/qwangxiao/p/9940972.html
			clos = ('编号', '商品名称', '入库数量', '已卖数量', '库存剩余', '总成本', '总收入')
			self.display_info = ttk.Treeview(self.root, columns=clos, show='headings')
			for col in clos:
				self.display_info.heading(col, text=col)
			self.display_info.grid(row=1, column=0, columnspan=2)
			# 设置列的宽度和对齐方式
			self.display_info.column('0', width=30, anchor='center')
			self.display_info.column('1', width=90, anchor='center')
			self.display_info.column('2', width=30, anchor='ne')
			self.display_info.column('3', width=30, anchor='n')
			self.display_info.column('4', width=30, anchor='center')
			self.display_info.column('5', width=60, anchor='center')
			self.display_info.column('6', width=60, anchor='center')
			# 创建一个查询结果的按钮
			self.sell_button = tk.Button(self.root, command=self.FuncSell, text="售出", bd=10, bg='white', font=("黑体", 36))
			self.input_button = tk.Button(self.root, command=self.FuncInput, text="入库", bd=10, bg='white', font=("黑体", 36))
			self.tongji_day_button = tk.Button(self.root, command=self.FuncTJDay, text="当日", bd=10, bg='white',font=("黑体", 36))
			self.tongji_month_button = tk.Button(self.root, command=self.FuncTJMonth, text="当月", bd=10, bg='white',font=("黑体", 36))
			# 创建刷新显示的线程
			t1 = threading.Thread(target=self.ThreadUpdateDisplay, args=())
			t1.setDaemon(True)
			t1.start()
		except Exception as e:
			self.logger.error("class init error:{}".format(e))

	def ThreadUpdateDisplay(self):
		self.display_need_update = True
		while True:
			try:
				if self.display_need_update is True:
					self.display_need_update = False
					#display_list_info = []
					dbmsg_list = self.db.getall()
					dbmsg_list.sort(key=lambda e: e[0], reverse=False)
					alreadyExitsItem = self.display_info.get_children()
					'''
					for dbitem in dbmsg_list:  # 从数据库的数据中提取出一条信息
						need_update = True
						in_display = False
						for displayitem in alreadyExitsItem:  # 从显示列表中提取一条信息
							displayitem_text = self.display_info.item(displayitem, "values")
							#比较商品编号
							#self.logger.info("{} type={} {} type={}".format(displayitem_text[0], type(displayitem_text[0]), dbitem[0], type(dbitem[0])))
							if dbitem[0] == int(displayitem_text[0]):
								in_display = True
								#比较商品的库存数量,卖出数量,成本,收入,如果不相同,则删除该条记录重新加入
								if dbitem[3] == int(displayitem_text[2]) and dbitem[4] == int(displayitem_text[3]) and dbitem[5] == float(displayitem_text[5]) and dbitem[6] == float(displayitem_text[6]):
									need_update = False
								else:
									self.logger.info("delete")
									self.display_info.delete(displayitem)
								break

						if in_display is False or (in_display is True and need_update is True):
							display_item = [dbitem[0], dbitem[1], dbitem[3], dbitem[4], dbitem[3] - dbitem[4], dbitem[5], dbitem[6]]
							display_list_info.append(display_item)
							self.goodsNameList.append([dbitem[0], dbitem[1], dbitem[2]])
							self.logger.info("新货物:id={} name={} pinyin={}".format(dbitem[0], dbitem[1], dbitem[2]))
							#self.logger.info(self.goodsNameList)
					for item in display_list_info:
						self.logger.info("insert")
						self.display_info.insert("", "end", 'item%i'%item[0], values=item)
					'''
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
							self.goodsNameList.append([dbitem[0], dbitem[1], dbitem[2]])
										
				time.sleep(0.1)
			except Exception as e:
				self.logger.error("ThreadUpdateDisplay error:{}".format(e))

	# def ShowMessageBoxClose(self, topid):
	#    topid.destroy()
	#    self.messagebox_exits = False


	def create_window_size(self, width, height):
		self.root.update()
		xoffset = self.root.winfo_x()
		yoffset = self.root.winfo_y()
		child_width = int(((self.RootWidth - width) / 2) + xoffset)
		child_height = int(((self.RootHeight - height) / 2) + yoffset)
		#size_str = '{}x{}+{}+{}'.format(width, height, child_width, child_height)
		return '{}x{}+{}+{}'.format(width, height, child_width, child_height)

	def ShowMessageBox(self, msg):
		if self.messagebox_exits == True:
			return
		try:
			self.messagebox_exits = True

			size = self.create_window_size(240, 80)

			thisTop = tk.Toplevel(self.toplevel_id)
			thisTop.resizable(False, False)
			thisTop.geometry(size)
			thisTop.wm_attributes('-topmost', True)
			# 设置右上角的X功能
			thisTop.protocol("WM_DELETE_WINDOW", lambda arg=thisTop: self.FuncButtonCancel(arg))
			# 设置窗口始终在最上层
			# self.selltop.wm_attributes("-topmost", 1)
			thisTop.title('Warning')
			tk.Label(thisTop, text=msg, fg='red', bg='blue', font=('黑体', 18)).pack()
			tk.Button(thisTop, text='确认', font=('黑体', 14), command=lambda: self.FuncButtonCancel(thisTop)).pack()
		except Exception as e:
			self.logger.error("ShowMessageBox error:{}".format(e))

	def SellCheckFunc(self):
		if self.sell_price_flag == True:
			self.sell_price_checkbutton_name.set('单价')
			self.sell_price_flag = False
		else:
			self.sell_price_checkbutton_name.set('总价')
			self.sell_price_flag = True

	def check_input_is_number(self, content):
		# 如果不加上==""的话，就会发现删不完。总会剩下一个数字
		rule = r"^[0-9]+\.?[0-9]?$"
		ret = re.match(rule, content)
		if ret or content == "":
			return True
		else:
			self.ShowMessageBox('只能够输入数字')
			return False
	
	def check_input_is_not_number_and_speacil(self, content):
		rule = r"(^[\u4e00-\u9fa5]{0,}$)|(^[A-Za-z]+$)"
		ret = re.match(rule, content)
		if ret or content == "":
			return True
		else:
			self.ShowMessageBox('只能够输入汉字或字母')
			return False

	# flag = 1 表示单个商品卖出的分支
	# flag = 2 表示商品入库的分支
	# flag = 3 表示多个商品卖出的分支
	def FuncButtonYes(self, screenid, flag):
		if self.child_screen_exits == False:
			return
		self.logger.info("press FuncButtonYes")
		try:
			if flag == 1:
				# 售出货物界面按下确认键
				self.logger.info("售出货物")
				name = self.sell_name_entry.get()
				number_str = self.sell_number_entry.get()
				money_str = self.sell_monery_entry.get()
				if not name or not number_str or not money_str:
					self.ShowMessageBox('请输入有效数据')
					return
				self.logger.info("售出:name = {} number = {} money = {}".format(name, number_str, money_str))
				
				flag = False
				for display_item in self.goodsNameList:
					if name == display_item[1]:
						name_pinyin = display_item[2]
						product_id = display_item[0]
						flag = True
						break
				if flag is False:
					#没在goodnamelist中找到对应货物，视其为新货物
					self.logger.error("can not find good name")
					self.ShowMessageBox('没能发现对应的货物')
					return

				input_number = int(number_str, 10)
				input_money = float(money_str)

				# 需要知道历史上数据库中保存的商品库存情况
#unicode_name = u'%s' % name
#				name_pinyin = xpinyin.Pinyin().get_pinyin(unicode_name)
				record_list = [[product_id, name, name_pinyin, 1, input_number, input_money],]
				self.db.update(record_list)
				self.display_need_update = True
			elif flag == 2:
				# 货物入库界面按下确认键
				self.logger.info("入库货物")
				name = self.input_name_entry.get()
				number_str = self.input_number_entry.get()
				money_str = self.input_monery_entry.get()
				
				if not name or not number_str or not money_str:
					self.ShowMessageBox('请输入有效数据')
					return

				#在goodnamelist中寻找对应货物名称
				flag = False
				for display_item in self.goodsNameList:
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

				if self.sell_price_flag == True:
					# print '总价格'
					money = input_money
				else:
					# print '单独价格'
					money = input_number * input_money

				record_list = [[product_id, name, name_pinyin, 0, input_number, money],]
				self.logger.info(record_list)
				self.db.update(record_list)
				self.display_need_update = True
			elif flag == 3:
				num = self.sell_mull_result_listbox.size()
				# print 'have %d' % num
				if num < 2:
					# tkm.showinfo('警告','请确认数据输入是否正确!')
					self.ShowMessageBox('数据有错误')
					return

				for val in self.sell_mull_result_listbox.get(0, last='end'):
					if val.startswith('total'):
						print('date right')
						return

				# tkm.showinfo('警告','请确认数据输入是否正确!')
				self.ShowMessageBox('数据有错误')
				self.display_need_update = True
			else:
				self.logger.info('other widget button')
		except Exception as e:
			self.logger.error("FuncButtonYes error:{}".format(e))

	def FuncButtonCancel(self, screenid):
		# print 'button cancel'
		screenid.destroy()
		if self.messagebox_exits == True:
			self.messagebox_exits = False
		elif self.child_screen_exits == True:
			self.child_screen_exits = False
			self.toplevel_id = 0
		else:
			print('error FuncButtonCancel')

	def FuncButtonSellMullAdd(self, args):
		if self.child_screen_exits == False:
			return

		if args == 1:  # 添加条目信息
			name = self.sell_mull_name_entry.get()
			number_str = self.sell_mull_number_entry.get()
			# print name
			# print number_str
			if not name or not number_str:
				# tkm.showinfo('警告','111请输入有效数据')
				self.ShowMessageBox('请输入有效数据')
				return
			# 判断name是不是字母，如果是字母则直接提取list里的第一条信息作为name值
			for val in name:
				if val >= 'a' and val <= 'z':
					name = self.sell_mull_name_listbox.get(0)
					# print name
				elif val >= 'A' and val <= 'Z':
					name = self.sell_mull_name_listbox.get(0)
					# print name
				else:
					break

			# 将数据加入到右侧list中显示
			val = '%sx%s' % (name, number_str)
			self.sell_mull_result_listbox.insert('end', val)
		elif args == 2:  # 添加总金额信息
			money_str = self.sell_mull_money_entry.get()
			if not money_str:
				# tkm.showinfo('警告','2222请输入有效数据')
				self.ShowMessageBox('请输入有效数据')
				return

			for val in self.sell_mull_result_listbox.get(0, last='end'):
				if val.startswith('total'):
					# tkm.showinfo('警告','已存在总金额信息')
					self.ShowMessageBox('已存在总金额信息')
					return

			val = 'total:%s' % money_str
			self.sell_mull_result_listbox.insert('end', val)
		else:
			# tkm.showinfo('警告','Error:PressButtonNoParamter')
			self.ShowMessageBox('已存在总金额信息')

	def SellMullResultListboxDoubleClickFunc(self, event):
		# print 'SellMullResultListboxDoubleClickFunc'
		select = self.sell_mull_result_listbox.curselection()
		if select:
			# print self.sell_mull_result_listbox.get(select)
			self.sell_mull_result_listbox.delete(select)

	def FuncSellComboxSelectedHander(self, args):
		#self.logger.info("FuncSellComboxSelectedHander:{}".format(args))
		if self.sell_flag == False:
			select = self.sell_name_listbox.curselection()
			#self.logger.info("FuncSellComboxSelectedHander signal sell:{}".format(select))
			if select:
				name = self.sell_name_listbox.get(select)
				self.sell_name_entry_var.set(name)
		else:
			select = self.sell_mull_name_listbox.curselection()
			#self.logger.info("FuncSellComboxSelectedHander mull sell:{}".format(select))
			if select:
				name = self.sell_mull_name_listbox.get(select)
				self.sell_mull_name_entry_var.set(name)

	def get_name_by_pinyin_func(self, content):
		display_list = []
		content = content.lower()  # 转换为小写
		# rule = r"^[aA-zZ]+$"
		rule = r"^[a-z]+$"
		ret = re.match(rule, content)

		self.logger.info("get_name_by_pinyin_func: ret={} content={}".format(ret, content))
		if ret or content == "":
			for proid, name, name_pinyin in self.goodsNameList:
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

			self.ShowMessageBox('只能够输入拼音字母')
			return False

	def sellRadiobuttonFunc(self):
		who = self.sell_radiobutton_var.get()
		# print who
		if who == '1':
			# print '111'
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
			# print '2222'
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

	def FuncSell(self):
		# print 'sell FuncSell'
		if self.child_screen_exits == True:
			# print 'sell screen exits'
			return
		# 该窗口分割成两个部分，左侧是单条卖货记录添加，右侧是组合卖货记录添加
		self.child_screen_exits = True
		##左侧的单次卖出窗口
		# 设置弹出窗口在主窗体的中间
		size = self.create_window_size(800, 280)
		self.selltop = tk.Toplevel(self.root)
		self.selltop.geometry(size)
		self.selltop.resizable(width=False, height=False)
		# 设置右上角的X功能
		self.selltop.protocol("WM_DELETE_WINDOW", lambda arg=self.selltop: self.FuncButtonCancel(arg))
		# 设置窗口始终在最上层
		self.selltop.wm_attributes("-topmost", 1)
		self.selltop.title('售出信息输入框')
		self.toplevel_id = self.selltop
		# radiobutton
		self.sell_flag = False  # 用来判断是单条记录还是多条记录的标志位
		self.sell_radiobutton_var = tk.StringVar()
		self.sell_radiobutton_var.set(1)  # 设置默认值为value=1的选项，即‘单条记录’
		tk.Radiobutton(self.selltop, text='单条记录', variable=self.sell_radiobutton_var, value=1,
					   command=self.sellRadiobuttonFunc).grid(row=0, column=0, padx=10, pady=1, columnspan=3)
		tk.Radiobutton(self.selltop, text='组合记录', variable=self.sell_radiobutton_var, value=2,
					   command=self.sellRadiobuttonFunc).grid(row=0, column=4, padx=10, pady=1, columnspan=6)
		# 画布 绘制中间的分割线
		canvas_width = 20
		canvas_height = 275
		canvas = tk.Canvas(self.selltop, width=canvas_width, height=canvas_height)
		# canvas.place(x=10,y=10, width=100, height=200)
		canvas.grid(row=0, column=3, padx=1, pady=1, rowspan=10)
		canvas.create_line(canvas_width / 2, 0, canvas_width / 2, canvas_height)
		# label
		tk.Label(self.selltop, text='货物名称').grid(row=1, column=0, padx=1, pady=1)
		tk.Label(self.selltop, text='货物数量').grid(row=1, column=1, padx=1, pady=1)
		tk.Label(self.selltop, text='金 额').grid(row=1, column=2, padx=1, pady=1)
		# 输入框限制函数
		check_input_is_number_handler = self.selltop.register(self.check_input_is_number)
		get_name_by_pinyin = self.selltop.register(self.get_name_by_pinyin_func)
		# 货物名称输入框
		self.sell_name_entry_var = tk.StringVar()
		self.sell_name_entry = tk.Entry(self.selltop, textvariable=self.sell_name_entry_var, validate='key',
										validatecommand=(get_name_by_pinyin, '%P'))
		self.sell_name_entry.grid(row=2, column=0, padx=1, pady=1)
		# 显示选项的listbox
		var1 = tk.StringVar()
		self.sell_name_listbox = tk.Listbox(self.selltop, listvariable=var1, selectmode="browse")
		self.sell_name_listbox.grid(row=3, column=0, padx=1, pady=1)
		self.sell_name_listbox.bind("<<ListboxSelect>>", self.FuncSellComboxSelectedHander)
		# 货物数量输入框
		var2 = tk.StringVar()
		self.sell_number_entry = tk.Entry(self.selltop, textvariable=var2, width=8, validate='key',
										  validatecommand=(check_input_is_number_handler, '%P'))  # %P代表输入框的实时内容)
		self.sell_number_entry.grid(row=2, column=1, padx=1, pady=1)
		# 货物钱数输入框（单价or总价）
		var3 = tk.StringVar()
		self.sell_monery_entry = tk.Entry(self.selltop, textvariable=var3, width=8, validate='key',
										  validatecommand=(check_input_is_number_handler, '%P'))
		self.sell_monery_entry.grid(row=2, column=2, padx=1, pady=1)
		# 按钮
		self.sell_YesButton = tk.Button(self.selltop, text='确认', command=lambda: self.FuncButtonYes(self.selltop, 1))
		self.sell_YesButton.grid(row=3, column=1, padx=1, pady=1)
		self.sell_CancelButton = tk.Button(self.selltop, text='取消', command=lambda: self.FuncButtonCancel(self.selltop))
		self.sell_CancelButton.grid(row=3, column=2, padx=1, pady=1)

		# 右侧多条记录的界面
		# label
		tk.Label(self.selltop, text='货物名称').place(x=300, y=30, width=100, height=22)
		self.sell_mull_name_entry_var = tk.StringVar()
		self.sell_mull_name_entry = tk.Entry(self.selltop, textvariable=self.sell_mull_name_entry_var, validate='key',
											 validatecommand=(get_name_by_pinyin, '%P'))
		self.sell_mull_name_entry.place(x=298, y=55, width=120, height=22)

		tk.Label(self.selltop, text='货物数量').place(x=410, y=30, width=100, height=22)
		var_mull0 = tk.StringVar()
		self.sell_mull_number_entry = tk.Entry(self.selltop, textvariable=var_mull0, validate='key',
											   validatecommand=(check_input_is_number_handler, '%P'))
		self.sell_mull_number_entry.place(x=430, y=55, width=50, height=22)

		tk.Label(self.selltop, text='双击来删除对应条目', fg='red').place(x=570, y=30, width=160, height=22)

		tk.Label(self.selltop, text='总金额').place(x=400, y=85, width=100, height=22)
		var_mull3 = tk.StringVar()
		self.sell_mull_money_entry = tk.Entry(self.selltop, textvariable=var_mull3, validate='key',
											  validatecommand=(check_input_is_number_handler, '%P'))
		self.sell_mull_money_entry.place(x=430, y=110, width=50, height=22)

		# 添加功能按钮
		# 这个添加按钮是放在货物信息右面
		self.sell_mull_AddButtonOne = tk.Button(self.selltop, text='添加',
												command=lambda arg=1: self.FuncButtonSellMullAdd(arg))
		self.sell_mull_AddButtonOne.place(x=500, y=55, width=50, height=22)
		# 这个按钮是放在总金额的右面
		self.sell_mull_AddButtonTwo = tk.Button(self.selltop, text='添加',
												command=lambda arg=2: self.FuncButtonSellMullAdd(arg))
		self.sell_mull_AddButtonTwo.place(x=500, y=110, width=50, height=22)

		# 显示根据拼音显示出来的选项的listbox
		var_mull1 = tk.StringVar()
		self.sell_mull_name_listbox = tk.Listbox(self.selltop, listvariable=var_mull1, selectmode="browse")
		# self.sell_mull_name_listbox.grid(row=3, column=4, padx=1, pady=1)
		self.sell_mull_name_listbox.place(x=298, y=85, width=120, height=180)
		self.sell_mull_name_listbox.bind("<<ListboxSelect>>", self.FuncSellComboxSelectedHander)
		# 显示添加结果的列表的listbox
		var_mull2 = tk.StringVar()
		self.sell_mull_result_listbox = tk.Listbox(self.selltop, listvariable=var_mull2, selectmode="browse")
		self.sell_mull_result_listbox.place(x=580, y=55, width=140, height=200)
		self.sell_mull_result_listbox.bind("<Double-Button-1>", self.SellMullResultListboxDoubleClickFunc)

		# 确认按钮
		self.sell_mull_YesButton = tk.Button(self.selltop, text='确认',
											 command=lambda: self.FuncButtonYes(self.selltop, 3))
		self.sell_mull_YesButton.place(x=430, y=200, width=50, height=22)
		# 取消按钮
		self.sell_mull_CancelButton = tk.Button(self.selltop, text='取消',
												command=lambda: self.FuncButtonCancel(self.selltop))
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

	def FuncInput(self):
		# print 'input func'
		if self.child_screen_exits == True:
			# print 'child screen is exits'
			return

		self.child_screen_exits = True
		# 设置弹出窗口在主窗体的中间
		size = self.create_window_size(280, 80)
		inputtop = tk.Toplevel(self.root)
		inputtop.geometry(size)
		inputtop.resizable(width=False, height=False)
		# 设置右上角的X功能
		inputtop.protocol("WM_DELETE_WINDOW", lambda arg=inputtop: self.FuncButtonCancel(arg))
		# 设置窗口始终在最上层
		inputtop.wm_attributes("-topmost", 1)
		inputtop.title('入库信息输入框')
		# self.inputtop.overrideredirect(True)   #隐藏边框标题
		# self.inputtop.positionfrom(who="user")
		self.toplevel_id = inputtop
		# 单价or总价 切换标志
		self.sell_price_flag = False
		# label
		tk.Label(inputtop, text='货物名称').grid(row=1, column=0, padx=1, pady=1)
		tk.Label(inputtop, text='货物数量').grid(row=1, column=1, padx=1, pady=1)
		# 点击会自动切换显示的label
		self.sell_price_checkbutton_name = tk.StringVar()
		self.sell_price_checkbutton_name.set('单价')
		tk.Checkbutton(inputtop, textvariable=self.sell_price_checkbutton_name, command=self.SellCheckFunc).grid(
			row=1, column=2, padx=1, pady=1)
		# 对输入进行限制的函数
		check_input_is_number_handler = inputtop.register(self.check_input_is_number)
		check_input_is_not_number_and_speacil_handler = inputtop.register(self.check_input_is_not_number_and_speacil)
		# 货物名称输入框
		var1 = tk.StringVar()
		#self.input_name_entry = tk.Entry(self.inputtop, textvariable=var1, width=20)
		self.input_name_entry = tk.Entry(inputtop, textvariable=var1, width=20, validate='key',
											validatecommand=(check_input_is_not_number_and_speacil_handler, '%P'))
		self.input_name_entry.grid(row=2, column=0, padx=1, pady=1)
		# 货物数量输入框
		var2 = tk.StringVar()
		self.input_number_entry = tk.Entry(inputtop, textvariable=var2, width=8, validate='key',
										   validatecommand=(check_input_is_number_handler, '%P'))  # %P代表输入框的实时内容)
		self.input_number_entry.grid(row=2, column=1, padx=1, pady=1)
		# 货物钱数输入框（单价or总价）
		var3 = tk.StringVar()
		self.input_monery_entry = tk.Entry(inputtop, textvariable=var3, width=8, validate='key',
										   validatecommand=(check_input_is_number_handler, '%P'))
		self.input_monery_entry.grid(row=2, column=2, padx=1, pady=1)
		# 按钮
		tk.Button(inputtop, text='确认', command=lambda: self.FuncButtonYes(inputtop, 2)).grid(row=3, column=1,
																									   padx=1, pady=1)
		tk.Button(inputtop, text='取消', command=lambda: self.FuncButtonCancel(inputtop)).grid(row=3, column=2,
																									   padx=1, pady=1)

	def FuncTJDay(self):
		if self.child_screen_exits == True:
			return

		self.child_screen_exits = True
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
		print(size)
		self.child_screen_exits = False

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
		self.sell_button.place(x=20, y=30, width=180, height=120)
		self.input_button.place(x=20, y=160, width=180, height=120)
		self.tongji_day_button.place(x=20, y=290, width=180, height=120)
		self.tongji_month_button.place(x=20, y=420, width=180, height=120)

		display_start_x = 230
		display_start_y = 30
		# 两侧留出20空余空间
		display_width = self.RootWidth - display_start_x - 40;
		# 底部留出200空余空间
		display_height = self.RootHeight - 200 * 3 / 4 - 40;
		self.display_info.place(x=display_start_x, y=display_start_y, width=display_width, height=display_height)

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


def main():
	# 初始化对象
	LoggingConsumer()
	FL = FindLocation()
	# 进行布局
	FL.gui_arrang()
	# 主程序执行
	tk.mainloop()
	pass

if __name__ == "__main__":
	main()
