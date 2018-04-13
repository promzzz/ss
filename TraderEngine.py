# coding:utf8
import sys

import platform

# print(platform.architecture())
# print(platform.platform())
# print(platform.system())

os = platform.system()

if os == 'Windows':
    from Trading.WLClient import WLClient
    from Trading.ZXClient import ZXClient
from Trading.ZXJTWeb import ZXJTWeb


PY_VERSION = sys.version_info[:2]
if PY_VERSION < (3, 5):
    raise Exception('Python 版本需要 3.5 或以上, 当前版本为 %s.%s 请升级 Python' % PY_VERSION)
    
def use(userCenter, clockEngine):
    jobber = userCenter.info.get('jobber')
    if jobber in ['WL'] and os == 'Windows':
        return WLClient(userCenter, clockEngine)
    if jobber in ['ZX'] and os == 'Windows':
        return ZXClient(userCenter, clockEngine)
    if jobber in ['ZXJT']:
        return ZXJTWeb(userCenter, clockEngine)

if __name__ == '__main__':
    clockEngine = 'clockEngine'
    a = ZXJTWeb(clockEngine)
    a.autoLogin()
    # print(a.entrustList())
    print(a.fundInfo)
    print(a.stockInfo)