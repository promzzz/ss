# coding: utf-8
from threading import Thread
import time

import aiohttp
import dill

from EventEngine import Event
from Quotation import Quotation

class QuotationEngine:
    """行情推送引擎基类"""
    EventType = 'Quotation'  # 事件类型
    PushInterval = 1         # 推送间隔

    def __init__(self, eventEngine = None, clockEngine = None):
        # try:
        #     type(eval('self.eventEngine'))
        # except:
        #     self.eventEngine = []
        #     if eventEngine is not None:
        #         self.eventEngine.append(eventEngine)
        # else:
        #     if eventEngine is not None:
        #         self.eventEngine.append(eventEngine)
        self.eventEngine = []
        
        if eventEngine is not None: self.eventEngine.append(eventEngine)

        self.is_active = True if len(self.eventEngine) > 0 else False
        self.clockEngine = clockEngine
        self.codes = []
        self.source = Quotation.use('sina')
        self.quotation_thread = Thread(target=self.push_quotation, name="Engine.%s" % self.EventType)
        self.quotation_thread.setDaemon(False)

        self.init()

        if self.is_active and len(self.eventEngine)>0 : self.quotation_thread.start()
    def add(self,eventEngine):
        self.eventEngine.append(eventEngine)

    def remove(self,eventEngine):
        if eventEngine in self.eventEngine:
            self.eventEngine.remove(eventEngine)

    def start(self):
        self.is_active = True
        self.quotation_thread.start()

    def stop(self):
        self.is_active = False

    def push_quotation(self):
        while self.is_active:
            if self.clockEngine.trading_state:
                try:
                    response_data = self.source.getAllData(self.codes)
                except:
                # except aiohttp.errors.ServerDisconnectedError:
                    self.wait()
                    continue
                else:
                    event = Event(eventType=self.EventType, data=response_data)
                    for engine in self.eventEngine: engine.put(event)
            self.wait()

    def init(self):
        pass

    def wait(self):
        interval = self.PushInterval
        if interval < 1:
            time.sleep(interval)
            return
        else:
            time.sleep(self.PushInterval - int(interval))
            interval = int(interval)
            while interval > 0 and self.is_active:
                time.sleep(1)
                interval -= 1
