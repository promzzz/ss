import sys
import json

path = sys.path[0].replace('\\','/')
x=open('x.json','w')
x.write(json.dumps([{'step':6},{'stp':"侯剑锋"}],ensure_ascii=True))
x.close()
x=open('x.json','r')
print(json.loads(x.read()))
Configure = '%s/Configure/' % path

logdir = '%s/log/' % path
imgdir = '%s/images/' % path
tempdir = '%s/temp/' % path

DBInfo = json.loads(open(Configure+'database.json','r').read())
system = json.loads(open(Configure+'system.json','r').read())
users = json.loads(open(Configure+'users.json','r').read())

print(DBInfo,system)
print(users)

# 数据库设置
# DBInfo = {
#     'host':'localhost',             # 主机地址
#     'user':'postgres',                  # 用户ID
#     'password':'root',              # 用户密码
#     'database':'new_ss',                # 数据库名称
# }
# system = {
#     'display':'GUI',
#     'database':'PostgreSQL',
#     'quotation':'sina',
#     'logdir':'%s/log/' % sys.path[0].replace('\\','/'),                   # 日志记录文件夹
#     'imgdir':'%s/images/' % sys.path[0].replace('\\','/'),                   # 日志记录文件夹
#     'tempdir': '%s/temp/' % sys.path[0].replace('\\','/')
# }
# # 股票账号设置
# user = [
#     # {
#     # 'jobber':'ZXJT',             # 开户证券商
#     # 'userid':'11466081',            # 用户账号(必须)
#     # 'password':'790519',             # 登录密码
#     # 'type':'web',                     # 登录方式(必须)
#     # 'uname':'侯剑锋',                   # 用户名字
#     # 'path':'https://www.csc108.com/', # 软件路径
#     # 'brokerage':0.00027,              # 手续费(必须)
#     # 'stamptax':0.001,                # 印花税(必须)
#     # 'mode':False,                     # 实盘(必须)
#     # 'aotuRun':False,                  # 启动自动运行(必须)
#     # 'status':False                    # 网络状态(必须)
#     # },
#     {
#     'userid':'123456789',            # 用户账号(必须)
#     'brokerage':0.00025,              # 手续费(必须)
#     'stamptax':0.001,                # 印花税(必须)
#     'mode':False,                     # 实盘(必须)
#     'aotuRun':True,                  # 启动自动运行(必须)
#     'status':False                    # 网络状态
#     },
#     {
#     'userid':'987654321',
#     'brokerage':0.0008,
#     'stamptax':0.001,
#     'mode':False,
#     'aotuRun':True,
#     'status':False                    # 网络状态
#     },
#     # {
#     # 'userid':'88888888',
#     # 'brokerage':0.0008,
#     # 'stamptax':0.001,
#     # 'mode':False,
#     # 'aotuRun':True,
#     # 'status':False,
#     # 'dynamic':True
#     # },
#     # {
#     # 'userid':'77777777',
#     # 'brokerage':0.0008,
#     # 'stamptax':0.001,
#     # 'mode':False,
#     # 'aotuRun':False,
#     # 'status':False
#     # }
# ]

# if __name__ == '__main__':

#     print(system)


# # self.userCenter = WanLian.WanLian('C:/wlzq/xiadan.exe','370004758','123128')
# # self.userCenter = WanLian.WanLian('C:/wlzq/xiadan.exe','370004748','882500')
# # self.userCenter = WanLian.WanLian('C:/wlzq/xiadan.exe','370012338','790519')
