#!/usr/bin/python3
#--coding:utf-8--


import datetime
import time
import urllib.request

from Helpers.HoliDay import HoliDay

def nowTimeStamp():
    return time.time() * 1000

# 判断是否为周末
def isWeekEnd(day):
    # 判断是否为周末 星期六为5星期天为6 周末返回真否则为假
    return day.weekday() >= 5

# 在线判断是否为假日
def isHoliDayByNet(day):
    # 0为工作日，2为假日 1为休息日
    day = day.strftime('%Y%m%d')
    url = 'http://apis.baidu.com/xiaogg/holiday/holiday?d='+day
    req = urllib.request.Request(url)
    req.add_header("apikey", "f4508323639740523c6f69d88ed00904")
    resp = urllib.request.urlopen(req)
    result = resp.read().decode('utf-8')
    return False if result == '0' else True

def isHoliDay(day):
    return day.strftime('%Y-%m-%d') in HoliDay

# 判断是否为交易日
def isTradeDay(day):
    return not isWeekEnd(day) and not isHoliDay(day)

# 判断是否为交易时间
def isTradeTime(day):
    OPEN_TIME = (
        (datetime.time(9, 15, 0), datetime.time(11, 30, 0)),
        (datetime.time(13, 0, 0), datetime.time(15, 0, 0)),
    )
    now = day.time()
    for begin, end in OPEN_TIME:
        if begin <= now < end:
            return True
    else:
        return False


# 获取下一个交易日期
def getNextTradeDate(day):
    now = day
    max_days = 30
    days = 0
    while 1:
        days += 1
        now += datetime.timedelta(days=1)
        if isTradeDay(now):
            if isinstance(now, datetime.date):
                return now
            else:
                return now.date()
        if days > max_days:
            raise ValueError('无法确定 %s 下一个交易日' % day)

