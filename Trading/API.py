
class API():
    """docstring for API"""
    def __init__(self):
        super(API, self).__init__()
        pass

    # 账户资金信息
    @property
    def fundPool(self):
        return self._getFundInfo()

    # 获取账户资金状况
    def _getFundInfo(self):
        pass

    # 账户持仓信息
    @property
    def stockPool(self):
        return self._getStockInfo()

    # 获取账户持仓数据
    def _getStockInfo(self):
        pass

    # 买入接口函数
    def buyStock(self, code, price, count):
        return self._trading('buy', code, price, count)

    # 卖出接口函数
    def sellStock(self,code,price,count):
        return self._trading('sell', code, price, count)

    def newStockCount(self):
        return self._newStockCount()

    def _newStockCount(self):
        pass

    def newStockList(self):
        return self._newStockList()

    def _newStockList(self):
        pass
    # 打新函数
    def buyNewStock(self):
        self._buyNewStock()

    def _buyNewStock(self):
        pass
        
    # 获取委托单列表
    def entrustList(self, begin=None, end=None):
        return self._getEntrustList(begin, end)

    # 获取成交列表
    def clinchDealList(self, begin=None, end=None):
        return self._getClinchDealList(begin, end)

    def _getEntrustList(self, begin=None, end=None):
        pass

    def _getClinchDealList(self, begin=None, end=None):
        pass

    

