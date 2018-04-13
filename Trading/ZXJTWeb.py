import os
import tempfile
import sys
sys.path.append('../')

import datetime
import time

# 第三方扩展包
import requests

from Trading.API import API
from Trading.Web import Web
from Helpers.RelatedTool import *
from Helpers.RelatedTime import *


class ZXJTWeb(Web, API):

    # 扩展初始化函数
    def _init(self):
        pass

    def login(self):
        try:
            self.S.get(self.API['loginPage'])
            checkCode = self.__checkCode()
        except Exception as e:
            pass
        else:
            loginParams = dict(
                inputid = self.U['userid'],
                j_username = self.U['userid'],
                j_inputid = self.U['userid'],
                j_password = self.U['password'],
                AppendCode = checkCode,
                isCheckAppendCode = 'false',
                logined = 'false',
                f_tdx = '',
                j_cpu = ''
                )
            logined = self.S.post(self.API['login'], params=loginParams)
            if logined.text.find(u'消息中心') != -1:
                self.caseEngine.userStatus = True
                self.caseEngine.sonWindow.checkStatus()
                return True
            return False

    # 获取并识别返回的验证码
    def __checkCode(self):
        # 获取验证码
        verify_code_response = self.S.get(self.API['checkCode'])
        # 保存验证码
        image_path = tempfile.mktemp()
        with open(image_path, 'wb') as f:
            f.write(bytes(verify_code_response.content))
        verify_code = verifyCode(image_path, 'zxjt')
        os.remove(image_path)

        ht_verify_code_length = 4
        if len(verify_code) != ht_verify_code_length:
            return False
        return verify_code

    def checkStatus(self):
        params = dict(isOcx='0', password='NzkwNTE5')
        # params = dict(isOcx='0', password=self.U['password'])
        txtdata = self.S.post(self.API['checkStatus'], params=params)
        jsonobj = formatWebJSON(txtdata)
        return jsonobj['result']

    def logout(self):
        self.isActive = False

    # 获取账户资金状况
    def _getFundInfo(self):
        txtdata = self.S.get(self.API['fundPool'])
        try:
            jsonobj = formatWebJSON(txtdata)
            stkdata = jsonobj['data']['moneytype0']
            # print(stkdata)
            # stkdata['fundid'] = jsonobj['fundid']
            fundinfo = dict(
                total = jsonobj['data']['moneytype0']['marketvalue'],
                surplus = jsonobj['data']['moneytype0']['fundbal'],
                employ = jsonobj['data']['moneytype0']['fundavl']
                )
            # print(fundinfo)
            return fundinfo
        except:
            pass

    # 获取账户持仓数据
    def _getStockInfo(self):
        # print(self.API['stockPool'])
        txtdata = self.S.get(self.API['stockPool'])
        # print(txtdata.text)
        try:
            jsonobj = formatWebJSON(txtdata)
            stocks = {}
            # print(jsonobj['data'])
            for i in jsonobj['data']:
                # print(i)
                stocks[i['stkcode']] = i
            # print(stocks)
            return stocks
        except:
            pass

    def _buyNewStock(self):
        pass
    # 订单函数
    def _trading(self, mode, code, price, count):
        if mode == 'buy':
            bsflag = 'B'
            buyflag = 'buy'
        else:
            bsflag = 'S'
            buyflag = 'sell'
        try:
            url = self.API['tradeCheck'] %(bsflag, code, buyflag, nowTimeStamp())
            txtdata = self.S.get(url)
        except Exception as e:
            self.autoLogin()
            self._trading(mode, code, price, count)
        else:
            # pass
            data = formatWebJSON(txtdata)['returnList'][0]
            if data.get('buysSecuid') is not None:
                buytype = '买入' if bsflag == 'B' else '卖出'
                tradeParams = dict(
                        stkname = data['stkname'],
                        stkcode = code,
                        buycount = count,
                        buyprice = price,
                        buytype = buytype,
                        secuid = data['buysSecuid'],
                        maxstkqty = '',
                        bsflag = bsflag,
                        _ = nowTimeStamp()
                    )
                tradeResult = self.S.post(self.API['tradeSubmit'], params=tradeParams)
                print(formatWebJSON(tradeResult))
                return formatWebJSON(tradeResult)
            return None

    def _getEntrustList(self, begin=None, end=None):
        if begin is None and end is None:
            url = self.API['entrust'] + '&_=%d'
            url = url % ('intraDay', nowTimeStamp())
        else:
            url = self.API['entrust'] + '&beginDate=%s&endDate=%s&_=%d'
            # begin = time.mktime(begin.timetuple()) * 1000
            # end = nowTimeStamp() if end is None else time.mktime(end.timetuple())
            end = datetime.date.today().strftime('%Y%m%d') if end is None else end.strftime('%Y%m%d')
            url = url % ('history', begin.strftime('%Y%m%d'), end, nowTimeStamp())
        # ['ordersno', 'stkcode', 'stkname', 'bsflagState', 'orderqty', 'matchqty', 'orderprice', 'operdate', 'opertime', 'orderdate', 'state']
        # ["操作日期","交易日","股东代码","证券代码","证券名称","状态说明","买卖标志","委托价格","委托数量","已成交数量","可撤单数量","委托编号","交易时间","cancelflag"]
        # print(url)
        txtdata = self.S.get(url)
        # print(txtdata)
        jsonobj = formatWebJSON(txtdata)['data']
        data = list()
        if jsonobj['total'] > 1:
            pass
        else:
            data.extend(jsonobj['rows'])

        return data

    def _getClinchDealList(self, begin=None, end=None):
        if begin is None and end is None:
            url = self.API['clinchDeal'] + '&_=%d'
            url = url % ('intraDay', nowTimeStamp())
        else:
            url = self.API['clinchDeal'] + '&beginDate=%s&endDate=%s&_=%d'
            end = datetime.date.today().strftime('%Y%m%d') if end is None else end.strftime('%Y%m%d')
            url = url % ('all', begin.strftime('%Y%m%d'), end, nowTimeStamp())
        # ['ordersno', 'matchcode', 'trddate', 'matchtime',  'stkcode', 'stkname', 'bsflagState', 'orderprice', 'matchprice', 'orderqty', 'matchqty', 'matchamt']
        # ["成交日期 ","成交时间","证券代码","证券名称","买卖标志","状态说明","委托价格","委托数量","成交价格","已成交数量","成交金额","股东代码","委托编号","成交编号"]
        txtdata = self.S.get(url)
        jsonobj = formatWebJSON(txtdata)
        return jsonobj['data']

    # 可撤销委托
    def revocableEntrust(self, code=None):
        data = self.S.get(self.API['revocableEntrust'] % nowTimeStamp())
        jsonobj = formatWebJSON(data)
        data = jsonobj['data']
        if code is not None:
            state = False
            for i in data:
                if code == i['stkcode']:
                    state = True
                    trade = i
                    break
            if state is True:
                url = self.API['revocableEntrustSubmit'] % (trade['bsflagState'],
                                                            trade['stkcode'], 
                                                            trade['stkname'], 
                                                            trade['ordersno'], 
                                                            trade['orderdate'], 
                                                            nowTimeStamp()
                                                            )
                result = self.S.get(url)
                jsonobj = formatWebJSON(result)  
                return jsonobj['msgMap']['resultSucess']
            return False
        else:
            return data

    def _newStockCount(self):
        data = self.S.get(self.API['newStockCount'] % nowTimeStamp())
        data = formatWebJSON(data)
        if data['result'] == True:
            count = {}
            for i in data['rows']:
                if '上海' in i['remark']:
                    count['sh'] = int(i['custquota'])
                else:
                    count['sz'] = int(i['custquota'])
            return count

    def _newStockList(self):
        data = self.S.get(self.API['newStockList'] % nowTimeStamp())
        data = formatWebJSON(data)
        if data['result'] == True:
            return data['rows']

if __name__ == '__main__':

    clockEngine = 'clockEngine'
    a = ZXJTWeb(clockEngine)
    # print(a.fundPool)
    # print(a.stockPool)
    # l1 = a.entrustList(datetime.date(2017,6,10))
    # l2 = a.entrustList()
    # l1 = a.clinchDealList()
    # l2 = a.clinchDealList(datetime.date(2017,6,10))
    # l1 = a.revocableEntrust()
    count = a.newStockCount()
    l1 = a.newStockList()
    # l2 = a.revocableEntrust('601398')
    # l2 = a.buyStock('600016',8.1,4000)
    for i in l1:
        if i['wsfxr'] == datetime.date.today().strftime('%Y-%m-%d'):
            a.buyStock(i['symbol'],i['fxj'],2000)
            # print(i)
    # print(l1)
    # print(l)
    # print(111111,l1)
    # print(222222,l2,)
    # for i in l:
    #     print('')
    #     print(i)
