#!/usr/bin/env python
#-*- coding:utf-8 -*-

from Tkinter import *
import pygeoip

#主窗口
root = Tk()
#标题
root.title("Main Title")
#创建一个输入框，设置尺寸
ip_input = Entry(root, width=30)
#创建回显列表
display_info = Listbox(root, width=50)

def find_position():
    gi = pygeoip.GeoIP("./GeoLiteCity-data/GeoLiteCity.dat")
    ip_addr = ip_input.get()
    aim = gi.record_by_name(ip_addr)
    try:
        city = aim["city"]
        country = aim["country_name"]
        region_code = aim["region_code"]
        longitude = aim["longitude"]
        latitude = aim["latitude"]
    except:
        pass

    the_ip_info = ["所在纬度:"+str(latitude),"所在经度:"+str(longitude),"地域代号:"+str(region_code),"所在城市:"+str(city),"所在国家或地区:"+str(country),"需要查询的ip:"+str(ip_addr)]
    for item in range(10):
        display_info.insert(0,"")
    for item in the_ip_info:
        display_info.insert(0, item)

#创建按钮
result_button = Button(root, command=find_position, text="search")


li = ['C','Python','php','html','sql']
movie = ['css','jQuery','bootstrap']
listb = Listbox(root)
listb2 = Listbox(root)
for item in li:
    listb.insert(0, item)
for item in movie:
    listb2.insert(0, item)

ip_input.pack()
display_info.pack()
result_button.pack()
listb.pack()
listb2.pack()

root.mainloop()
