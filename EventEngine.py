from collections import defaultdict
from queue import Queue, Empty
from threading import Thread

class Event:
    """事件对象"""
    def __init__(self, eventType, data=None):
        self.eventType = eventType
        self.data = data

class EventEngine:
    """事件驱动引擎"""

    def __init__(self):
        """初始化事件引擎"""
        # 事件队列
        self.__queue = Queue()

        # 事件引擎开关
        self.__active = False
        self.active = False

        # 事件引擎处理线程
        self.__thread = Thread(target=self.__run, name="EventEngine.__thread")

        # 事件字典，key 为时间， value 为对应监听事件函数的列表
        self.__handlers = defaultdict(list)

    def __run(self):
        """启动引擎"""
        while self.__active:
            try:
                event = self.__queue.get(block=True, timeout=1)
                handle_thread = Thread(target=self.__process, name="EventEngine.__process", args=(event,))
                handle_thread.start()
            except Empty:
                pass

    def __process(self, event):
        """事件处理"""
        # 检查该事件是否有对应的处理函数
        if event.eventType in self.__handlers:
            # 若存在,则按顺序将时间传递给处理函数执行
            for handler in self.__handlers[event.eventType]:
                handler(event.data)

    def start(self):
        """引擎启动"""
        self.__active = True
        if not self.__thread.is_alive():
            self.__thread.start()


    def stop(self):
        """停止引擎"""
        self.__active = False
        self.__thread.join()

    def register(self, eventType, handler):
        """注册事件处理函数监听"""
        if handler not in self.__handlers[eventType]:
            self.__handlers[eventType].append(handler)

    def unregister(self, eventType, handler):
        # print(eventType)
        # print(handler)
        """注销事件处理函数"""
        handler_list = self.__handlers.get(eventType)
        # print('获取到',handler_list)
        if handler_list is None:
            return
        if handler in handler_list:
            handler_list.remove(handler)
            # print('清除后', handler_list)
        if len(handler_list) == 0:
            self.__handlers.pop(eventType)

    def put(self, event):
        self.__queue.put(event)

    @property
    def queue_size(self):
        return self.__queue.qsize()
        