from TacticsEngine import TacticsEngine

# 第三方库
import pandas
import numpy
import json

import datetime
from dateutil import tz

class Tactics(TacticsEngine):
    name = 'antLevel'
    def init(self):

        self.parm = {
            'level':10,
            'threshold':0.02,
            'jump':500,
            'stocknum':300,
            'history':130
            }

        dc = self.ue.getActionData('level')
        self.c = json.loads(dc) if dc is not None else {'level':[], 'run':{}}
        self.level = self.c.get('level')
        self.runs = self.c.get('run')


    def tactics(self, data):
        if len(self.stockPool) > 0:
            # 如果数据里没有这一条也不用比对啦
            code = list(self.stockPool.keys())[0]
            if data.get(code) is None or data.get(code).get('now') <= 0: return

            now = data.get(code).get('now')
            stock = self.stockPool.get(code)

            if now > stock['high']:
                stock['high'] = now
                self.ue.recordStockPool('update',code,price=[now,0])

            if now < stock['low']:
                stock['low'] = now
                self.ue.recordStockPool('update',code,price=[0,now])

            level = self.level[self.runs['level']]
            if level[1] * (1+self.parm['threshold']) <= now:

                index = self.runs['grade'] - self.runs['level']

                if self.runs['employ'] >= self.level[index][2]:
                    self.order('sell', code, self.level[index][2])

                    if self.runs['level'] < 1:
                        self.level = []
                        self.runs = {}
                    else:
                        self.runs['level'] -= 1
                        self.runs['employ'] -= self.level[index][2]

            if level[1] * (1-self.parm['threshold']) >= now:
                if self.runs['level'] >= 9: return

                if self.runs['level'] < self.runs['grade']:
                    index = self.runs['grade'] - self.runs['level'] - 1
                    if self.fundPool['employ'] < now*self.level[index][2]*1.0014: return
                    self.order('buy', code, now*self.level[index][2])
                    self.runs['level'] += 1
                else:
                    if self.fundPool['employ'] < now*self.level[self.runs['level']+1][2]*1.0014: return
                    self.runs['level'] += 1
                    self.runs['grade'] += 1
                    self.order('buy', code, now*self.level[self.runs['level']][2])

            self.ue.recordActionData('level', json.dumps(self.c))

    def market(self, data):
        # 开盘前的准备工作,8.30运行
        if data.clockEvent == 'before':
            code = list(self.stockPool.keys())[0]
            self.runs['employ'] = self.stockPool[code]['count']
        if data.clockEvent == 'buyStock' and len(self.stockPool) == 0:
             # 空仓 比对时间 有选票 只有买
            code = self.selectStock()

            price = data.get(code).get('now')
            count = self.parm['jump']

            self.order('buy', code, price*count)

            for i in range(self.parm['level']):
                self.level.append((i, price, count))
                price = round(price*(1-self.parm['threshold']), 2)
                count = (i+2)*self.parm['jump']
            self.runs['level'] = 0    # 当前运行的级别
            self.runs['grade'] = 0    # 策略运行到的最高级别
            self.runs['employ'] = 0   # 当前可卖的数量
            self.ue.recordActionData('level', json.dumps(self.c))


    def selectStock(self):
        oneYearAgo = datetime.date.today() - datetime.timedelta(days=365)
        where = ["`code` NOT LIKE '300%'",
                 "`name` NOT LIKE 'ST%'",
                 "`name` NOT LIKE '*%'",
                 "`eps` > 0",
                 "`md` < '%s'" % oneYearAgo]
        sorce ={}
        stocks = self.de.getStockBaseInfo(where,['`mv` ASC'],self.parm['stocknum'])

        for code in stocks.index.values:
            h = self.de.getHistData(code,['open','close','high','low'],self.parm['history'])
            h.insert(0, 'extent', (h.high-h.low)/h.close)
            mean = h.extent.mean()
            high = h[h.extent > mean]
            low = h[h.extent < mean]
            if len(high) > len(low):
                sorce[code] = mean

        stocks = pandas.DataFrame(list(sorce.values()),index = sorce.keys())
        stocks.columns = ['score']
        stocks = stocks.sort_values(by='score',ascending=False)

        real = self.de.getRealtimeData(stocks.index.values)
        for code in stocks.index.values:
            stock = real.get(code)
            if stock['now'] > 0 and stock['now'] <= stock['close']*1.097:
                return code