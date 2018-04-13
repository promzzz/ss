from DataEngine import DataEngine
from UserEngine import UserEngine
from QuotationEngine import QuotationEngine
from ClockEngine import ClockEngine
from setting import user,system

# 第三方库
import pandas
import numpy

from datetime import *
from dateutil import tz

# 手动运行买卖脚本

user = user[0]

name = 'smallvalue'

DE = DataEngine()
UE = UserEngine(user, name)

# days = int(UE.getActionData('days'))
days = 1
fundPool = UE.getAccountInfo()
stockPool = UE.getStockPool()


def order(mode, code, number):
    now = DE.getRealtimeData(code)
    now = now.get(code)

    if now is None or now['now'] == 0: return
    print('执行的动作',mode,code)
    if mode == 'buy':
        count = number // now['now'] // 100 * 100
        if count > 0:
            print('购买前余额',fundPool['employ'])
            fundPool['employ'] -= now['now'] * count * (1 + user['brokerage'])
            print('购买后余额',fundPool['employ'])

            if code in stockPool.keys():
                stockPool[code]['count'] += count
            else:
                stockPool[code] = dict(count = count)
        # print(code,count,now['now'] * count * (1 + user['brokerage']))
    else:
        count = number
        fundPool['employ'] += now['now'] * count * (1-user['brokerage']-user['stamptax'])
        stockPool[code]['count'] -= count

    if count > 0:
        # pass
        # 数据库操作买卖记录
        UE.recordTransaction(mode,code,now['name'],now['now'],count)
            # 更新股票池
        UE.recordStockPool(mode,code,now['name'],now['now'],count)
            # 记录账户信息
        UE.recordAccountInfo(fundPool)

s = datetime.now()

oneYearAgo = date.today() - timedelta(days=365)
where = ["code NOT LIKE '300%'",
         "name NOT LIKE 'ST%'",
         "name NOT LIKE '*%'",
         "eps > 0",
         "md < '%s'" % oneYearAgo]
stocks = DE.getStockBaseInfo(where,['mv ASC'],100)

codes = set(list(stocks.index.values)+list(stockPool.keys()))

print(codes)

realData = DE.getRealtimeData(codes)

ss = {}
bl = []
for code,val in realData.items():

    if val['now'] == 0 or val['open'] == 0 or val['high'] == 0 or val['low'] == 0: continue

    if val['close'] * 0.90 < val['now'] < val['close'] * 1.0998:
        h = DE.getHistData(code,['high','close','low'],130)
        ss[code] = val['now']*3 - h.high.max() - h.low.min() - h.close.values[:15].mean()

    if code in stockPool.keys():
        if val['now'] >= val['close'] * 1.0998: bl.append(code)

        if val['now'] >= val['close'] * 1.0998:
            h = DE.getHistData(code,['high','close','low'],130)
            ss[code] = val['now']*3 - h.high.max() - h.low.min() - h.close.values[:15].mean()


stocks = pandas.DataFrame(list(ss.values()),index = ss.keys())
stocks.columns = ['score']
stocks = stocks.sort_values(by='score',ascending=True)
stockList = stocks.index.values[:4]


# 卖出不在筛选列表中的票 但需保留涨停的票
for code, val in stockPool.items():
    if code not in stockList and code not in bl: order('sell',code,val['count'])

# 计算每只票可用金额
trueStock = [code for code,val in stockPool.items() if val['count'] > 0 ]

print('需要购买的：',stockList)
print('目前持仓的：',stockPool.keys())
# print(trueStock)
# 需要进仓数量
addStock = 4-len(trueStock)

if addStock > 0:
    trusCash = fundPool['employ'] * (1-user['brokerage'])
    stockCash = trusCash / addStock

    # 买入不在仓的票
    ns = 0
    for code in stockList:
        if code not in trueStock:
            ns += 1
            order('buy', code, stockCash)
            if ns == addStock: break

print(stockPool)
days += 1
UE.recordActionData('days',days)


e = datetime.now()

print(e-s)
