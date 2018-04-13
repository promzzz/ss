#coding:utf-8
# 系统自带包
import os
import time
import datetime

# 第三方扩展包
import win32api  
import win32con
import win32gui
import win32clipboard

from PIL import Image,ImageGrab
import pytesseract

class Client():
    shortcut = {}
    position = {}
    widgetID = {}

    key = {'0':0x30,'1':0x31,'2':0x32,'3':0x33,'4':0x34,'5':0x35,
        '6':0x36,'7':0x37,'8':0x38,'9':0x39,'.':0xBE,
        'F1':0x70,'F2':0x71,'F3':0x72,'F4':0x73,'F5':0x74,'F6':0x75,
        'F7':0x76,'F8':0x77,'F9':0x78,'F10':0x79,'F11':0x7A,'F12':0x7B,
        'Ctrl':0x11,'C':0x43,'N':0x4E,'Y':0x59}

    name = ''

    activeName = ''

    def __init__(self, caseEngine):
        super(Client, self).__init__()
        self.caseEngine = caseEngine
        self.clockEngine = 'caseEngine.clockEngine'
        self.user = caseEngine.userInfo

        self.heartThread = Thread(target=self.__sendHeartBeat, name='heartThread')
        self.heartThread.setDaemon(True)

        self.activeName = self.activeName + '-' + self.user['uname']
        self._init()

    # 扩展初始化函数
    def _init(self):
        pass

    # 保持活力函数
    def keepAlive(self):
        """启动保持在线的进程 """
        if not self.heartThread.is_alive():
            self.isActive = True
            self.heartThread.start()

    def __sendHeartBeat(self):
        while self.isActive:
            if self.clockEngine.trading_state:
                try:
                    status = self.checkStatus()
                    if not status:
                        self.autoLogin()
                except Exception as e:
                    self.caseEngine.userStatus = False
                    self.autoLogin()
                finally:
                    pass
                    # 获取成功后执行
                    self.caseEngine.userStatus = status
                # 隔100秒执行获取资金数据
                time.sleep(60)
            else:
                time.sleep(5)

    def autoLogin(self):
        self.mainPanel = win32gui.FindWindow(None, self.name)
        # print(self.mainPanel)
        if self.mainPanel > 0:
            # 软件已启动
            loginWindows = win32gui.FindWindow(None,'用户登录')
            if loginWindows > 0:
                # 存在登陆界面
                self.login(loginWindows)
                self.getBaseWindows()
            else:
                # 已经登陆
                l, t, r, b = win32gui.GetWindowRect(self.mainPanel)
                if l < 0 and t < 0 and r < 0 and b < 0:
                    activePanel =  win32gui.FindWindow(None, self.activeName)
                    if  activePanel <= 0:
                        height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
                        win32api.SetCursorPos([165,height-10])    #为鼠标焦点设定一个位置
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0,0,0)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0,0,0)

                    time.sleep(0.3)

                    activePanel =  win32gui.FindWindow(None, self.activeName)
                    if activePanel > 0:
                        passwordInput = win32gui.GetDlgItem(activePanel,self.widgetID['activePasswordInput'])
                        activeButton = win32gui.GetDlgItem(activePanel,self.widgetID['activeButton'])
                        win32gui.SendMessage(passwordInput,win32con.WM_SETTEXT,None,self.user['password'])
                        win32gui.SendMessage(activeButton,win32con.BM_CLICK,None,None)
                self.getBaseWindows()
        else:
            os.startfile(self.user['path'])
            time.sleep(2)
            self.autoLogin()

    # 系统登录
    def login(self, handler):
        # 登陆窗口置顶
        win32gui.SetForegroundWindow(handler)
        # 获取登陆输入控件
        try:
            useridInput = win32gui.GetDlgItem(handler, self.widgetID['loginUseridInput'])
            passwordInput = win32gui.GetDlgItem(handler, self.widgetID['loginPasswordInput'])
            codeInput = win32gui.GetDlgItem(handler, self.widgetID['loginCodeInput'])
            identify = win32gui.GetDlgItem(handler, self.widgetID['loginIdentifyPic'])
            loginButton = win32gui.GetDlgItem(handler, self.widgetID['loginButton'])
        except Exception as e:
            pass
        finally:
            # 抓取验证码并识别
            left, top, right, bottom = win32gui.GetWindowRect(identify)
            image = ImageGrab.grab(bbox=(left, top, left+68, bottom))
            identifyCode = pytesseract.image_to_string(image)

            # 发送登陆信息并确定登陆
            win32gui.SendMessage(useridInput,win32con.WM_SETTEXT,None,self.user['userid'])
            win32gui.SendMessage(passwordInput,win32con.WM_SETTEXT,None,self.user['password'])
            win32gui.SendMessage(codeInput,win32con.WM_SETTEXT,None,identifyCode)
            win32gui.SendMessage(loginButton,win32con.BM_CLICK,None,None)

            # 等待2秒钟确定是否能够登陆
            time.sleep(2)

            # 获取错误窗口
            errorWindows = win32gui.FindWindow('#32770','')

            if errorWindows > 0:
                l, t, r, b = win32gui.GetWindowRect(errorWindows)
            if errorWindows > 0 and r-l == 341 and b-t == 182:
                button = win32gui.GetDlgItem(errorWindows,2)
                buttonTitle = win32gui.GetWindowText(button)
                if buttonTitle == '确定':
                    win32gui.SendMessage(button,win32con.BM_CLICK,None,None)
                    win32gui.SendMessage(identify,win32con.BM_CLICK,None,None)
                    # 等待一秒钟重新登陆
                    time.sleep(1)
                    self.login(handler)

    # 获取基本窗口句柄
    def getBaseWindows(self):
        # 子窗口句柄
        self.subPanel = win32gui.GetDlgItem(self.mainPanel, self.widgetID['subPanel'])

        # 工具条句柄
        # self.toolBar = win32gui.GetDlgItem(self.mainPanel, self.widgetID['toolBar'])
        # 状态栏句柄
        # self.statusBar = win32gui.GetDlgItem(self.mainPanel, self.widgetID['statusBar'])

        # 树形菜单句柄
        sonWindows = win32gui.GetDlgItem(self.subPanel, self.widgetID['treeView'][0])
        sonWindows = win32gui.GetDlgItem(sonWindows, self.widgetID['treeView'][1])
        sonWindows = win32gui.GetDlgItem(sonWindows, self.widgetID['treeView'][2])
        self.treeView = win32gui.GetDlgItem(sonWindows, self.widgetID['treeView'][3])

        # if self.subPanel > 0 and self.toolBar > 0 and self.statusBar > 0 and self.treeView > 0:
        #     self.getBaseWindows()

    @property
    def fundInfo(self):
        return self._getfundInfo()

    # 获取用户基本信息
    def _getfundInfo(self):

        # 资金账户面板
        self.pressKey(self.key[self.shortcut['infoPanel']])
        infoPanel = win32gui.GetDlgItem(self.subPanel,  self.widgetID['infoPanel'])

        total = win32gui.GetDlgItem(infoPanel, self.widgetID['infoTotal'])
        surplus = win32gui.GetDlgItem(infoPanel, self.widgetID['infoSurplus'])
        employ = win32gui.GetDlgItem(infoPanel, self.widgetID['infoEmploy'])
        free = win32gui.GetDlgItem(infoPanel, self.widgetID['infoFree'])
        freeze = win32gui.GetDlgItem(infoPanel, self.widgetID['infoFreeze'])
        stockval = win32gui.GetDlgItem(infoPanel, self.widgetID['infoStockVal'])

        # 总资产
        self.fundInfo['total'] = float(win32gui.GetWindowText(total))
        # 资金余额
        self.fundInfo['surplus'] = float(win32gui.GetWindowText(surplus))
        # 可用余额
        self.fundInfo['employ'] = float(win32gui.GetWindowText(employ))
        # 可取金额
        self.fundInfo['free'] = float(win32gui.GetWindowText(free))
        # 冻结金额
        self.fundInfo['freeze'] = float(win32gui.GetWindowText(freeze))
        # 股票市值
        self.fundInfo['stockval'] = float(win32gui.GetWindowText(stockval))

        return self.fundInfo

        # print('您的总资产为：',self.fundInfo['total'])
        # print('您的资金余额为：',self.fundInfo['surplus'])
        # print('您的可用余额为：',self.fundInfo['employ'])
        # print('您的可取金额为：',self.fundInfo['free'])
        # print('您的冻结金额为：',self.fundInfo['freeze'])
        # print('您的股票市值为：',self.fundInfo['stockval'])
    
    @property
    def stockInfo(self):
        return self._getStockInfo()

    # 获取用户在仓票
    def _getStockInfo(self):
        # 资金账户面板
        self.pressKey(self.key[self.shortcut['infoPanel']])

        # 获取股票列表窗口 没用啊，获取到了也拿不到数据只有靠拷贝了
        # listWindows = win32gui.GetDlgItem(infoPanel,1047)
        # listWindows = win32gui.GetDlgItem(listWindows,200)
        # listWindows = win32gui.GetDlgItem(listWindows,1047)

        data = self.copy()
        if data is not None:
            data = data.split('\n')
            for i in range(len(data)):
                if i == 0:
                    columns = data[i].split('\t')[1:-2]
                else:
                    fields = data[i].split('\t')[1:-2]
                    code = data[i].split('\t')[0]
                    lists = {}
                    for i in range(len(fields)):
                        lists[columns[i]] = fields[i]
                    if float(lists['当前持仓']) > 0:
                        self.stockInfo[code] = lists
            return self.stockInfo
            
     
    def buyNewStock(self, stock, price, count):
        # 新股申购
        self.mouseKey(self.position['newStockPanel'][0])
        self.mouseKey(self.position['newStockPanel'][1])
        newStockPanel = win32gui.GetDlgItem(self.subPanel, self.widgetID['newStockPanel'])

        codeInput = win32gui.GetDlgItem(newStockPanel, self.widgetID['newStockCodeInput'])
        priceInput = win32gui.GetDlgItem(newStockPanel, self.widgetID['newStockPriceInput'])
        countInput = win32gui.GetDlgItem(newStockPanel, self.widgetID['newStockCountInput'])
        buyButton = win32gui.GetDlgItem(newStockPanel,  self.widgetID['newStockButton'])

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

    # 获取当天成交数据
    def todayTrade(self):
        self.mouseKey(self.position['todayTradePanel'])
        time.sleep(.5)
        data = self.copy()
        trade = {}
        if data is not None:
            data = data.split('\n')
            for i in range(len(data)):
                if i == 0:
                    columns = data[i].split('\t')[0:-1]
                else:
                    fields = data[i].split('\t')[0:-1]
                    lists = {}

                    for i in range(len(fields)):
                        lists[columns[i]] = fields[i]

                    if fields[1] not in trade.keys():
                        trade[fields[1]] = lists
                    else:
                        trade[fields[1]]['成交数量'] = float(trade[fields[1]]['成交数量']) + float(lists['成交数量'])
                        trade[fields[1]]['成交金额'] = float(trade[fields[1]]['成交金额']) + float(lists['成交金额'])
                        trade[fields[1]]['成交均价'] = trade[fields[1]]['成交金额'] / trade[fields[1]]['成交数量']
        return trade

    # 获取当天委托数据
    def todayEntrust(self):
        self.mouseKey(self.position['todayEntrustPanel'])
        time.sleep(.5)
        data = self.copy()
        trade = {}
        if data is not None:
            data = data.split('\n')
            for i in range(len(data)):
                if i == 0:
                    columns = data[i].split('\t')[0:-1]
                else:
                    fields = data[i].split('\t')[0:-1]
                    lists = {}

                    for i in range(len(fields)):
                        lists[columns[i]] = fields[i]
                    if fields[1] not in trade.keys():
                        trade[fields[1]] = lists
                    else:
                        trade[fields[1]]['成交数量'] = float(trade[fields[1]]['成交数量']) + float(lists['成交数量'])
                        trade[fields[1]]['成交金额'] = float(trade[fields[1]]['成交金额']) + float(lists['成交金额'])
                        trade[fields[1]]['成交均价'] = trade[fields[1]]['成交金额'] / trade[fields[1]]['成交数量']
        return trade

    # 获取历史成交数据
    def historyTrade(self, begin=None, end=None):
        self.mouseKey(self.position['histTradePanel'])

        histTradePanel = win32gui.GetDlgItem(self.subPanel, self.widgetID['histTradePanel'])

        begin = win32gui.GetDlgItem(histTradePanel, self.widgetID['histTradeBeginInput']) # 开始时间
        end = win32gui.GetDlgItem(histTradePanel, self.widgetID['histTradeEndInput']) # 结束时间
        button = win32gui.GetDlgItem(histTradePanel, self.widgetID['histTradeButton']) # 确定按钮

        time.sleep(.5)
        data = self.copy()
        trade = []
        if data is not None:
            data = data.split('\n')
            for i in range(len(data)):
                if i == 0:
                    columns = data[i].split('\t')[0:-1]
                else:
                    fields = data[i].split('\t')[0:-1]
                    lists = {}
                    for i in range(len(fields)):
                        if i < 1:
                            lists['成交时间'] = datetime.datetime.strptime(fields[0]+' '+fields[1],'%Y%m%d %H:%M:%S')
                        if i > 1:
                            lists[columns[i]] = fields[i]
                    if fields[4] != '申购配号':
                        trade.append(lists)
        return trade

    # 获取历史委托数据
    def historyEntrust(self, begin=None, end=None):
        self.mouseKey(self.position['histEntrustPanel'])
        
        histEntrustPanel = win32gui.GetDlgItem(self.subPanel, self.widgetID['histEntrustPanel'])
        begin = win32gui.GetDlgItem(histEntrustPanel, self.widgetID['histEntrustBeginInput']) # 开始时间
        end = win32gui.GetDlgItem(histEntrustPanel, self.widgetID['histEntrustEndInput']) # 结束时间
        button = win32gui.GetDlgItem(histEntrustPanel, self.widgetID['histEntrustButton']) # 确定按钮

        time.sleep(.5)
        data = self.copy()
        trade = []
        if data is not None:
            data = data.split('\n')
            for i in range(len(data)):
                if i == 0:
                    columns = data[i].split('\t')[0:-1]
                else:
                    fields = data[i].split('\t')[0:-1]
                    lists = {}
                    for i in range(len(fields)):
                        if i < 1:
                            lists['成交时间'] = datetime.datetime.strptime(fields[0]+' '+fields[1],'%Y%m%d %H:%M:%S')
                        if i > 1:
                            lists[columns[i]] = fields[i]
                    if fields[4] != '申购配号':
                        trade.append(lists)
        return trade
    
    def newStock(self):
        # 新股申购
        self.mouseKey(self.position['newStockPanel'][0])
        self.mouseKey(self.position['newStockPanel'][1])
        newStockPanel = win32gui.GetDlgItem(self.subPanel, self.widgetID['newStockPanel'])

        time.sleep(.5)

        time.sleep(.5)
        data = self.copy()
        trade = []
        if data is not None:
            data = data.split('\n')
            for i in range(len(data)):
                if i == 0:
                    columns = data[i].split('\t')[0:-1]
                else:
                    fields = data[i].split('\t')[0:-1]
                    lists = {}
                    for i in range(len(fields)):
                        if i < 1:
                            lists['成交时间'] = datetime.datetime.strptime(fields[0]+' '+fields[1],'%Y%m%d %H:%M:%S')
                        if i > 1:
                            lists[columns[i]] = fields[i]
                    if fields[4] != '申购配号':
                        trade.append(lists)
        return trade
        
    # 模拟鼠标点击
    def mouseKey(self, position):
        x = position[0]
        y = position[1]
        # l1=x+y*65536
        lParam = (y << 16) | x
        win32gui.PostMessage(self.treeView,win32con.WM_LBUTTONDOWN,win32con.MK_LBUTTON,lParam)
        win32gui.PostMessage(self.treeView,win32con.WM_LBUTTONUP,0,lParam)
        time.sleep(0.5)

    # 按键程序
    def pressKey(self, key):
        win32api.PostMessage(self.mainPanel, win32con.WM_KEYDOWN, key, None)
        win32api.PostMessage(self.mainPanel, win32con.WM_KEYUP, key, None)
        time.sleep(0.5)

    # 拷贝列表资料函数
    def copy(self):
        # 窗口置顶
        win32gui.SetForegroundWindow(self.mainPanel)
        # 模拟Ctrl+C
        win32api.keybd_event(0x11,0,0,0)      # Ctrl
        win32api.keybd_event(0x43,0,0,0)     # C
        win32api.keybd_event(0x43,0,win32con.KEYEVENTF_KEYUP,0)  #释放按键
        win32api.keybd_event(0x11,0,win32con.KEYEVENTF_KEYUP,0)
        time.sleep(0.5)
        # 打开剪贴板获取内容并关闭
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()

        if '证券代码' not in data and '0' not in data or data == None:
            self.copy()
        else:
            return data

    # 判断窗口是否显示在最顶层
    def isWindowsTop(self):
        topWindows = win32gui.GetForegroundWindow()
        if topWindows == self.mainWindows:
            return True
        else:
            return False
