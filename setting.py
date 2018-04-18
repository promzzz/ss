import sys
import json

path = sys.path[0].replace('\\','/')

Configure = '%s/Configure/' % path

logdir = '%s/log/' % path
imgdir = '%s/images/' % path
tempdir = '%s/temp/' % path

DBInfo = json.loads(open(Configure+'database.json','r').read())
system = json.loads(open(Configure+'system.json','r').read())
users = json.loads(open(Configure+'users.json','r').read())

# # self.userCenter = WanLian.WanLian('C:/wlzq/xiadan.exe','370004758','123128')
# # self.userCenter = WanLian.WanLian('C:/wlzq/xiadan.exe','370004748','882500')
# # self.userCenter = WanLian.WanLian('C:/wlzq/xiadan.exe','370012338','790519')
