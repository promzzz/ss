# coding:utf8

import asyncio
import aiohttp
import yarl
import requests

from Helpers.RelatedCode import perfectCode



class Base:
    """行情获取基类"""
    max_num = 800  # 每次请求的最大股票数
    Realtime_API = ''  # 实时行情接口
    HistData_API = ''  # 历史数据接口

    def __init__(self):
        super(Base, self).__init__()
        self._session = None
        # self.stockList = stockList

    def gen_stock_list(self, stock_codes):
        stock_codes = stock_codes if type(stock_codes) == list else [stock_codes]
        stock_with_exchange_list = [perfectCode(code) + code[-6:] for code in stock_codes]
        stock_list = []
        request_num = len(stock_codes) // self.max_num + 1
        for range_start in range(request_num):
            num_start = self.max_num * range_start
            num_end = self.max_num * (range_start + 1)
            request_list = ','.join(stock_with_exchange_list[num_start:num_end])
            stock_list.append(request_list)
        return stock_list
    
    async def get_stocks_by_range(self, params):
        if self._session is None:
            self._session = aiohttp.ClientSession()
        headers = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'
        }
        url = yarl.URL(self.Realtime_API + params, encoded=True)
        try:
            async with self._session.get(url, timeout=10, headers=headers) as r:
                response_text = await r.text()
                return response_text
        except asyncio.TimeoutError:
            return None

    # 获取实时数据
    def getAllData(self, stock_list, **kwargs):

        stock_list = self.gen_stock_list(stock_list)

        coroutines = []

        for params in stock_list:
            coroutine = self.get_stocks_by_range(params)
            coroutines.append(coroutine)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        res = loop.run_until_complete(asyncio.gather(*coroutines))
        return self.formatRealtimeData([x for x in res if x is not None], **kwargs)

    def getHistoryData(self,stock):
        pass

    def getRealtimeData(self,codes):
        codes = [codes] if type(codes) == str else codes
        codes = [perfectCode(code) + code[-6:] for code in codes]
        codes = ','.join(codes)

        agent = {'Accept-Encoding': 'gzip, deflate, sdch',
                 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
        s = requests.session()
        s.headers.update(agent)
        try:
            data = s.get(self.Realtime_API+codes)
        except:
            pass
        finally:
            d = {}
            for i in data.text.split('\n'):
                x = self.formatRealtimeData(i)
                if len(x) > 0:
                    d.update(x)
            return d

    def __del__(self):
        if self._session is not None:
            self._session.close()

    def formatRealtimeData(self, rep_data, **kwargs):
        pass
