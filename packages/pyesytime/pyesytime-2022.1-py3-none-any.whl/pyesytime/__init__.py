#!/usr/bin/python3
# -*- coding: utf-8 -*- 

#Version 2022.1
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

def HOUR_MINUTE_SECOND_12_COLON():
	nowTime = datetime.datetime.now()
	now = str(nowTime)[13:19]
	if nowTime.hour > 12:
		now = str(nowTime.hour-12) + now + " pm"
	elif nowTime.hour == 12:
		now = str(nowTime.hour) + now + " pm"
	else:
		now = str(nowTime.hour) + now + " am"
	return now

def ONLY_HOUR_24():
	return datetime.datetime.now().hour

def ONLY_HOUR_12():
	hour = datetime.datetime.now().hour
	if hour >= 12:
		return str(hour-12)+" pm"
	else:
		return str(hour)+" am"

if __name__ == "__main__":
	print("请将EasyTime作为模块使用，谢谢")
	exit()