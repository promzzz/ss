import os, sys, json
from PyQt5.QtWidgets import QApplication

from UserEngine import UserCenter
from DataEngine import DataEngine
from EventEngine import EventEngine
from CaseEngine import CaseEngine
from ClockEngine import ClockEngine
from QuotationEngine import QuotationEngine
from InterfaceEngine import MainInterface
from setting import *

class MainEngine:

    # 主引擎，负责行情、时钟、实例、主界面

    def __init__(self, tzinfo=None):

        string = input('是否添加新账户(y/n):')
        if string == 'y':
            user = {}
            user['userid'] = input('请输入账号:')
            user['mode'] = input('是否为实盘操控(y/n):')
            if user['mode'] == 'y':
                user["jobber"] = input('请输入服务商:')
                user["password"] = input('请输入登录密码:')
                user["type"] = input('请确定操控模式(web/client):')
                user["uname"] = input('请输入用户姓名:')
                user["path"] = input('请输入程序路径:')

            while True:
                user["brokerage"] = input('请确定手续费:')
                try:
                    user["brokerage"] = float(user["brokerage"])
                    if type(user["brokerage"]) == float: break
                except:
                    print('您的输入不正确，请重新输入数字!')

            while True:
                user["stamptax"] = input('请确定印花税:')
                try:
                    user["stamptax"] = float(user["stamptax"])
                    if type(user["stamptax"]) == float: break
                except:
                    print('您的输入不正确，请重新输入数字!')

            user["autoRun"] = input('是否自动运行(y/n):')
            user["show"] = input('是否图形化(y/n):')

            user['mode'] =  True if user["mode"] == 'y' else False
            user["autoRun"] = True if user["autoRun"] == 'y' else False
            user["show"] = True if user["show"] == 'y' else False

            users.append(user)

            uf = open(Configure+'users.json','w')
            uf.write(json.dumps(users))
            uf.close()

        if not os.path.exists(imgdir): os.makedirs(imgdir)
        if not os.path.exists(logdir): os.makedirs(logdir)
        if not os.path.exists(tempdir): os.makedirs(tempdir)

        self.ui = QApplication(sys.argv)

        self.ce = ClockEngine()
        self.qe = QuotationEngine(clockEngine=self.ce)
        self.de = DataEngine()

        # 实例引擎独立数据引擎 若行情引擎未启动则赋予代码库
        if not self.qe.is_active:
            stock = self.de.getStockBaseInfo()
            self.qe.codes = list(stock.index.values)

        self.si = {}
        self.ces = []

        for i in users:
            i['status'] = False
            ce = CaseEngine(UserCenter(i), self.ce, self.qe, self.de)
            self.ces.append(ce)
            if i['show']: self.si[i['userid']] = ce.si

        control = dict(
            start = self.start,
            stop = self.stop,
            exit = self.exit,
            ces = self.ces
            )

        self.MainInterface = MainInterface(control)
        self.MainInterface.addSon(self.si)
        self.MainInterface.show()

        sys.exit(self.ui.exec_())

    def start(self):
        for ce in self.ces:
            if not ce.isActive: ce.start()

    def stop(self):
        for ce in self.ces:
            if ce.isActive: ce.stop()

    def exit(self):
        for ce in self.ces:
            ce.stop()
            ce.eventEngine.stop()
        self.ce.stop()
        self.qe.stop()
        self.ui.quit()

