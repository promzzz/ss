from Trading.API import API
from Trading.Client import Client

class ZXClient(Client, API):
    
    shortcut = {'infoPanel':'F4','buyPanel':'F1','sellPanel':'F2','cancelPanel':'F3','twowayPanel':'F6'}
    position = {'todayTradePanel':[70,170],'todayEntrustPanel':[70,150],'histTradePanel':[70,250],'histEntrustPanel':[70,230],'newStockPanel':[[70,410],[70,430]]}
    widgetID = {'subPanel':59648,'infoPanel':59649,'buyPanel':59649,'sellPanel':59649,'cancelPanel':59649,'twowayPanel':59649,'treeView':[59648,129,200,129],'toolBar':59392,'statusBar':59393,'loginUseridInput':1011,'loginPasswordInput':1012,'loginCodeInput':1003,'loginIdentifyPic':1499,'loginButton':1006,'infoTotal':1015,'infoSurplus':1012,'infoEmploy':1016,'infoFree':1017,'infoFreeze':1013,'infoStockVal':1014,'activePasswordInput':1039,'activeButton':1,'buyCodeInput':1032,'buyPriceInput':1033,'buyCountInput':1034,'buyButton':1006,'sellCodeInput':1032,'sellPriceInput':1033,'sellCountInput':1034,'sellButton':1006,'buyAndSellYes':6,'buyAndSellNo':7,'histTradePanel':59649,'histTradeBeginInput':1009,'histTradeEndInput':1010,'histTradeButton':1006,'histEntrustPanel':59649,'histEntrustBeginInput':1009,'histEntrustEndInput':1010,'histEntrustButton':1006,'newStockPanel':59649,'newStockCodeInput':1032,'newStockPriceInput':1033,'newStockCountInput':1034,'newStockButton':1006}

    name = '中信证券至胜全能版'
    activeName = '中信证券至胜全能版（V5.18.51.412）'

    def _buyStock(self, code, price, count):
        self.buy(code, price, count)

    def _sellStock(self, code, price, count):
        self.sell(code, price, count)

    def _getTodayTrade(self):
        return self.todayTrade()

    def _getHistoryTrade(self, begin=None, end=None):
        return self.historyTrade(begin,end)

if __name__ == '__main__':

    a = ZhongXin(r'D:\jtxd\xiadan.exe','880001852793','790519','侯剑锋')
    a.checkState()
    a.getBaseInfo()
    print(a.baseInfo)
    # a.buyStock('600960',8.8,400)
    # a.buyNewStock('600960',8.8,400)
    # a.getTodayTrade()
    # a.getHistoryTrade()
    a.sellStock('600960',6.96,200)
