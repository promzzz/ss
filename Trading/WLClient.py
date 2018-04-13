# 系统自带包
import os
import time
import datetime

# 第三方扩展包
import win32api  
import win32con
import win32gui
import win32clipboard


from Trading.API import API
from Trading.Client import Client


class WLClient(Client, API):
    
    shortcut = {'infoPanel':'F4','buyPanel':'F1','sellPanel':'F2','cancelPanel':'F3','twowayPanel':'F6'}
    position = {'todayTradePanel':[70,190],'todayEntrustPanel':[70,210],'histTradePanel':[70,225],'histEntrustPanel':[70,245],'newStockPanel':[[70,325],[70,345]]}
    widgetID = {'subPanel':59648,'infoPanel':59649,'buyPanel':59649,'sellPanel':59649,'cancelPanel':59649,'twowayPanel':59649,'treeView':[59648,129,200,129],'toolBar':59392,'statusBar':59393,'loginUseridInput':1011,'loginPasswordInput':1012,'loginCodeInput':1003,'loginIdentifyPic':1499,'loginButton':1006,'infoTotal':1015,'infoSurplus':1012,'infoEmploy':1016,'infoFree':1017,'infoFreeze':1013,'infoStockVal':1014,'activePasswordInput':1039,'activeButton':1,'buyCodeInput':1032,'buyPriceInput':1033,'buyCountInput':1034,'buyButton':1006,'sellCodeInput':1032,'sellPriceInput':1033,'sellCountInput':1034,'sellButton':1006,'buyAndSellYes':6,'buyAndSellNo':7,'histTradePanel':59649,'histTradeBeginInput':1009,'histTradeEndInput':1010,'histTradeButton':1006,'histEntrustPanel':59649,'histEntrustBeginInput':1009,'histEntrustEndInput':1010,'histEntrustButton':1006,'newStockPanel':59649,'newStockCodeInput':1032,'newStockPriceInput':1033,'newStockCountInput':1034,'newStockButton':1006}

    name = '网上股票交易系统5.19'
    activeName = '网上股票交易系统5.19'

    def _buyStock(self, code, price, count):
        # 买入面板
        self.pressKey(self.key[self.shortcut['buyPanel']])
        buyPanel = win32gui.GetDlgItem(self.subPanel, self.widgetID['buyPanel'])

        codeInput = win32gui.GetDlgItem(buyPanel, self.widgetID['buyCodeInput'])
        priceInput = win32gui.GetDlgItem(buyPanel, self.widgetID['buyPriceInput'])
        countInput = win32gui.GetDlgItem(buyPanel, self.widgetID['buyCountInput'])
        buyButton = win32gui.GetDlgItem(buyPanel,  self.widgetID['buyButton'])

        win32gui.SendMessage(codeInput,win32con.WM_SETTEXT,None,str(stock))
        win32gui.SendMessage(priceInput,win32con.WM_SETTEXT,None,str(price))
        win32gui.SendMessage(countInput,win32con.WM_SETTEXT,None,str(count))
        win32gui.PostMessage(buyButton,win32con.BM_CLICK,None,None)

        time.sleep(0.3)

        from handle import gethWnd
        confirmWindows = gethWnd([297,229]) #确认下单窗口
        if confirmWindows is not None:
            yesButton = win32gui.GetDlgItem(confirmWindows, self.widgetID['buyAndSellYes'])
            win32gui.PostMessage(yesButton,win32con.BM_CLICK,None,None)
        confirmWindows = gethWnd([300,197]) #超出涨跌停窗口
        if confirmWindows is not None:
            noButton = win32gui.GetDlgItem(confirmWindows, self.widgetID['buyAndSellNo'])
            win32gui.PostMessage(noButton,win32con.BM_CLICK,None,None)
        time.sleep(1)
        confirmWindows = gethWnd([341,182]) #余额不足窗口
        if confirmWindows is not None:
            noButton = win32gui.GetDlgItem(confirmWindows, 2)
            win32gui.PostMessage(noButton,win32con.BM_CLICK,None,None)

    def _sellStock(self, code, price, count):
        # 卖出面板
        self.pressKey(self.key[self.shortcut['sellPanel']])
        sellPanel = win32gui.GetDlgItem(self.subPanel, self.widgetID['sellPanel'])

        codeInput = win32gui.GetDlgItem(sellPanel, self.widgetID['sellCodeInput'])
        priceInput = win32gui.GetDlgItem(sellPanel, self.widgetID['sellPriceInput'])
        countInput = win32gui.GetDlgItem(sellPanel, self.widgetID['sellCountInput'])
        sellButton = win32gui.GetDlgItem(sellPanel, self.widgetID['sellButton'])

        win32gui.SendMessage(codeInput,win32con.WM_SETTEXT,None,str(stock))
        win32gui.SendMessage(priceInput,win32con.WM_SETTEXT,None,str(price))
        win32gui.SendMessage(countInput,win32con.WM_SETTEXT,None,str(count))
        win32gui.PostMessage(sellButton,win32con.BM_CLICK,None,None)

        time.sleep(0.3)
        from handle import gethWnd
        confirmWindows = gethWnd([297,229])
        if confirmWindows is not None:
            yesButton = win32gui.GetDlgItem(confirmWindows, self.widgetID['buyAndSellYes'])
            win32gui.PostMessage(yesButton,win32con.BM_CLICK,None,None)
        confirmWindows = gethWnd([300,197])
        if confirmWindows is not None:
            noButton = win32gui.GetDlgItem(confirmWindows, self.widgetID['buyAndSellNo'])
            win32gui.PostMessage(noButton,win32con.BM_CLICK,None,None)
        time.sleep(1)
        confirmWindows = gethWnd([341,182]) #余额不足窗口
        if confirmWindows is not None:
            noButton = win32gui.GetDlgItem(confirmWindows, 2)
            win32gui.PostMessage(noButton,win32con.BM_CLICK,None,None)

    def _getTodayTrade(self):
        return self.todayTrade()

    def _getHistoryTrade(self, begin=None, end=None):
        return self.historyTrade(begin,end)
        

if __name__ == '__main__':

    a=WanLian(r'D:\wlzq5.19\xiadan.exe','370004758','123128','蒋鹏')
    a.checkState()
    a.getfundInfo()
    a.buyStock('600960',8.8,400)
    # a.buyNewStock()
    a.getTodayTrade()
    a.getHistoryTrade()
    a.sellStock('600960',6.96,200)
    # print(a.name)