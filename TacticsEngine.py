# coding:utf-8
import sys
import traceback
import dill
import time

from UserEngine import UserEngine
from setting import system

ACCOUNT_OBJECT_FILE = 'account.session'


class TacticsEngine:
    name = 'TacticsTemplate'

    def __init__(self, UserCenter, traderEngine, dataEngine, clockEngine, quotationEngine, SubInterface):

        # 引用用户中心
        self.uc = UserCenter
        # 引用数据引擎
        self.de = dataEngine
        # 引用下单引擎
        self.te = traderEngine
        # 引用时钟引擎
        self.ce = clockEngine
        # 引用行情引擎
        self.qe = quotationEngine
        # 引用界面引擎
        self.message = SubInterface.showMessage.emit
        # 实例用户引擎
        self.ue = UserEngine(self.uc.info, self.name)
        self.ta = '%s_%s' % (self.uc.info['userid'], self.name)

        self.brokerage = self.uc.info['brokerage'] # 手续费
        self.stamptax = self.uc.info['stamptax'] # 印花税
        self.mode = self.uc.info['mode'] # 实盘或模拟盘

        self._synchroInfo()
        self.__reLoadInfo()

        self.init()

    def init(self):
        # 进行相关的初始化操作
        pass

    def __tactics(self, event):

        self.__calculation(event)
        self.tactics(event)

    def __calculation(self,event):

        ttl = tpl = 0

        for code,val in self.stockPool.items():
            now = event.get(code).get('now') if event.get(code) is not None else 0
            if now is None or now == 0 or val['count'] == 0 : continue
            val['now'] = now
            val['worth'] = now * val['count']
            val['P&L'] = val['worth'] * (1-self.brokerage-self.stamptax) - val['total']*(self.brokerage+1)

            ttl += val['worth']
            tpl += val['P&L']

        # 赋值策略总盈亏
        self.uc.tpl[self.ta] = tpl
        # 赋值策略总价值
        self.uc.ttl[self.ta] = ttl
        # 赋值策略股票池
        self.uc.tsp[self.ta] = self.stockPool

    def tactics(self, event):
        pass

    def run(self, event):
        try:
            self.__tactics(event)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.message(repr(traceback.format_exception(exc_type,
                                                         exc_value,
                                                         exc_traceback)))

    def clock(self, event):
        # 开盘前的准备工作,8.30运行
        if event.clockEvent == 'before':
            # 重新载入用户信息
            self.__reLoadInfo()

        self.market(event)

    def market(self,data):
        pass

    def log_handler(self):
        """
        优先使用在此自定义 log 句柄, 否则返回None, 并使用主引擎日志句柄
        :return: log_handler or None
        """
        return None

    def shutdown(self):
        """
        关闭进程前调用该函数
        :return:
        """
        pass

    # 同步券商账户与数据库之间所有信息
    def _synchroInfo(self):
        pass

    # 重新载入用户信息
    def __reLoadInfo(self):
        # 赋予用户中心资金池
        self.uc.fundPool = self.ue.getAccountInfo()
        # 获取账户策略股票池
        self.uc.tsp[self.ta] = self.stockPool = self.ue.getStockPool()


    def order(self, mode, code, number):
        now = self.de.getRealtimeData(code)
        now = now.get(code)
        if mode == 'buy':
            count = int(number // now['now'] // 100 * 100)
            if count < 100: return

            # 如果卖一价比当前价高出两分钱以上，那么设定价格为当前价加一分钱，否则价格为卖一价

            price = now['now'] + 0.01 if now['sell'] - now['now'] > 0.01 else now['sell']
            self.uc.fundPool['employ'] -= price * count * (1 + self.brokerage)
                
            if self.mode:
                # 账号操作买入动作
                result = self.te.buyStock(code,price,count)
                self.message('订单状态：%s' % result['result'])


            if code in self.stockPool.keys():
                if self.stockPool[code]['count'] <= 0:
                    self.stockPool[code]['price'] = price
                    self.stockPool[code]['high'] = price
                    self.stockPool[code]['low'] = price
                self.stockPool[code]['count'] += count
            else:
                self.stockPool[code] = dict()
                self.stockPool[code]['name'] = now['name']
                self.stockPool[code]['code'] = code
                self.stockPool[code]['count'] = count
                self.stockPool[code]['total'] = count * price
                self.stockPool[code]['price'] = price
                self.stockPool[code]['high'] = price
                self.stockPool[code]['low'] = price
                self.stockPool[code]['now'] = price
                self.stockPool[code]['profit'] = 1
                self.stockPool[code]['loss'] = 1
                self.stockPool[code]['worth'] = 0
                self.stockPool[code]['P&L'] = 0
                self.stockPool[code]['control'] = ''

            self.message('买入股票 [%s] %s 价格: %.2f 数量: %s' % (code,now['name'],price,count))
        else:
            count = int(number)

            price = now['now'] - 0.01 if now['now'] - now['buy'] > 0.01 else now['buy']
            self.uc.fundPool['employ'] += price * count * (1-self.brokerage-self.stamptax)
            
            if self.mode:
                # 账号操作卖出动作
                result = self.te.sellStock(code, price, count)
                self.message('订单状态：%s' % result['result'])

            if count >= self.stockPool[code]['count']:
                self.stockPool.pop(code)
            else:
                self.stockPool[code]['count'] -= count
            self.message('卖出股票 [%s] %s 价格: %.2f 数量: %s' % (code,now['name'],price,count))

        if count > 0:
            # 数据库操作买卖记录
            self.ue.recordTransaction(mode,code,now['name'],price,count)
            # 更新股票池
            self.ue.recordStockPool(mode,code,now['name'],price,count)
            # 记录账户信息
            self.ue.recordAccountInfo(self.uc.fundPool)