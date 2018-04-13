from TacticsEngine import TacticsEngine

# 第三方库

class Tactics(TacticsEngine):
    name = 'BankStock'
    def init(self):

        self.parm = {}
        self.parm['差值'] = 0.005
        times = self.ue.getActionData('times')
        self.parm['次数'] = 0 if times == None else int(times)
        self.stockList = ['601398', '601288','601939','601988']
        self.history = {}

        self.uc.par['set'][self.name] = self.parm
        # self.uc.par['run'][self.name] = self.fun

        self.getYesterdayClose()

    def tactics(self, data):
        raito = []
        for code in self.stockList:
            if data.get(code) is None: return
            raito.append(data[code]['now'] / self.history[code])

        if len(self.stockList) != len(raito) != len(self.history): return

        for code,val in self.stockPool.items():
            now = data.get(code).get('now') if data.get(code) is not None else 0
            if now is None or now <= 0 or val['count'] <= 0 : continue

            if now > val['high']: self.stockPool[code]['high'] = now

            if now < val['low']: self.stockPool[code]['low'] = now

        if self.parm['次数'] == 1: return

        realStock = [code for code, val in self.stockPool.items() if val['count'] > 0]

        if len(realStock) > 0:
            code = realStock[0]

            index = self.stockList.index(code)
            # print(self.name,code,index,raito[index],min(raito))
            if raito[index] - min(raito) > self.parm['差值']:
                # print('1',raito[index],min(raito),self.stockList[raito.index(min(raito))])
                self.order('sell',code,self.stockPool[code]['count'])
                index = raito.index(min(raito))
                realCash = self.uc.fundPool['employ'] * (1-self.brokerage)
                self.order('buy', self.stockList[index], realCash)
                self.parm['次数'] = 1
                self.ue.recordActionData('times',1)
        else:
            if max(raito) - min(raito) > self.parm['差值']:
                # print('0',max(raito),min(raito),self.stockList[raito.index(min(raito))])
                index = raito.index(min(raito))
                realCash = self.uc.fundPool['employ'] * (1-self.brokerage)
                self.order('buy', self.stockList[index], realCash)
                self.parm['次数'] = 1
                self.ue.recordActionData('times',1)

    def market(self, data):
        # 开盘前的准备工作,8.30运行
        if data.clockEvent == 'before':
            self.getYesterdayClose()
            self.parm['次数'] = 0
            self.ue.recordActionData('times', 0)

    def getYesterdayClose(self):

        # print(self.stockList)
        for code in self.stockList:
            history = self.de.getHistData(code,['close'],1)
            self.history[code] = history.close.values[-1]
            if code in self.stockPool.keys():
                self.stockPool[code].pop('control')
                self.stockPool[code]['preClose'] = history.close.values[-1]

