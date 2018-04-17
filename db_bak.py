# 数据库备份

from Database.MySQL import MySQL
from Database.PostgreSQL import PostgreSQL
import json
import pandas
from datetime import *
import os
import re

from setting import *

DB,DBSet = (MySQL,True) if system['database'] == 'MySQL' else (PostgreSQL,False)

start = datetime.now()

db = DB(DBInfo)

for t in db.tableList:
    columns = db.getColumns(t)
    count = db.custom("SELECT Count(%s) FROM %s" % (columns[0],t))[0][0]

    if count == 0: continue

    string = '", "'.join(columns)

    now = str(datetime.now())[:-7].replace(':','-')
    path = 'e:/JeFF/backup_%s_%s.sql' % (t, now)
    file = open(path, 'w', encoding='utf-8')
    # string = 'INSERT INTO "%s" ("%s") VALUES ('6', 'a'),('5', '3');'
    string = 'INSERT INTO "%s" ("%s") VALUES ' % (t,string)
    file.write(string)
    file = open(path, 'a', encoding='utf-8')

    for i in range(0,count,5000):

        value = db.select(t, columns, limit=[i,5000])
        for v in value:
            x = '('
            for s in v:
                x += '%s,' % s if type(s) is int or type(s) is float else "'%s'," % re.sub("'", r"\'", str(s))
            valueStr = x[:-1] + '),' if len(value) > value.index(v)+1 else x[:-1] + ')'
            file.write(valueStr)
    file.write(';')
    file.close()

end = datetime.now()

print('开始时间：%s 结束时间：%s 共花费时间：%s' %(start, end, end-start))
