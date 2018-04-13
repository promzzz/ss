#!/usr/bin/python3
#--coding:utf-8--
import json
import os
import re

import urllib.request
import requests

import struct
import time
import datetime
from pandas.compat import StringIO
import pandas as pd

# 散户之家的代码列表
def get_stock_codes():
    url = 'http://www.shdjt.com/js/lib/astock.js'
    grep_stock_codes = re.compile('~(\d+)`')
    response = requests.get(url)
    stock_codes = grep_stock_codes.findall(response.text)
    return stock_codes

def get_all_codes():
    url = 'http://www.shdjt.com/js/lib/astock.js'
    string = urllib.request.urlopen(url).read()
    lists = string.decode('utf8').split('=')[1].replace('"', '').split('~')

    stocks = {}
    funds = {}
    exponent = {}
    classify = {}
    for i in lists:
        codes = i.split('`')
        if codes[0][:2] in ['00','30','60']:
            stocks[codes[0]] = {'code':codes[0],
                                'type':'stock',
                                'market':'sh' if codes[0][:1] == '6' else 'sz',
                                'name':codes[1]
                                }
        # elif codes[0][:2] in ['20','90']:
        #     stocks[codes[0]] = {'code':codes[0],
        #                         'type':'stock_B',
        #                         'market':'sh' if codes[0][:1] == '9' else 'sz',
        #                         'name':codes[1]
        #                         }
        elif codes[0][:2] in ['sh','39']:
            code = codes[0][2:] if len(codes[0]) > 6 else codes[0]
            exponent[code] = {'code':code,
                                'type':'exponent',
                                'market':'sh' if code[:1] == '0' else 'sz',
                                'name':codes[1].split('.')[0]
                                }
        # elif codes[0][:1] in ['1','5']:
        #     funds[codes[0]] = {'code':codes[0],
        #                         'type':'fund',
        #                         'market':'sh' if codes[0][:1] == '5' else 'sz',
        #                         'name':codes[1].split('.')[0]
        #                         }
        # elif codes[0][:2] == '99':
        #     classify[codes[0]] = {'code':codes[0],
        #                           'type':'classify',
        #                           'name':codes[1].split('.')[0]
        #                         }
    return stocks,exponent

# 从tushare里得到的股票列表
def get_code_list():
    request = urllib.request.Request('http://218.244.146.57/static/all.csv')
    text = urllib.request.urlopen(request, timeout=10).read()
    text = text.decode('GBK')
    text = text.replace('--', '')
    df = pd.read_csv(StringIO(text), dtype={'code':'object'})
    df = df.set_index('code')
    return df

def perfectCode(code):
    """判断股票ID对应的证券市场
    匹配规则
    ['50', '51', '60', '90', '110'] 为 sh
    ['00', '13', '18', '15', '16', '18', '20', '30', '39', '115'] 为 sz
    ['5', '6', '9'] 开头的为 sh， 其余为 sz
    :param stock_code:股票ID, 若以 'sz', 'sh' 开头直接返回对应类型，否则使用内置规则判断
    :return 'sh' or 'sz'"""
    assert type(code) is str, 'stock code need str type'
    if code.startswith(('sh', 'sz')):
        return code[:2]
    if code.startswith(('50', '51', '60', '73', '90', '110', '113', '132', '204', '78')):
        return 'sh'
    if code.startswith(('00', '13', '18', '15', '16', '18', '20', '30', '39', '115', '1318')):
        return 'sz'
    if code.startswith(('5', '6', '9')):
        return 'sh'
    return 'sz'
