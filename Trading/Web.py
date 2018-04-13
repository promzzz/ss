# coding: utf-8
# 系统自带包
import os
import re
import time
from threading import Thread

# 第三方扩展包
import requests

# 系统自定义包
import sys
sys.path.append('../') 
from Helpers.RelatedTool import *
from Helpers.RelatedTime import *

class NotLoginError(Exception):

    def __init__(self, result=None):
        super(NotLoginError, self).__init__()
        self.result = result


class TradeError(Exception):

    def __init__(self, message=None):
        super(TradeError, self).__init__()
        self.message = message

class Web(object):


    def __init__(self, userCenter, clockEngine):

        self.isActive = False

        self.ce = clockEngine
        self.uc = userCenter

        self.__loadConfig(self.uc.info['jobber'])

        self.S = requests.session()
        self.S.headers.update(self.API['headers'])
      
        self.heartThread = Thread(target=self.__sendHeartBeat, name='heartThread')
        self.heartThread.setDaemon(True)

        self._init()

        self.autoLogin()

    # 扩展初始化函数
    def _init(self):
        pass

    def __loadConfig(self, files):

        self.API = file2dict('%s/config/%s.json' % (os.path.dirname(__file__), files))

    # 自动登录
    def autoLogin(self, limit=10):
        if self.uc.info['mode']:
            # 实现自动登录 param limit: 登录次数限制
            for _ in range(limit):
                if self.login():
                    break
            else:
                raise NotLoginError('登录失败次数过多, 请检查密码是否正确 / 券商服务器是否处于维护中 / 网络连接是否正常')
            self.keepAlive()

    def login(self):
        pass

    # 保持活力函数
    def keepAlive(self):
        """启动保持在线的进程 """
        if not self.heartThread.is_alive():
            self.isActive = True
            self.heartThread.start()

    def __sendHeartBeat(self):
        # 循环检查阀
        while self.isActive:
            if self.ce.trading_state:
                try:
                    status = self.checkStatus()
                    if not status: self.autoLogin()
                except Exception as e:
                    self.uc.info['status'] = False
                    self.autoLogin()
                else:
                    self.uc.info['status'] = status
                finally:
                    pass

                time.sleep(60)
            else:
                if self.uc.info['status'] != False: self.uc.info['status'] = False
                time.sleep(10)

    # 检查状态函数
    def checkStatus(self):
        pass

    def logout(self):
        pass

    

    