# 系统自带包
import os,time
import importlib
from threading import Thread, Lock

# 第三方扩展包


# 本系统自定义包

from EventEngine import EventEngine
from InterfaceEngine import SubInterface
import TraderEngine
from setting import system
# from TraderEngine import TraderEngine

class CaseEngine:

    # 实例引擎 负责数据库、策略、下单、实例界面

    def __init__(self, userCenter, clockEngine, quotationEngine, dataEngine):

        self.uc = userCenter

        self.isActive = True if self.uc.info['aotuRun'] else False


        # 载入系统公用时钟引擎、行情引擎、数据引擎
        self.ce = clockEngine
        self.qe = quotationEngine
        self.de = dataEngine

        # 实例本实例事件引擎及窗口引擎、日志引擎
        self.eventEngine = EventEngine()
        if system.get('display') == 'GUI': self.si = SubInterface(self)

        # 最后启动订单引擎
        self.te = TraderEngine.use(self.uc, self.ce)
        if self.uc.info['mode']: self.te.autoLogin()

        # 是否动态加载策略
        self.isDynamic = False if self.uc.info.get('dynamic') is None else self.uc.info.get('dynamic')

        # 保存读取的策略类
        # self.strategies = OrderedDict()
        self.tacticsList = list()

        # 修改时间缓存
        self._cache = {}

        # 文件模块映射
        self._modules = {}
        self._names = None

        # 加载锁
        self.lock = Lock()

        # 加载监控线程
        self._watchThread = Thread(target=self._loadTactics, name="CaseEngine.watchReloadTactics")

        # 初始化载入策略
        self.loadTactics()

        if self.isActive: self.start()

    def start(self):
        # 启动事件引擎
        self.eventEngine.start()

        # 注册时钟引擎
        self.ce.add(self.eventEngine)

        # 注册行情引擎
        self.qe.add(self.eventEngine)

        if self.ce.is_active == False: self.ce.start() # 如有需要启动时钟引擎
        if self.qe.is_active == False: self.qe.start() # 如有需要启动行情引擎
        if self.isDynamic and not self._watchThread.is_alive(): self._watchThread.start() # 如果动态监控策略，则启动监控线程

        # 更改本案列引擎状态为真
        self.isActive = True

    def stop(self):
        self.ce.remove(self.eventEngine)  # 注销时钟引擎
        self.qe.remove(self.eventEngine)  # 注销行情引擎

        # 实盘模式退出登陆
        if self.uc.info['mode']: self.te.logout()

        # 因为线程不支持重复开始，所以其实线程并没有终断循环
        # self.eventEngine.stop()

        # 如时钟引擎再无注册事件引擎，则引擎终止
        # if len(self.ce.eventEngine) == 0: self.ce.stop()

        # 如行情引擎再无注册事件引擎，则引擎终止
        # if len(self.qe.eventEngine) == 0: self.qe.stop()

        # 更改本案列引擎状态为假
        self.isActive = False

    def _loadTactics(self):
        while self.isActive and self.isDynamic:
            try:
                self.loadTactics(self._names)
                time.sleep(2)
            except Exception as e:
                self.si.showMessage.emit(e)

    def loadTactics(self, name=None):
        folder = 'Tacticses' # 策略文件夹
        self._names = name

        # 判断账户策略目录是否存在，不存在则建立
        if not os.path.exists('%s/%s'%(folder, self.uc.info['userid'])):
            os.makedirs('%s/%s'%(folder, self.uc.info['userid']))

        # 获取目录下所有文件列表
        tacticses = os.listdir('%s/%s'%(folder, self.uc.info['userid']))

        # 过滤掉非Python文件和init文件
        tacticses = filter(lambda file: file.endswith('.py') and file != '__init__.py', tacticses)

        # 引入策略账户文件夹
        importlib.import_module('%s.%s'%(folder, self.uc.info['userid']))

        # 循环载入策略文件
        for tactics in tacticses:
            self.loading(self._names, tactics)

        # 如果线程没有启动，就启动策略监视线程
        # if self.isDynamic and not self._watchThread.is_alive():
        #     self._watchThread.start()

    def loading(self, name, tacticsFile):

        with self.lock:
            folder = 'Tacticses'

            # 获取策略文件的修改时间
            mtime = os.path.getmtime(os.path.join('%s/%s'%(folder, self.uc.info['userid']), tacticsFile))

            # 删除策略文件的扩展名
            tacticsModuleName = os.path.basename(tacticsFile)[:-3]

            # 是否需要重新加载
            reload = False

            newModule = lambda tacticsModuleName: importlib.import_module('%s.%s.%s'%(folder, self.uc.info['userid'],tacticsModuleName))
            # print(self.uc.info,'模型列表',self._modules)
            # print(self.uc.info,'重新生成', newModule(tacticsModuleName))
            tacticsModule = self._modules.get(tacticsFile, newModule(tacticsModuleName))
            # print(self._cache)
            if self._cache.get(tacticsFile, None) == mtime:
                # print(self._cache.get(tacticsFile, None),mtime)
                # 检查最后改动时间
                return
            elif self._cache.get(tacticsFile, None) is not None:
                # 注销策略的监听
                # print(tacticsModule.Tactics.name)
                # print(self.tacticsList)
                oldTactics = self.getTactics(tacticsModule.Tactics.name)
                # for i in self.tacticsList: print('循环打印所有策略列表里的策略名称:',i.name)
                # print(oldTactics)
                # print('获取到旧的策略',oldTactics)
                if oldTactics is None:
                    self.si.showMessage.emit(tacticsModuleName)
                    # print(18181818, tacticsModuleName)
                    for s in self.tacticsList:
                        self.si.showMessage.emit(s.name)
                        # print(s.name)
                self.listenEvent(oldTactics, "unlisten")
                self.tacticsList.remove(oldTactics)
                # print('已经注销时间是:',self._cache.get(tacticsFile, None))
                time.sleep(2)
                reload = True

            # 重新加载模块
            if reload:
                tacticsModule = importlib.reload(tacticsModule)

            # 模块加入模块库
            self._modules[tacticsFile] = tacticsModule

            # 获取类名
            tacticsClass = getattr(tacticsModule, 'Tactics')

            if name is None or tacticsClass.name in name:
                # self.strategies[strategy_module_name] = strategy_class
                # 实例化策略类
                newTactics = tacticsClass(self.uc, self.te, self.de, self.ce, self.qe, self.si)
                # 实例化类添加策略列表
                self.tacticsList.append(newTactics)
                # 更新策略文件时间
                self._cache[tacticsFile] = mtime
                # 注册事件处理方法
                self.listenEvent(newTactics, "listen")

    def getTactics(self, name):
        for tactics in self.tacticsList:
            if tactics.name == name:
                return tactics
        return None

    def listenEvent(self, tactics, _type="listen"):
        """
        所有策略要监听的事件都绑定到这里
        :param tactics: Tactics()
        :param _type: "listen" OR "unlisten"
        :return:
        """
        func = {
            "listen": self.eventEngine.register,
            "unlisten": self.eventEngine.unregister,
        }.get(_type)

        # 行情引擎的事件
        func(self.qe.EventType, tactics.run)

        # 时钟事件
        func(self.ce.EventType, tactics.clock)
