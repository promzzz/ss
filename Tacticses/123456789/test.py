from TacticsEngine import TacticsEngine

# 第三方库
import pandas
import numpy

import datetime
from dateutil import tz

class Tactics(TacticsEngine):
    name = 'smallvalue'
    def init(self):
        # 注册时钟事件
        clock_type = "buyStock"
        moment = datetime.time(14, 50, tzinfo=tz.tzlocal())
        self.ce.register_moment(clock_type, moment)

        self.par = {}
        self.par['轮动间隔'] = 3
        self.par['个股历史'] = 130
        self.par['指数比对'] = 20
        self.par['盈损历史'] = 250
        self.par['预选数目'] = 100
        self.par['持仓数量'] = 4
        days = self.ue.getActionData('days')
        days = 0 if days == None else int(days)
        self.fun = {'轮动时间':days}

        self.uc.par['set'][self.name] = self.par
        self.uc.par['run'][self.name] = self.fun

        self.stopLossProfit()

    def tactics(self, data):
        stockList = list(self.stockPool.keys())

        for code in stockList:

            if data.get(code) is None or self.stockPool.get(code) is None: continue

            now = data.get(code).get('now')
            stock = self.stockPool.get(code)

            if now <= 0 or stock['count'] <= 0: continue

            if now > stock['high']: stock['high'] = now

            if now < stock['low']: stock['low'] = now

            if now <= (1-stock['loss']) * stock['high']:
                self.order('sell', code, stock['count'])
                logStr = '[%s] %s 已超过%.2f的止损设定，进行个股止损' % (code, stock['name'], stock['loss'])
                self.message(logStr)
                self.fun['轮动时间'] = 0
                self.ue.recordActionData('days',0)

            if now >= (1+stock['profit']) * stock['price']:
                self.order('sell', code, stock['count'])
                logStr = '[%s] %s 已达到%.2f的止盈设定，进行个股止盈' % (code, stock['name'], stock['profit'])
                self.message(logStr)
                self.fun['轮动时间'] = 0
                self.ue.recordActionData('days',0)


    def market(self, data):
        # 开盘前的准备工作,8.30运行
        if data.clockEvent == 'before':
            self.stopLossProfit()

        # 下午休盘之后事件，虽然在账户策略里，但这动作属于系统动作，只是此动作只需运行一次
        if data.clockEvent == 'after':
            # 更新行情引擎代码库
            stock = self.de.getStockBaseInfo()
            self.qe.codes = list(stock.index.values)

        # 策略自定义的时钟事件
        if data.clockEvent == 'buyStock':

            self.message('已到买股时间，程序将进行指数判断是否达到购买条件')

            zxbz_20 = self.de.getHistData('sz399005',['close'], self.par['指数比对'])
            sz50_20 = self.de.getHistData('sh000016',['close'], self.par['指数比对'])

            now = self.de.getRealtimeData(['sh000016','sz399005'])
            sz50 = now.get('000016').get('now')
            zxbz = now.get('399005').get('now')

            if sz50 < 1.01 * sz50_20.close.values[-1] and zxbz < 1.01 * zxbz_20.close.values[-1]:
                self.message('指数参考未达到买股标准，如有在仓股票将全部清仓')
                self.sell()
            else:
                self.message('指数达到买股标准，程序进入选股阶段')
                self.buy()

    def stopLossProfit(self):
        for code, value in self.stockPool.items():
            history = self.de.getHistData(code,['close'],length=self.par['盈损历史'])
            change = history['close'].pct_change(3)
            maxd = change.min()
            maxr = change.max()
            avgd = change.mean()
            bstd = (maxd + avgd) / 2
            value['profit'] = round(abs(maxr), 2) if (not numpy.isnan(maxr)) and maxr != 0 else 0.20
            if not numpy.isnan(bstd):
                if bstd != 0:
                    value['loss'] = round(abs(bstd), 2)
                else:
                    if maxd < 0:
                        value['loss'] = round(abs(maxd), 2)
            else:
                value['loss'] = 0.099

    def selectStock(self):
        oneYearAgo = datetime.date.today() - datetime.timedelta(days=365)
        where = ["code NOT LIKE '300%'",
                 "name NOT LIKE 'ST%'",
                 "name NOT LIKE '*%'",
                 "eps > 0",
                 "md < '%s'" % oneYearAgo]
        stocks = self.de.getStockBaseInfo(where,['mv ASC'],self.par['预选数目'])
        codes = set(list(stocks.index.values)+list(self.stockPool.keys()))
        # print(codes)
        realData = self.de.getRealtimeData(codes)

        stocks = {}
        retain = []
        for code,val in realData.items():
            if val['now'] == 0 or val['open'] == 0 or val['high'] == 0 or val['low'] == 0: continue

            if val['close'] * 0.90 < val['now'] < val['close'] * 1.0998:
                h = self.de.getHistData(code,['high','close','low'],130)
                stocks[code] = val['now']*3 - h.high.max() - h.low.min() - h.close.values[:15].mean()

            if code in self.stockPool.keys() and val['now'] >= val['close'] * 1.0998: retain.append(code)

        stocks = pandas.DataFrame(list(stocks.values()),index = stocks.keys())
        stocks.columns = ['score']
        stocks = stocks.sort_values(by='score',ascending=True)
        return stocks.index.values[:self.par['持仓数量']], retain

    def buy(self):
        if self.fun['轮动时间'] % self.par['轮动间隔'] == 0:

            self.message('满足三天持仓时间，开始选股，准备买卖股票')

            stockList, retain= self.selectStock() # 选取持仓代码以及保留票

            self.message('选股完成，开始循环比对买卖股票')

            # 卖出不在筛选列表中的票, 保留涨停的票
            
            stockPool = list(self.stockPool.keys())
            for code in stockPool:
                if code not in stockList and code not in retain:
                    self.order('sell', code, self.stockPool[code]['count'])

            buyCount = self.par['持仓数量'] - len(self.stockPool) # 购买数量

            if buyCount > 0:

                trusCash = self.uc.fundPool['employ'] * (1-self.brokerage) # 实际金额
                stockCash = trusCash / buyCount

                # 买入不在仓的票
                for code in stockList:
                    if code not in self.stockPool.keys(): self.order('buy',code,stockCash)
                    if len(self.stockPool) == self.par['持仓数量']: break
        else:
            self.message('未满足三天持仓时间，将忽略选股程序')

        self.fun['轮动时间'] += 1
        self.ue.recordActionData('days',self.fun['轮动时间'])

    def sell(self):
        stockPool = list(self.stockPool.keys())
        for code in stockPool: self.order('sell', code, self.stockPool[code]['count'])
        self.fun['轮动时间'] = 0
        self.ue.recordActionData('days',0)

