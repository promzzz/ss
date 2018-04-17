
# coding:utf-8

# 系统自带包
import datetime
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
from Helpers.RelatedZX import getStockTickData
from Helpers.RelatedCode import get_all_codes,get_code_list,perfectCode
from Helpers.RelatedDZH import get_finance_365_net,get_except_365_net,get_finance_365_local
from Helpers.RelatedTool import *

# from setting import databases
from setting import *

DB,DBSet = (MySQL,True) if system['database'] == 'MySQL' else (PostgreSQL,False)

class DataEngine(object):
    """docstring for DataEngine"""
    def __init__(self):
        pass

    def multipro(self, function, lists):
        res = {}
        if __name__ == '__main__':
            cpu = multiprocessing.cpu_count()*4
            pool = multiprocessing.Pool(cpu)
            for i in lists: res[i] = pool.apply_async(function,(i,))
            pool.close()
            pool.join()

            res = {i:result.get() for i,result in res.items()}
        else:
            for i in lists: res[i] = function(i)
        return res

    # 更新代码列表
    def updateCodeList(self):
        db = DB(DBInfo)
        if not db.isExistTable('stock_codes_list'):
            fields = {}
            fields['date'] = 'date DEFAULT(now())'
            fields['code'] = 'varchar(6)'
            fields['name'] = 'varchar(20)'
            fields['market'] = 'varchar(6)'
            fields['type'] = 'varchar(20)'
            db.cearteTable('stock_codes_list',fields)
        stockList,exponentList = get_all_codes()
        beCode = self.getCodeList('stock')
        newList = []
        if len(beCode) > 0:
            for code,val in stockList.items():
                if code in beCode.index.values and val['name'] != beCode.loc[code].at['name'] and datetime.date.today() != beCode.loc[code].at['date'] or code not in beCode.index.values:
                    newList.append(val)
            if len(newList) > 0: db.insertAll('stock_codes_list',newList)
        else:
            newList = [val for code,val in stockList.items()]
            db.insertAll('stock_codes_list',newList)

        beCode = self.getCodeList('exponent')
        exponentList = [val for code,val in exponentList.items() if code not in beCode.index.values]
        if len(exponentList) > 0: db.insertAll('stock_codes_list',exponentList)
        db.closeLink()

    # 获取代码列表
    def getCodeList(self, types='stock', market=None):
        db = DB(DBInfo)
        if not db.isExistTable('stock_codes_list'): self.updateCodeList()
        fields = ['date','code','name','market']
        if DBSet:
            fields.remove('date')
            fields = '`,`'.join(fields)
            r = db.custom('SELECT Max(`date`) AS `date`,`%s` FROM stock_codes_list WHERE `type` = "%s" GROUP BY `code` ORDER BY `date` DESC' % (fields,types))
            fields = fields.split('`,`')
            fields.insert(0,'date')
        else:
            r = []
            codes = db.custom('SELECT code,Max("date") AS "date" FROM stock_codes_list WHERE type = \'%s\' GROUP BY code' % types)
            for i in codes:
                where = ["code = '%s'" % i[0], "date = '%s'" % i[1]]
                r.append(db.select('stock_codes_list',fields,where)[0])
        df = pandas.DataFrame(list(r), columns=fields)
        df = df.set_index('code')
        return df

    # 创建基本代码信息
    def createStockBaseInfo(self):
        db = DB(DBInfo)
        if not db.isExistTable('stock_basic_info'):
            fields = dict(
                code = 'varchar(6)',
                name = 'varchar(20)',
                pe = 'double(16,4)' if DBSet else 'float8', #市盈率
                pb = 'double(16,4)' if DBSet else 'float8', #市净率
                ps = 'double(16,4)' if DBSet else 'float8', #市销率
                roe = 'double(16,4)' if DBSet else 'float8', #净资收益率
                eps = 'double(16,4)' if DBSet else 'float8', #每股收益
                bvps = 'double(16,4)' if DBSet else 'float8', #每股净值
                ts = 'double(16,4)' if DBSet else 'float8',  # 总股本
                cs = 'double(16,4)' if DBSet else 'float8',  # 流通股本
                ta = 'double(16,4)' if DBSet else 'float8',  # 总资产
                ca = 'double(16,4)' if DBSet else 'float8',  # 流通资产
                fa = 'double(16,4)' if DBSet else 'float8',  # 固定资产
                mv = 'double(16,4)' if DBSet else 'float8',  # 市值
                md = 'date'     # 上市时间
            )
            db.cearteTable('stock_basic_info',fields)

        codes = self.getCodeList('stock')
        close = self.getHistListData()
        infos = self.getFinanceList()

        data = []

        for code,val in codes.iterrows():
            if code not in infos.index.values or code not in close.index.values: continue

            cp = close.loc[code].at['close']
            eps = infos.loc[code].at['eps']
            bvps = infos.loc[code].at['bvps']
            mi = infos.loc[code].at['main_income']
            ts = infos.loc[code].at['total_shares']

            data.append(dict(
                code = code,
                name = val['name'],
                pe = cp / eps if cp != 0 and eps != 0 else 0,
                pb = cp / bvps if cp != 0 and bvps != 0 else 0,
                ps = cp / (mi / ts) if mi != 0 and ts != 0 else 0,
                roe = eps / bvps if eps != 0 and bvps != 0 else 0,
                eps = eps,
                bvps = bvps,
                ts = ts,
                cs = infos.loc[code].at['a_share'],
                ta = infos.loc[code].at['total_assets'],
                ca = infos.loc[code].at['current_assets'],
                fa = infos.loc[code].at['fixed_assets'],
                mv = cp * ts,
                md = infos.loc[code].at['market_date'],
            ))
        db.truncateTable('stock_basic_info')
        db.insertAll('stock_basic_info',data)
        db.closeLink()

    # 获取基本代码信息
    def getStockBaseInfo(self, where=[], order=[], count=0):
        db = DB(DBInfo)
        if not db.isExistTable('stock_basic_info'): self.createStockBaseInfo()
        fields = db.getColumns('stock_basic_info')

        if count == None or count <= 0:
            data = db.select('stock_basic_info',fields,where,order)
        else:
            data = db.select('stock_basic_info',fields,where,order,[0,count])

        data = list(data)
        pd = pandas.DataFrame(data,columns = fields)
        pd = pd.set_index('code')
        return pd

    # 下载除权数据
    def downExceptAuthorityData(self):
        db = DB(DBInfo)
        if db.isExistTable('stock_except_authority'):
            od = self.getExceptAuthorityList()
            nd = get_except_365_net()
            data = []
            for i in nd:
                if i['code'] not in od.index.values:
                    if i['code'].startswith(('0', '3', '6')):
                        data.append(i)
                else:
                    # print('下载',type(i['date']),i['date'])
                    # print('库里',type(od.loc[i['code']].at['date']),od.loc[i['code']].at['date'])
                    # print(i['date'] > od.loc[i['code']].at['date'])
                    if i['date'] > od.loc[i['code']].at['date']:
                        data.append(i)
                        # print('达到条件')
            if len(data) > 0 : db.insertAll('stock_except_authority',data)
        else:
            fields = dict(
                code = 'varchar(6)',
                date = 'datetime'  if DBSet else 'timestamp(6)',
                present = 'float(7,2)' if DBSet else 'float4',
                bonus = 'float(7,2)' if DBSet else 'float4',
                price = 'float(7,2)' if DBSet else 'float4',
                rationed = 'float(7,2)' if DBSet else 'float4'
            )

            exData = get_except_365_net()
            db.cearteTable('stock_except_authority', fields, index=['code', 'date'])
            db.insertAll('stock_except_authority',exData)
        db.closeLink()

    # 获取除权列表
    def getExceptAuthorityList(self):
        db = DB(DBInfo)
        if not db.isExistTable('stock_except_authority'): self.downExceptAuthorityData()

        if DBSet:
            r = db.custom('SELECT `code`,Max(date) AS `date` FROM stock_except_authority GROUP BY `code` ORDER BY `date` ASC')
        else:
            r = db.custom('SELECT "code",Max("date") AS "date" FROM stock_except_authority GROUP BY code ORDER BY "date" ASC')

        df = pandas.DataFrame(list(r), columns=['code','date'])
        df = df.set_index('code')
        return df

    # 获取单只代码时间段除权信息
    def getExceptAuthority(self,code, begin=None, end=None):
        db = DB(DBInfo)
        if not db.isExistTable('stock_except_authority'):
            self.downExceptAuthorityData()

        fields = db.getColumns('stock_except_authority')
        fields.remove('code')

        where = ["code = '%s'" % code]
        if begin is not None : where.append("date >= '%s'" % str(begin)[:10])
        if end is not None:
            where.append("date <= '%s'" % str(end)[:10])
        else:
            where.append("date <= '%s'" % datetime.date.today())
        order = ['date ASC']
        data = db.select('stock_except_authority',fields,where,order)

        db.closeLink()

        pd = pandas.DataFrame()
        if len(data) > 0:
            pd = pandas.DataFrame(list(data),columns = fields)
            pd = pd.sort_values(by='date',ascending=False)
            pd = pd.set_index('date')
        return pd

    # 下载财务数据
    def downFinanceData(self):
        db = DB(DBInfo)
        if db.isExistTable('stock_finance_data'):
            od = self.getFinanceList()
            nd = get_finance_365_net()
            # nd = get_finance_365_local()
            data = []
            for i in nd:
                if i['code'] not in od.index.values:
                    data.append(i)
                else:
                    if i['report_date'] > od.loc[i['code']].at['report_date']:
                        data.append(i)
            if len(data) > 0 : db.insertAll('stock_finance_data',data)
        else:
            finance = get_finance_365_net()
            # finance = get_finance_365_local()
            fields = {}
            for i in finance[0].keys():
                if type(finance[0][i]) == datetime.date:
                    fields[i] = 'date'
                if type(finance[0][i]) == str:
                    fields[i] = 'varchar(20)'
                if type(finance[0][i]) == float:
                    fields[i] = 'double(16,4)' if DBSet else 'float8'
            db.cearteTable('stock_finance_data', fields, index=['code', 'report_date'])
            db.insertAll('stock_finance_data',finance)
        db.closeLink()

    # 获取财务数据列表
    def getFinanceList(self):
        db = DB(DBInfo)
        if not db.isExistTable('stock_finance_data'): self.downFinanceData()
        fields = db.getColumns('stock_finance_data')
        if DBSet:
            fields.remove('code')
            fields.remove('report_date')
            fields = '`,`'.join(fields)
            r = db.custom('SELECT `code`,Max(report_date) AS report_date,`%s` FROM stock_finance_data GROUP BY `code` ORDER BY report_date DESC' % fields)
            fields = fields.split('`,`')
            fields.insert(0,'report_date')
            fields.insert(0,'code')
        else:
            r = []
            codes = db.custom('SELECT code,Max(report_date) AS report_date FROM stock_finance_data GROUP BY code ORDER BY report_date DESC')
            for i in codes:
                where = ["code = '%s'" % i[0], "report_date = '%s'" % i[1]]
                r.append(db.select('stock_finance_data',fields,where)[0])

        df = pandas.DataFrame(list(r), columns=fields)
        df = df.set_index('code')

        return df

    # 获取单只代码财务数据
    def getFinance(self, code=''):
        db = DB(DBInfo)
        if not db.isExistTable('stock_finance_data'): self.downFinanceData()

        where = ["code = '%s'" % code]
        fields = db.getColumns('stock_finance_data')
        fields.remove('code')
        order = ['report_date DESC']
        data = db.select('stock_finance_data',fields,where,order)
        db.closeLink()
        if len(data) > 0:
            data = list(data)
            df = pandas.DataFrame(data, columns=fields)
            df = df.set_index('report_date')
            return df

    # 下载单只代码历史数据
    def downHistData(self,code='',unit='d'):

        from Quotation.Sina import Sina

        sina = Sina()

        db = DB(DBInfo)

        classes, codes = ('exponent',code[2:]) if len(code) > 6 else ('stock',code)
        table = {'w':'%s_week_data' % classes, 'd':'%s_day_data' % classes, 'h':'%s_hour_data' % classes}
        table = table.get(unit)

        if db.isExistTable(table):
            where = ["code = '%s'" % codes]
            nowTime = datetime.datetime.now()
            last = db.select(table,['date'],where,['date DESC'],[0,1])

            if len(last) > 0:
                if unit == 'd':
                    datalen = (nowTime-last[0][0]).days
                if unit == 'h':
                    datalen = (nowTime-last[0][0]).days*4
                if unit == 'i':
                    datalen = (nowTime-last[0][0]).days*240

                if nowTime.weekday() < 5:
                    l = 1 if nowTime.hour < 15 else 0
                else:
                    l = 1 if nowTime.weekday() < 6 else 2
                # 如果数据长度大于差异 则下载数据
                if datalen > l:
                    histData = sina.getHistoryData(code,unit,datalen)
                    # histData = self.qe.source.getHistoryData(code, unit, datalen)
                    if histData is not None:
                        record = db.select(table,['date'],where,['date DESC'],[0,datalen])

                        if len(histData[0]['date']) > 10:
                            record = [i[0].strftime('%Y-%m-%d %H:%M:%S') for i in record]
                        else:
                            record = [i[0].strftime('%Y-%m-%d') for i in record]
                        listData = [v for v in histData if v['date'] not in record]

                        if len(listData) > 0:
                            db.insertAll(table,listData)
                            db.closeLink()
            else:
                histData = sina.getHistoryData(code,unit)
                if histData is not None:
                    db.insertAll(table,histData)
                    db.closeLink()

        else:
            histData = sina.getHistoryData(code,unit)
            if histData is not None:
                fields = {'code':'varchar(6)'}
                for key in histData[0]:
                    if key == 'date':
                        fields[key] = 'datetime'  if DBSet else 'timestamp(6)'
                    elif key.startswith('v') or key.startswith('a'):
                        fields[key] = 'bigint(20)' if DBSet else 'int8'
                    elif key != 'code':
                        if DBSet:
                            fields[key] = 'float(7,2)' if table.startswith('s') else 'double(16,3)'
                        else:
                            fields[key] = 'float4' if table.startswith('s') else 'float8'

                db.cearteTable(table, fields, index=['code', 'date'])
                db.insertAll(table, histData)
                db.closeLink()

    # 获取单只代码历史数据  代码 字段 时间长度 时间单位 读取模式 复权方式
    def getHistData(self,code,fields=[],length=1,unit='d',types = 'r',fq ='forward'):
        db = DB(DBInfo)

        classes, code = ('exponent',code[2:]) if len(code) > 6 else ('stock',code)
        table = {'w':'%s_week_data' % classes, 'd':'%s_day_data' % classes, 'h':'%s_hour_data' % classes}
        table = table.get(unit)

        if not db.isExistTable(table): return pandas.DataFrame()

        if len(fields) > 0:
            if 'date' not in fields: fields.append('date')
        else:
            fields = db.getColumns(table)
            fields.remove('code')

        if 'tick' in fields: fields.remove('tick')

        order = ['date DESC']
        where = ["code = '%s'" % code]

        if types == 't':
            # 按时间长度之前开始读取，时间长度里包括节假日停牌日
            startday = datetime.datetime.now() - datetime.timedelta(days=length)
            where.append("date >= '%s'" % str(startday)[:10])
            data = db.select(table,fields,where,order,[])

        elif types == 'd':
            # 自某一日期起开始读取，时间长度的整数变量改为时间变量
            where.append("date >= '%s'" % str(length)[:10])
            data = db.select(table,fields,where,order,[])
        else:
            # 按照时间长度读取，排除节假日停牌日
            limit = [0,length]
            data = db.select(table,fields,where,order,limit)

        db.closeLink()
        # print(data)
        if len(data) > 0:
            # print(code,data)
            df = pandas.DataFrame(list(data),columns = fields)
            df = df.set_index('date')
        else:
            df = pandas.DataFrame()
        # print(table,df)
        if fq == 'forward' and table.startswith('s') and len(df) > 0:
            # print(type(df.index.values[-1]),df.index.values[-1])
            ea = self.getExceptAuthority(code, df.index.values[-1])
            # print(code,ea)
            if len(ea) > 0:
                for key,val in ea.iterrows():
                    date = key - datetime.timedelta(days=1)
                    for field in df.columns.values:
                        if field != 'volume' and field != 'amount' and field != 'tick':
                            df.ix[date:,field] -= val.bonus/10
                            df.ix[date:,field] += val.price*(val.rationed/10)
                            df.ix[date:,field] /= 1 + val.present/10 + val.rationed/10
                    if key == ea.index.values[-1]:
                        return df
            else:
                return df
        # elif fq == 'backward' and len(code) <= 6 and len(df) > 0:
        #     pass
        else:
            return df

    # 获取所有代码数据列表
    def getHistListData(self):
        db = DB(DBInfo)
        if not db.isExistTable('stock_day_data'): return
        if DBSet:
            r = db.custom('SELECT `code`,Max(`date`) AS `date`,`close` FROM stock_day_data GROUP BY `code` ORDER BY `date` DESC' % fields)
        else:
            r = []
            codes = db.custom('SELECT code,Max(date) AS date FROM stock_day_data GROUP BY code ORDER BY date DESC')
            for i in codes:
                where = ["code = '%s'" % i[0], "date = '%s'" % i[1]]
                r.append(db.select('stock_day_data',['code','date','close'],where)[0])

        df = pandas.DataFrame(list(r), columns=['code','date','close'])
        df = df.set_index('code')

        return df

    def getRealtimeData(self,codes):
        from Quotation.Sina import Sina
        sina = Sina()
        return sina.getRealtimeData(codes)

    # 查对数据库
    def checkData(self):

        db = DB(DBInfo)
        logFile = '%supdate.log' % tempdir

        if datetime.time(9,0,0) < datetime.datetime.now().time() < datetime.time(15,5,0): return
        try:
            log = open(logFile,'r')
        except:
            log = open(logFile,'w')
            log.write(json.dumps({'step':6}))
            step = 6
        else:
            step = json.loads(log.read()).get('step')
        finally:
            log.close()

        nowTime = datetime.datetime.now
        try:
            start = datetime.datetime.now()
            r = db.select('exponent_day_data',['date'],["code = '399602'"],['date DESC'],[0,1])
        except:
            pass
        else:
            if start.weekday() == 0:
                diff = 3 if start.time() < datetime.time(15,0,0) else 0
            elif start.weekday() < 5:
                diff = 1 if start.time() < datetime.time(15,0,0) else 0
            else:
                diff = 1 if start.weekday() < 6 else 2

            if (start.date() - r[0][0].date()).days <= diff and step == 10: return

        if step > 9:
            st = datetime.datetime.now()
            try:
                self.updateCodeList()
            except:
                string = ' 代码列表更新失败 耗时:'
                pass
            else:
                string = ' 代码列表更新完成 耗时:'
                log = open(logFile,'w')
                log.write(json.dumps({'step':9}))
                log.close()
            finally:
                print(time.ctime(), string, nowTime()-st)

        if step > 8:
            st = datetime.datetime.now()
            try:
                self.downFinanceData()
            except:
                string = ' 财务数据更新失败 耗时:'
            else:
                string = ' 财务数据更新完成 耗时:'
                log = open(logFile,'w')
                log.write(json.dumps({'step':8}))
                log.close()
            finally:
                print(time.ctime(), string, nowTime()-st)

        if step > 7:
            st = datetime.datetime.now()
            try:
                self.downExceptAuthorityData()
            except:
                string = ' 除权数据更新失败 耗时:'
            else:
                string = ' 除权数据更新完成 耗时:'
                log = open(logFile,'w')
                log.write(json.dumps({'step':7}))
                log.close()
            finally:
                print(time.ctime(), string, nowTime()-st)

        if step > 6:
            st = datetime.datetime.now()
            codes = self.getCodeList('stock')
            self.multipro(self.downHistData, codes.index.values)
            print(time.ctime(), ' 股票数据更新完成 耗时:', nowTime()-st)

            log = open(logFile,'w')
            log.write(json.dumps({'step':6}))
            log.close()

        if step > 5:
            st = datetime.datetime.now()
            codes = self.getCodeList('exponent')
            codes = [v['market']+k for k,v in codes.iterrows()]
            self.multipro(self.downHistData, codes)

            print(time.ctime(), ' 指数数据更新完成 耗时:', nowTime()-st)

            log = open(logFile,'w')
            log.write(json.dumps({'step':5}))
            log.close()

        if step > 4:
            st = datetime.datetime.now()

            self.createStockBaseInfo()
            print(time.ctime(), ' 基本数据创建完成 耗时:', nowTime()-st)


            print(time.ctime(), ' 所有步骤全部完成 耗时:', nowTime()-start)
            log = open(logFile,'w')
            log.write(json.dumps({'step':10}))
            log.close()


if __name__ == '__main__':

    de = DataEngine()
    s = datetime.datetime.now()


    # de.updateCodeList()
    # de.downFinanceData()
    # de.createStockBaseInfo()
    # de.downHistData('sh000001')
    # de.downHistData('600960')
    # print(de.getHistData('600960',[],250))
    # print(de.getHistListData())
    de.checkData()
    # print(de.getCodeList().date.values.max())
    # de.updateCodeList()
    e = datetime.datetime.now()

    print(e-s)

    # de.downExceptAuthorityData()
    # de.downHistData('600960')
    # de.completeTickData('600960',datetime.date.today())

    # print(de.getCodeList())
    # print(de.getStockBaseInfo())
    # print(de.getFinanceList())
    # print(de.getFinance('600960'))
    # print(de.getExceptAuthority('600960'))
    # print(de.getExceptAuthorityList())