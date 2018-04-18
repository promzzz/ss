# coding:utf-8

# 系统自带包
from datetime import *
import time
import multiprocessing
import os,sys

# 第三方扩展包
import pandas
import json
import copy

# 自定义包
from Database.MySQL import MySQL
from Database.PostgreSQL import PostgreSQL
from Helpers.RelatedTool import *

from setting import DBInfo,system

DB,DBSet = (MySQL,True) if system['database'] == 'MySQL' else (PostgreSQL,False)

class UserCenter(object):
    """docstring for UserCenter"""
    def __init__(self, info):
        self.info = info
        self.message = ''
        self.fundPool = dict(
                total = 0.0,     # 总资产
                surplus = 0.0,   # 资金余额
                employ = 0.0,    # 可用余额
                free = 0.0,      # 可取余额
                freeze = 0.0,    # 冻结金额
                stockvalue = 0.0,# 股票市值
            )
        self.tpl = {} # 策略盈亏字典
        self.ttl = {} # 策略价值总额
        self.tsp = {} # 策略股票池表
        self.par = {'set':{},'run':{}} # 用户策略参数(set:设置参数,run:运行参数)


class UserEngine(object):
    """docstring for UserEngine"""
    def __init__(self, userInfo, action):

        self.action = action
        self.brokerage = userInfo['brokerage'] # 手续费
        self.stamptax = userInfo['stamptax'] # 印花税
        self.account = userInfo['userid']
        self.mode = userInfo['mode']

    # 保存交易记录
    def recordTransaction(self, mode, code, name, price, count, time=''):
        db = DB(DBInfo)
        if not db.isExistTable('account_transaction_record'):
            fields = dict(
                mode = 'varchar(5)',                                    # 买卖方式
                code = 'varchar(6)',                                    # 证券代码
                name = 'varchar(20)',                                   # 证券名称
                count = 'mediumint(8) UNSIGNED' if DBSet else 'int4',   # 证券数量
                price = 'float(7,3)' if DBSet else 'float4',            # 证券价格
                stockvalue = 'double(16,2)' if DBSet else 'float8',     # 证券市值
                actual = 'double(16,2)' if DBSet else 'float8',         # 实际金额
                brokerage = 'float(7,2)' if DBSet else 'float4',        # 手续费
                stamps = 'float(7,2)' if DBSet else 'float4',           # 印花税
                account = 'varchar(20)',                                # 发生账号
                action = 'varchar(20)',                                 # 执行策略
                date = 'datetime'  if DBSet else 'timestamp(6)'         # 发生时间
            )
            db.cearteTable('account_transaction_record',fields)

        nowTime = datetime.now() if time == '' else time

        value = {
            'account':self.account,
            'action':self.action,
            'mode':mode,
            'code':code,
            'name':name,
            'price':price,
            'count':int(count),
            'date':nowTime,
        }

        value['stockvalue'] = price * count
        value['brokerage'] = value['stockvalue'] * self.brokerage if value['stockvalue'] * self.brokerage > 5 else 5

        if mode == 'buy':
            value['stamps'] = 0
            value['actual'] = value['stockvalue'] + value['brokerage']

        if mode == 'sell':
            value['stamps'] = value['stockvalue'] * self.stamptax
            value['actual'] = value['stockvalue'] - value['brokerage'] - value['stamps']

        if self.mode:
            where = []
            where.append("account = '%s'" % self.account)
            where.append("action = '%s'" % self.action)
            where.append("code = '%s'" % code)
            where.append("mode = '%s'" % mode)
            where.append("date = '%s'" % nowTime)
            r = db.select('account_transaction_record',[],where)
            if len(r) <= 0:
                db.insert('account_transaction_record',value)
        else:
            db.insert('account_transaction_record',value)
        db.closeLink()

    # 获取交易记录
    def getTransaction(self, start=None, end=None):
        db = DB(DBInfo)
        where = ["account = '%s'" % self.account, "action = '%s'" % self.action]
        if start is not None:
            where.append("date > '%s'" % start.strftime('%Y-%m-%d %H:%M:%S'))
        if end is not None:
            where.append("date < '%s'" % end.strftime('%Y-%m-%d %H:%M:%S'))

        fields = db.getColumns('account_transaction_record')

        data = db.select('account_transaction_record',fields,where,['date ASC'])
        db.closeLink()
        if len(data) > 0:
            data = list(data)
            pd = pandas.DataFrame(data,columns = fields)
            pd = pd.set_index('date')
            return pd

    # 记录股票池信息
    def recordStockPool(self, mode=None, code='', name='', price=0, count=0):
        db = DB(DBInfo)
        if not db.isExistTable('account_stock_pool'):
            fields = dict(
                code = 'varchar(6)',
                name = 'varchar(20)',
                count = 'mediumint(8) UNSIGNED' if DBSet else 'int4',
                price = 'float(7,3)' if DBSet else 'float4',
                total = 'double(16,2)' if DBSet else 'float8',
                account = 'varchar(20)',
                action = 'varchar(20)'
            )
            db.cearteTable('account_stock_pool',fields)

        if mode is None: return

        where = ["code ='%s'" % code, "account ='%s'" % self.account, "action ='%s'" % self.action]
        record = db.select('account_stock_pool',['price','count'],where)

        value = {}
        if len(record) > 0:
            if mode == 'buy':    #购买时的更新
                value['price'] = (record[0][0] * record[0][1] + price * count) / (record[0][1] + count)
                value['count'] = int(record[0][1] + count)
                db.update('account_stock_pool',where,value)

            if mode == 'sell':   #卖出时的更新
                if record[0][1] <= count:
                    db.delete('account_stock_pool',where)
                else:
                    value['count'] = int(record[0][1] - count)
                    db.update('account_stock_pool',where,value)

            if mode == 'update':
                value['count'] = int(count)
                value['price'] = price
                value['total'] = count * price
                db.update('account_stock_pool',where,value)
        else:
            if mode == 'buy' and count > 0 :
                value['code'] = code
                value['name'] = name
                value['count'] = int(count)
                value['price'] = price
                value['total'] = count * price
                value['account'] = self.account
                value['action'] = self.action
                db.insert('account_stock_pool',value)
        db.closeLink()

    # 记录在仓股票除权信息 参数注解：(代码,之前总量,之前价格,之后总量,之后价格)
    def recordAccountEA(self,code=None,cb='',pb='',ca='',pa=''):
        db = DB(DBInfo)
        if not db.isExistTable('account_ea_record'):
            fields = dict(
                account = 'varchar(20)',
                action = 'varchar(20)',
                code = 'varchar(6)',
                date = 'date',
                count_before = 'mediumint(8) UNSIGNED' if DBSet else 'int4',
                count_after = 'mediumint(8) UNSIGNED' if DBSet else 'int4',
                price_before = 'float(7,3)' if DBSet else 'float4',
                price_after = 'float(7,3)' if DBSet else 'float4'
            )
            db.cearteTable('account_ea_record',fields)

        if code is None: return

        fields = dict(
            account = self.account,
            action = self.action,
            code = code,
            date = date.today(),
            count_after = ca,
            price_after = pa,
            count_before = cb,
            price_before = pb
            )
        db.insert('account_ea_record',fields)

    # 获取股票池信息
    def getStockPool(self):
        db = DB(DBInfo)
        if not db.isExistTable('account_stock_pool'):
            self.recordStockPool(None)

        where = ["account = '%s'" % self.account, "action ='%s'" % self.action]

        fields = ['code','name','price','count','total']

        r = db.select('account_stock_pool', fields, where)

        data = {}
        for i in r:
            price = high = low = i[2]
            count = i[3]
            total = i[4]

            # 获取最后一次购买记录日期
            where = ["code = '%s'" % i[0],"mode = 'buy'","action = '%s'" % self.action,"account = '%s'" % self.account]

            res = db.select('account_transaction_record',['date'],where,['date DESC'],[0,1])

            # 存在交易记录并且交易记录的购买时间早于今天
            if len(res) > 0 and res[0][0].date() < date.today():
                # 获取次代码历史里大于最后一次日期的所有数据

                where = ["code = '%s'" % i[0], "date > '%s'" % res[0][0].date()]
                hist = db.select('stock_day_data', ['high','low'], where, ['date DESC'])

                # 假如有数据则重新赋值给最高及最低
                if len(hist) > 0: high, low = max([i[0] for i in hist]),min([i[1] for i in hist])

            # 查找此代码今日是否有除权记录
            where = ["code = '%s'" % i[0], "date = '%s'" % date.today()]
            field = ['present','bonus','price','rationed','date']
            ea = db.select('stock_except_authority', field, where, ['date DESC'], [0,1])

            # 执行一次件除权记录表操作
            self.recordAccountEA(None)

            # 查找此代码此账户此策略今日是否已做除权处理的记录
            where.extend(["account = '%s'" % self.account, "action = '%s'" % self.action])
            aea = db.select('account_ea_record',[],where)

            # 添加交易模式为购买，移除搜索条件中的日期限制，查找交易记录表中此代码此策略此账户的最后一条记录
            where.extend(["mode = 'buy'"])
            where.remove("date = '%s'" % date.today())
            at = db.select('account_transaction_record',['date'],where,['date DESC'],[0,1])

            # 如果此代码今日有除权，而此账户此策略此代码除权记录为零，并且此账户此策略此代码的购买日期早于今日则代码做除权处理(避免软件出错而退出，软件重启时从而今天的票做也做除权，那是不用做的)
            if len(ea) > 0 and len(aea) == 0 and at[0][0].date() < ea[0][4].date():
                count = count + count * ea[0][0]/10
                price = (price - ea[0][1]/10) / (1 + ea[0][0]/10)
                high = high if len(hist) > 0 else (high - ea[0][1]/10) / (1 + ea[0][0]/10)
                low = low if len(hist) > 0 else  (low - ea[0][1]/10) / (1 + ea[0][0]/10)
                diff = (total - count * price)*0.8
                total = count * price

                self.recordStockPool('update', i[0], i[1], price, count)

                accData = self.getAccountInfo()
                accData['employ'] += diff
                self.recordAccountInfo(accData)
                self.recordAccountEA(i[0],i[3],i[2],count,price)

            data[i[0]] = {
                    'code' : i[0],
                    'name' : i[1],
                    'count' : count,
                    'price' : price,
                    'high' : high,
                    'low' : low,
                    'profit' : 0,
                    'loss' : 0,
                    'now' : 0,
                    'total' : total,
                    'worth' : 0,
                    'P&L' : 0,
                    'control' : ''
                }
        db.closeLink()
        return data

    # 记录系统策略数据
    def recordActionData(self, frame, value=None):
        db = DB(DBInfo)
        if not db.isExistTable('action_data_record'):
            fields = {}
            fields['account'] = 'varchar(20)'
            fields['action'] = 'varchar(20)'
            fields['frame'] = 'varchar(20)'
            fields['value'] = 'varchar(20)'
            db.cearteTable('action_data_record',fields)
        where = ["action = '%s'" % self.action,
                "account = '%s'" % self.account,
                "frame = '%s'"  % frame]
        record = db.select('action_data_record',[],where)
        values = {}
        if len(record) > 0:
            values['value'] = value
            db.update('action_data_record',where,values)
        else:
            values['account'] = self.account
            values['action'] = self.action
            values['frame'] = frame
            values['value'] = value
            db.insert('action_data_record',values)
        db.closeLink()

    # 获取系统策略记录的参数
    def getActionData(self, frame):
        db = DB(DBInfo)
        if not db.isExistTable('action_data_record'):
            self.recordActionData(frame,None)
        where = ["account = '%s'" % self.account,
                 "action = '%s'" % self.action,
                 "frame = '%s'" % frame]
        record = db.select('action_data_record', ['value'], where)
        if len(record) > 0:
            db.closeLink()
            return record[0][0] if record[0][0] is not None else None
        else:
            self.recordActionData(frame,None)
            db.closeLink()
            return None

    # 记录账户信息
    def recordAccountInfo(self,value):

        db = DB(DBInfo)
        if not db.isExistTable('account_info_record'):
            fields = {}
            for i in value:
                fields[i] = 'double(16,2)' if DBSet else 'float8'
            fields['account'] = 'varchar(20)'
            db.cearteTable('account_info_record',fields)
        where = ["account = '%s'" % self.account]
        record = db.select('account_info_record',[],where)
        if len(record) > 0:
            db.update('account_info_record',where,value)
        else:
            value['account'] = self.account
            db.insert('account_info_record',value)
        db.closeLink()

    # 获取账户信息
    def getAccountInfo(self):
        db = DB(DBInfo)
        if not db.isExistTable('account_info_record'):
            fields = dict(
                    account = 'varchar(20)',
                    total = 'double(16,2)' if DBSet else 'float8',
                    surplus = 'double(16,2)' if DBSet else 'float8',
                    employ = 'double(16,2)' if DBSet else 'float8',
                    free = 'double(16,2)' if DBSet else 'float8',
                    freeze = 'double(16,2)' if DBSet else 'float8',
                    stockvalue = 'double(16,2)' if DBSet else 'float8',
                )
            db.cearteTable('account_info_record',fields)
        fields = ['total','surplus','employ','free','freeze','stockvalue']
        record = db.select('account_info_record',fields,["account = '%s'" % self.account])
        if len(record) > 0:
            data = {}
            data['total'] = float(record[0][0]) # 总资产
            data['surplus'] = float(record[0][1]) # 资金余额
            data['employ'] = float(record[0][2]) # 可用余额
            data['free'] = float(record[0][3]) # 可取余额
            data['freeze'] = float(record[0][4]) # 冻结金额
            data['stockvalue'] = float(record[0][5]) # 股票市值

            db.closeLink()
        else:
            data = {}
            data['account'] = self.account
            data['total'] = 50000
            data['surplus'] = 50000
            data['employ'] = 50000
            data['free'] = 50000
            data['freeze'] = 0
            data['stockvalue'] = 0

            db.insert('account_info_record',data)
            db.closeLink()
        return data


if __name__ == '__main__':
    pass

    # ue = UserEngine(user[1],'smallvalue')

    # ue.recordTransaction('buy','603198','测试名字',6.18,6000)

    # print('jiaoyijilu',ue.getTransaction())

    # ue.recordStockPool('buy','603198','测试名字',6.18,6000)
    # ue.recordAccountEA('603198',6000,6.18,8000,5.11)
    # ue.recordActionData('days',3)
    # print('gupiaochi',ue.getStockPool())
    # print('celuedongzuo',ue.getActionData('days'))
    # print('zhanghuxinxi',ue.getAccountInfo())

    # print(uc.balance)
    # print(uc.ProfitAndLoss)
