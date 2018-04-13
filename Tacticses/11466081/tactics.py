from TacticsEngine import TacticsEngine
import time

# 第三方库

class Tactics(TacticsEngine):
    name = 'BankStock'
    def init(self):

        self.parm = {}
        self.parm['差值'] = 0.005
        self.parm['次数'] = int(self.ue.getActionData('times'))
        self.stockList = ['601398', '601288','601939','601988']
        self.history = {}

        self.isOrder = True

        self.getYesterdayClose()

    def tactics(self, data):
        raito = []
        for code in self.stockList:
            if data.get(code) is None: continue
            raito.append(data[code]['now'] / self.history[code])

        stockPool = list(self.stockPool.keys())

        for code in stockPool:
            now = data.get(code)
            stock = self.stockPool.get(code)
            if now is None or stock is None or now['now'] <= 0 or stock['count'] <= 0: continue

            if now['now'] > stock['high']:
                stock['high'] = now['now']
                self.de.recordStockPool(self.name,'update',code,price=[now['now'],0])

            if now['now'] < stock['low']:
                stock['low'] = now['now']
                self.de.recordStockPool(self.name,'update',code,price=[0,now['now']])

        if self.parm['次数'] == 1: return
        
        realStock = [code for code, val in self.stockPool.items() if val['count'] > 0]

        if len(realStock) > 0:
            code = realStock[0]
            index = self.stockList.index(code)
            if raito[index] - min(raito) > self.parm['差值'] and self.isOrder:
                self.isOrder = False
                self.order('sell',code,self.stockPool[code]['count'])
                result = self.ConfirmOrder(code)
                if result == True:
                    self.isOrder = True
        else:
            if max(raito) - min(raito) > self.parm['差值'] and self.isOrder:
                self.isOrder = False
                index = raito.index(min(raito))
                realCash = self.EE.fundPool['employ'] * (1-self.brokerage)
                self.order('buy', self.stockList[index], realCash)
                self.parm['次数'] = 1
                self.ue.recordActionData(self.name,'times',1)
                self.isOrder = True

    def market(self, data):
        # 开盘前的准备工作,8.30运行
        if data.clockEvent == 'before':
            self.getYesterdayClose()
            self.parm['次数'] = 0
            self.ue.recordActionData(self.name,'times',0)
			
    def getYesterdayClose(self):
        for code in self.stockList:
            history = self.de.getHistData(code,['close'],1)
            self.history[code] = history.close.values[-1]

    def ConfirmOrder(self,code):
        while True:
            if code in self.revEntrust:
                # self.SW.updateLogLable.emit('等待一秒钟，查看订单%s是否成交' % code)
                time.sleep(1)
            else:
                return True
                break

    @property
    def revEntrust(self):
        stockList = self.te.revocableEntrust()
        stockList = [i.get('stkcode') for i in stockList]
        return stockList

    def _synchroInfo(self):
        if self.mode and self.EE.userStatus:
            self.stockPool = self.de.getStockPool(self.name)
            # # 重新获取账户信息
            self.EE.fundPool['employ'] = self.TE.fundPool['employ']
            # # 同步账户信息
            self.de.recordAccountInfo(self.EE.fundPool)

            stockList = self.TE.stockPool
            # 同步账户策略股票池
            for code, val in stockList.items():
                if float(val['buycost']) == 0: continue
                # print(val)
                price = float(val['buycost']) * (1 - self.brokerage) / float(val['stkqty'])
                # print(price)
                if code in self.stockPool.keys():
                    self.de.recordStockPool(self.name,'synchro',code,val['stkname'],price,val['stkqty'])
                else:
                    self.de.recordStockPool(self.name,'buy',code,val['stkname'],price,val['stkqty'])
            
            # print(self.stockPool)
            for code, val in self.stockPool.items():
                if code not in stockList.keys():
                    self.de.recordStockPool(self.name,'sell',code,val['name'],val['price'],val['count'])

