#!/usr/bin/python3
# -*- coding: utf-8 -*- 

#Version 2022.2
#Author:SunnyLi
import datetime,time,os,sys

def ALL_IN_ONE():
	return str(datetime.datetime.now())[:19]

def YEAR_MONTH_DAY_LINE():
	now = str(datetime.datetime.now())[:19]
	return now[:10]

def YEAR_MONTH_DAY_DIAGONAL():
	now = str(datetime.datetime.now())[:19].replace('-','/')
	return now[:10]

def HOUR_MINUTE_SECOND_24_COLON():
	now = str(datetime.datetime.now())[11:19]
	return now

def HOUR_MINUTE_SECOND_12_COLON_ENGLISH():
	nowTime = datetime.datetime.now()
	now = str(nowTime)[13:19]
	if nowTime.hour > 12:
		now = str(nowTime.hour-12) + now + " pm"
	elif nowTime.hour == 12:
		now = str(nowTime.hour) + now + " pm"
	else:
		now = str(nowTime.hour) + now + " am"
	return now

def HOUR_MINUTE_SECOND_12_COLON_CHINESE():
	nowTime = datetime.datetime.now()
	now = str(nowTime)[13:19]
	if nowTime.hour > 12:
		now = "下午 "+str(nowTime.hour-12) + now
	elif nowTime.hour == 12:
		now = "下午 "+str(nowTime.hour) + now
	else:
		now = "上午 "+str(nowTime.hour) + now
	return now

def ONLY_HOUR_24():
	return datetime.datetime.now().hour

def ONLY_HOUR_12_ENGLISH():
	hour = datetime.datetime.now().hour
	if hour >= 12:
		return str(hour-12)+" pm"
	else:
		return str(hour)+" am"

def ONLY_HOUR_12_CHINESE():
	hour = datetime.datetime.now().hour
	if hour >= 12:
		return "下午"+str(hour-12)+"时"
	else:
		return "上午"+str(hour)+"时"

if __name__ == "__main__":
	print("请将EasyTime作为模块使用，谢谢")
	exit()