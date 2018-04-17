import os, sys
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui

import time
import datetime

from setting import *

class MainInterface(QtWidgets.QWidget):
    startTime = datetime.datetime.now()
    """docstring for MainInterface"""
    def __init__(self, control={}):
        super(MainInterface, self).__init__()
        # self.setGeometry(50, 50, 800, 434)
        self.setGeometry(50, 50, 800, 355)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.start()
        self.timer.timeout.connect(self.onTimerOut)

        self.runInfo = control

        # 系统参数栏
        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")

        # tab标签块
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setObjectName("tabWidget")

        self.sysTimeText = QtWidgets.QLabel(self.groupBox)
        self.sysTimeText.setMaximumSize(QtCore.QSize(48, 16777215))
        self.sysTimeText.setText('系统时间')

        self.runTimeText = QtWidgets.QLabel(self.groupBox)
        self.runTimeText.setMaximumSize(QtCore.QSize(48, 16777215))
        self.runTimeText.setText('运行时间')

        self.netStatusText = QtWidgets.QLabel(self.groupBox)
        self.netStatusText.setMaximumSize(QtCore.QSize(48, 16777215))
        self.netStatusText.setText('网络状态')

        self.status = QtWidgets.QLabel(self.groupBox)
        self.status.setMaximumSize(QtCore.QSize(88, 16777215))

        self.netStatus = QtWidgets.QLabel(self.groupBox)
        self.netStatus.setMaximumSize(QtCore.QSize(17, 16777215))
        self.netStatus.setPixmap(QtGui.QPixmap("%son.png" % imgdir))

        self.startBtn = QtWidgets.QPushButton(self.groupBox)
        self.startBtn.setMaximumSize(QtCore.QSize(60, 16777215))
        self.startBtn.setText("全部开始")
        self.startBtn.clicked.connect(self.runInfo.get('start'))

        self.stopBtn = QtWidgets.QPushButton(self.groupBox)
        self.stopBtn.setMaximumSize(QtCore.QSize(60, 16777215))
        self.stopBtn.setText("全部停止")
        self.stopBtn.clicked.connect(self.runInfo.get('stop'))

        self.exitBtn = QtWidgets.QPushButton(self.groupBox)
        self.exitBtn.setMaximumSize(QtCore.QSize(60, 16777215))
        self.exitBtn.setText("退出系统")
        self.exitBtn.clicked.connect(self.runInfo.get('exit'))

        self.sysTimeLCD = QtWidgets.QLCDNumber(self.groupBox)
        self.sysTimeLCD.setMaximumSize(QtCore.QSize(230, 16777215))
        self.sysTimeLCD.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.sysTimeLCD.setNumDigits(6)
        self.sysTimeLCD.setDigitCount(19)
        self.sysTimeLCD.setMode(QtWidgets.QLCDNumber.Dec)
        self.sysTimeLCD.setSegmentStyle(QtWidgets.QLCDNumber.Flat)

        self.runTimeLCD = QtWidgets.QLCDNumber(self.groupBox)
        self.runTimeLCD.setMaximumSize(QtCore.QSize(106, 16777215))
        self.runTimeLCD.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.runTimeLCD.setNumDigits(6)
        self.runTimeLCD.setDigitCount(10)
        self.runTimeLCD.setMode(QtWidgets.QLCDNumber.Dec)
        self.runTimeLCD.setSegmentStyle(QtWidgets.QLCDNumber.Flat)


        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.addWidget(self.sysTimeText)
        self.horizontalLayout.addWidget(self.sysTimeLCD)
        self.horizontalLayout.addWidget(self.runTimeText)
        self.horizontalLayout.addWidget(self.runTimeLCD)
        self.horizontalLayout.addWidget(self.netStatus)
        self.horizontalLayout.addWidget(self.netStatusText)
        self.horizontalLayout.addWidget(self.status)
        self.horizontalLayout.addWidget(self.startBtn)
        self.horizontalLayout.addWidget(self.stopBtn)
        self.horizontalLayout.addWidget(self.exitBtn)


        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("")
        self.verticalLayout.addWidget(self.groupBox)
        self.verticalLayout.addWidget(self.tabWidget)

    def onTimerOut(self):
        nowTime = datetime.datetime.now()
        runTime = nowTime - self.startTime
        self.sysTimeLCD.display(str(nowTime)[:-7])
        self.runTimeLCD.display(str(runTime)[:-7])

        n = 0
        for i in self.runInfo.get('ces'):
            if i.isActive: n+=1
        self.status.setText('共%s个账户在运行' % n)

    def addSon(self, dicts):
        for key,val in dicts.items(): self.tabWidget.addTab(val, key)

class SubInterface(QtWidgets.QWidget):
    showMessage = QtCore.pyqtSignal(str)

    """docstring for SubInterface"""
    def __init__(self, caseEngine):

        super(SubInterface, self).__init__()

        self.uc = caseEngine.uc
        self.ce = caseEngine

        self.cearteControl()
        self.cearteTable()
        self.cearteMessage()

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.addWidget(self.widget)
        self.verticalLayout.addWidget(self.stockTable)
        self.verticalLayout.addWidget(self.groupBox)

        self.showMessage.connect(self.__updateLogLable)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.start()
        self.timer.timeout.connect(self.__updateStatus)

    def cearteControl(self):

        self.widget = QtWidgets.QWidget(self)
        self.widget.setMaximumSize(QtCore.QSize(16777215, 16777215))

        self.controlBtn = QtWidgets.QPushButton(self.widget)
        self.controlBtn.setMaximumSize(QtCore.QSize(40, 16777215))

        if self.ce.isActive:
            self.controlBtn.setText("停止")
            self.controlBtn.clicked.connect(self.caseStop)
        else:
            self.controlBtn.setText("启动")
            self.controlBtn.clicked.connect(self.caseRun)

        self.usLable = QtWidgets.QLabel(self.widget)
        self.usLable.setMaximumSize(QtCore.QSize(48, 16777215))

        self.taLable = QtWidgets.QLabel(self.widget)
        self.taLable.setMaximumSize(QtCore.QSize(48, 16777215))

        self.totalLabel = QtWidgets.QLabel(self.widget)
        self.totalLabel.setMaximumSize(QtCore.QSize(25, 16777215))
        self.totalLabel.setText("总额")

        self.totalLcd = QtWidgets.QLCDNumber(self.widget)
        self.totalLcd.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.totalLcd.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.totalLcd.setDigitCount(10)
        self.totalLcd.setMode(QtWidgets.QLCDNumber.Dec)
        self.totalLcd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)

        self.amountLabel = QtWidgets.QLabel(self.widget)
        self.amountLabel.setMaximumSize(QtCore.QSize(25, 16777215))
        self.amountLabel.setText("余额")

        self.amountLcd = QtWidgets.QLCDNumber(self.widget)
        self.amountLcd.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.amountLcd.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.amountLcd.setDigitCount(10)
        self.amountLcd.setMode(QtWidgets.QLCDNumber.Dec)
        self.amountLcd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)

        self.prolosLabel = QtWidgets.QLabel(self.widget)
        self.prolosLabel.setMaximumSize(QtCore.QSize(25, 16777215))
        self.prolosLabel.setText("盈亏")

        self.prolosLcd = QtWidgets.QLCDNumber(self.widget)
        self.prolosLcd.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.prolosLcd.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.prolosLcd.setDigitCount(10)
        self.prolosLcd.setMode(QtWidgets.QLCDNumber.Dec)
        self.prolosLcd.setSegmentStyle(QtWidgets.QLCDNumber.Flat)

        self.usilabel = QtWidgets.QLabel(self.widget)
        self.usilabel.setMaximumSize(QtCore.QSize(16, 16777215))

        self.tailabel = QtWidgets.QLabel(self.widget)
        self.tailabel.setMaximumSize(QtCore.QSize(16, 16777215))

        self.lockBtn = QtWidgets.QRadioButton(self.widget)
        self.lockBtn.setMaximumSize(QtCore.QSize(30, 16777215))
        self.lockBtn.setText("锁")

        self.sellBtn = QtWidgets.QPushButton(self.widget)
        self.sellBtn.setMaximumSize(QtCore.QSize(40, 16777215))
        self.sellBtn.setText("清仓")

        self.statusBtn = QtWidgets.QPushButton(self.widget)
        self.statusBtn.setMaximumSize(QtCore.QSize(60, 16777215))
        self.statusBtn.setText("查看状态")
        self.statusBtn.clicked.connect(self.__showStauts)

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 9, 0, 9)
        self.horizontalLayout.addWidget(self.controlBtn)
        self.horizontalLayout.addWidget(self.usilabel)
        self.horizontalLayout.addWidget(self.usLable)
        self.horizontalLayout.addWidget(self.tailabel)
        self.horizontalLayout.addWidget(self.taLable)
        self.horizontalLayout.addWidget(self.lockBtn)
        self.horizontalLayout.addWidget(self.sellBtn)
        self.horizontalLayout.addWidget(self.totalLabel)
        self.horizontalLayout.addWidget(self.totalLcd)
        self.horizontalLayout.addWidget(self.amountLabel)
        self.horizontalLayout.addWidget(self.amountLcd)
        self.horizontalLayout.addWidget(self.prolosLabel)
        self.horizontalLayout.addWidget(self.prolosLcd)
        self.horizontalLayout.addWidget(self.statusBtn)

    def cearteTable(self):

        self.stockTable = QtWidgets.QTableWidget(self)
        self.stockTable.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.stockTable.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.stockTable.setMidLineWidth(0)
        self.stockTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.stockTable.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.stockTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.stockTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.stockTable.setGridStyle(QtCore.Qt.SolidLine)
        self.stockTable.setColumnCount(13)
        self.stockTable.setRowCount(8)
        self.stockTable.setFocusPolicy(False)
        self.stockTable.setFrameShape(False)
        self.stockTable.horizontalHeader().setHighlightSections(False)
        self.stockTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.stockTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.stockTable.horizontalHeader().setStyleSheet("QHeaderView::section {background-color:#d8d8d8;color: black;border: 1px solid #d8d8d8;}")
        self.stockTable.horizontalHeader().setDefaultSectionSize(60)
        self.stockTable.verticalHeader().setVisible(False)
        self.stockTable.verticalHeader().setDefaultSectionSize(27)

    def cearteMessage(self):
        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox)
        self.logLabel = QtWidgets.QLabel(self.groupBox)
        self.horizontalLayout_3.addWidget(self.logLabel)

    def __updateStatus(self):

        pal = 0
        ttl = self.uc.fundPool['employ']
        for tac, pl in self.uc.tpl.items(): pal += pl
        for tac, tl in self.uc.ttl.items(): ttl += tl

        self.totalLcd.display(round(ttl, 2))
        self.prolosLcd.display(round(pal, 2))
        self.amountLcd.display(round(self.uc.fundPool['employ'], 2))

        self.__updateTable(self.uc.tsp)

        if self.uc.info['status']:
            self.usLable.setText("用户在线")
            self.usilabel.setPixmap(QtGui.QPixmap("%son.png" % imgdir))
        else:
            self.usLable.setText("用户离线")
            self.usilabel.setPixmap(QtGui.QPixmap("%soff.png" % imgdir))

        if self.ce.isActive:
            self.taLable.setText("系统运行")
            self.tailabel.setPixmap(QtGui.QPixmap("%son.png" % imgdir))
        else:
            self.taLable.setText("系统停止")
            self.tailabel.setPixmap(QtGui.QPixmap("%soff.png" % imgdir))


    def caseRun(self):
        if not self.ce.isActive:
            self.ce.start()
            self.controlBtn.setText('停止')
            self.controlBtn.clicked.connect(self.caseStop)

    def caseStop(self):
        if self.ce.isActive:
            self.ce.stop()
            self.controlBtn.setText('启动')
            self.controlBtn.clicked.connect(self.caseRun)

    # @QtCore.pyqtSlot(dict)
    def __updateTable(self, tsp):

        stockPool = dict()
        for key, stocks in tsp.items(): stockPool.update(stocks)

        fields = stockPool[list(stockPool.keys())[0]].keys() if len(stockPool) > 0 else []

        self.stockTable.setHorizontalHeaderLabels(fields)
        self.stockTable.setColumnCount(len(fields))
        self.stockTable.setRowCount(len(stockPool))

        row = 0
        for code, stock in stockPool.items():
            column = 0
            for key, val in stock.items():
                val = round(val,2) if type(val) != str else val
                field = QtWidgets.QTableWidgetItem(str(val))
                if type(val) != str and key == 'P&L' and val != 0:
                    color = QtCore.Qt.green if val < 0 else QtCore.Qt.red
                    field.setBackground(color)
                field.setTextAlignment(QtCore.Qt.AlignHCenter |  QtCore.Qt.AlignVCenter)
                self.stockTable.setItem(row, column, field)
                column += 1
            row += 1

        self.stockTable.update()

    @QtCore.pyqtSlot(str)
    def __updateLogLable(self, string = ''):
        self.__record2file(string)
        string = string[:100]+'……' if len(string) > 100 else string
        self.logLabel.setText(string)

    # @QtCore.pyqtSlot()
    def __showStauts(self):
        self.ei = EjectInterface(self.uc.par, self.uc.info['userid'])
        # print(id(self.ei))
        self.ei.show()

    def __record2file(self, string):
        nowTime = datetime.datetime.now()
        file = logdir + self.uc.info['userid'] + '.txt'
        model = 'a' if os.path.isfile(file) else 'w'
        logFile = open(file, model)
        if model == 'a': logFile.write('\n')
        logFile.write('%s_%s' % (nowTime, string))
        logFile.close()


class EjectInterface(QtWidgets.QWidget):
    """docstring for EjectInterface"""
    def __init__(self, par, name=''):
        super(EjectInterface, self).__init__()

        self.setWindowTitle("账号%s参数状态" % name)

        top = self.draWidget(par['set'])
        top = self.draWidget(par['run'],top)

        self.resize(250, top+10)

    def draWidget(self, par, top=0):
        left = 10
        right = 230
        string = '策略：%s的运行参数' if top > 0 else '策略：%s的参数设定'

        for key,val in par.items():
            top += 5

            Label = QtWidgets.QLabel(self)
            Label.setGeometry(left,top,right,25)
            Label.setMaximumSize(QtCore.QSize(right-left, 16777215))
            Label.setText(string % key)

            top += 25

            table = QtWidgets.QTableWidget(self)
            table.setGeometry(left,top,right,len(val)*25)
            table.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
            table.setFrameShadow(QtWidgets.QFrame.Sunken)
            table.setMidLineWidth(0)
            table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
            table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
            table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            table.setGridStyle(QtCore.Qt.SolidLine)
            table.setColumnCount(2)
            table.setColumnWidth(0,200)
            table.setColumnWidth(1,72)
            table.setRowCount(len(val))
            table.setFocusPolicy(False)
            table.setFrameShape(False)

            table.horizontalHeader().setVisible(False)
            table.horizontalHeader().setHighlightSections(False)
            table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            table.horizontalHeader().setStyleSheet("QHeaderView::section {background-color:#d8d8d8;color: black;border: 1px solid #d8d8d8;}")
            table.horizontalHeader().setDefaultSectionSize(60)

            table.verticalHeader().setVisible(False)
            table.verticalHeader().setDefaultSectionSize(27)
            table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

            r = 0
            for k,v in val.items():
                table.setRowHeight(r, 25)
                key = QtWidgets.QTableWidgetItem(str(k))
                table.setItem(r, 0, key)
                value = QtWidgets.QTableWidgetItem(str(v))
                table.setItem(r, 1, value)
                r += 1

            top += len(val)*25

        return top



if __name__ == '__main__':
    parm = {}
    parm['轮动间隔'] = 3
    parm['个股历史'] = 130
    parm['指数比对'] = 20
    parm['盈损历史'] = 250
    parm['预选数目'] = 100
    parm['持仓数量'] = 4

    arm = {}
    arm['轮动'] = 3
    arm['个股'] = 130
    arm['指数'] = 20
    arm['盈损'] = 250
    arm['预选'] = 100
    arm['持仓'] = 4

    app = QtWidgets.QApplication(sys.argv)
    # app.qRegisterMetaType(QVector<int>);
    main = EjectInterface({'set':{'smallValue':parm,'Value':arm},'run':{'smallValue':parm,'Value':arm}})
    # main = MainInterface()

    # main.addTab({'test':SonInterface()})
    main.show()
    sys.exit(app.exec_())