import os, sys
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
            ce = CaseEngine(UserCenter(i), self.ce, self.qe, self.de)
            self.ces.append(ce)
            self.si[i['userid']] = ce.si

        control = dict(
            start = self.start,
            stop = self.stop,
            exit = self.exit,
            ces = self.ces
            )

        if system.get('display') == 'GUI':
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

