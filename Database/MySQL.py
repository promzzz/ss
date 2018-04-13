import pymysql
import re

class MySQL:
    """docstring for MySQL"""
    def __init__(self,db):

        self.conn = pymysql.connect(db['host'],db['user'],db['password'],'',use_unicode=True, charset='utf8')
        self.cur = self.conn.cursor()

        self.cur.execute("show databases")
        self.databaseList = [db[0] for db in self.cur.fetchall()]

        # 判断数据库是否存在，如果不存在则建立
        if not self.isExistDatabase(db['database']):
            self.cearteDatabase(db['database'])

        # 使用数据库
        self.cur.execute('USE ' + db['database'])
        
        self.cur.execute('SHOW TABLES')
        self.tableList = [table[0] for table in self.cur.fetchall()]

        # self.cur.execute('set wait_timeout=90000')
        # self.cur.execute('set interactive_timeout=90000')
        # self.cur.execute('set global max_allowed_packet=524288000')

    # 判断数据库是否存在
    def isExistDatabase(self,database):
        return True if database in self.databaseList else False

    # 判断数据表是否存在
    def isExistTable(self,table = 'test'):
        return True if table in self.tableList else False

    # 建立数据库
    def cearteDatabase(self,database,drop = False):
        if type(database) is not str or len(database) <= 0: return False
        if self.isExistDatabase(database) and drop is False: return False
        if self.isExistDatabase(database) and drop is True: self.dropDatabase(database)

        self.cur.execute('CREATE DATABASE %s;' % database)
        self.databaseList.append(database)
        return database

    # 删除数据库
    def dropDatabase(self,database):
        self.cur.execute('DROP DATABASE '+database)
        self.databaseList.remove(database)

    # 创建数据表
    def cearteTable(self,table = 'test',fields = {},PRIMARY = [],index=[],drop = False):
        if self.isExistTable(table) and drop is False: return False
        if type(table) is not str or len(table) <= 0: return False

        sqlstr = 'CREATE TABLE `%s` (' % table

        for field, types in fields.items(): sqlstr += '`%s` %s ,' % (field, types)

        if len(PRIMARY) > 0: sqlstr += ' PRIMARY KEY ('

        for field in PRIMARY: sqlstr += '`%s`,' % field

        if len(PRIMARY) > 0: sqlstr = sqlstr[:-1] + '),'

        if len(index) > 0:
            indexName = columns = ''
            for i in index:
                indexName += '_%s' % i
                columns += '`%s`,' % i

            sqlstr += 'INDEX `%s%s` (%s) USING BTREE ' % (table,indexName,columns[:-1])
        else:
            sqlstr = sqlstr[:-1]

        sqlstr += ') ENGINE=MyISAM DEFAULT CHARACTER SET=utf8 COLLATE=utf8_general_ci CHECKSUM=0'

        if drop == True: self.dropTable(table)

        # print(sqlstr)
        self.cur.execute(sqlstr)
        self.tableList.append(table)

    # 删除数据表
    def dropTable(self,table = 'test'):
        self.cur.execute('DROP TABLE '+ table)
        self.tableList.remove(table)

    # 清空数据表
    def truncateTable(self,table):
        self.cur.execute('TRUNCATE '+ table)

    # 增加内容
    def insert(self,table = 'test',value = {}):
        if len(value) == 0: return
        columns = ''
        values = ''
        for key,val in value.items():

            columns += '`%s`,' % key

            if type(val) is str and len(val) == 0 or val is None:
                val = 'NULL'
            else:
                val = "'%s'" % re.sub("'", r"\'", str(val))

            values += '%s,' % val

        sql = 'INSERT INTO `%s` (%s) VALUES (%s)' % (table, columns[:-1], values[:-1])
        # print(sql)
        self.cur.execute(sql)
        #INSERT INTO stock_399001_day VALUES ('1','2','3','4','5','6','7','8','9','0','10')

    def insertAll(self,table = 'test',value = []):
        if len(value) == 0: return

        sql = 'INSERT INTO `%s` (' % table

        columns = ''
        for i in value[0]: columns += '`%s`,' % i

        values = ''
        for i in value:
            values += '('
            for j in i:
                if type(i[j]) is str and len(i[j]) == 0 or i[j] is None:
                    val = 'NULL'
                else:
                    val = "'%s'" % re.sub("'", r"\'", str(i[j]))

                values += '%s,' % val

            values = values[:-1] + '),'

        sql += '%s) VALUES %s' % (columns[:-1], values[:-1])

        self.cur.execute(sql)
        #INSERT INTO  `test`.`test` (`id` ,`x` ,`y`) VALUES ('1',  'aa',  'bb'), ('2',  'cc',  'dd');

    # 更新内容
    def update(self,table = 'test',where = [],value = {}):
        sql = 'UPDATE `%s` SET ' % table
        for key, val in value.items():

            if type(val) is str and len(val) == 0 or val is None:
                val = 'NULL'
            else:
                val = "'%s'" %  re.sub("'", r"\'", str(val))

            sql += '`%s` = %s,' % (key, val)

        sql = sql[:-1] + ' WHERE '

        for field in where: sql += field + ' and '

        # print(sql)
        self.cur.execute(sql[:-5])
        # UPDATE stock_000600_day SET open = 1152.829 WHERE date = '2016-09-18 00:00:00' and high = 23.98

    # 删除内容
    def delete(self,table = 'test',where = []):
        if len(where) == 0: return

        sql = 'DELETE FROM `%s` where ' % table
            
        for field in where: sql += field + ' and '

        self.cur.execute(sql[:-5])

    # 查找内容
    def select(self,table = 'test',fields = [],where = [],order = [],limit = []):

        if len(fields) > 0:
            string = ''
            for field in fields: string += '`%s`,' % field
            fields = string[:-1]
        else:
            fields = '*'

        condition = ''

        if len(where) > 0:
            string = ''
            for field in where: string += field + ' and '
            condition += ' WHERE %s' % string[:-5]

        if len(order) > 0:
            string = ''
            for field in order: string += field + ','
            condition += ' ORDER BY %s' % string[:-1]

        if len(limit) > 1: condition += ' LIMIT %s,%s' % (limit[0],limit[1])

        sqlstr = 'SELECT %s FROM `%s`%s' % (fields, table, condition)
        # print(sqlstr)
        self.cur.execute(sqlstr)
        return self.cur.fetchall()

    def custom(self,sql):
        self.cur.execute(sql)
        return self.cur.fetchall()

    # 获取表字段名
    def getColumns(self,table):
        self.cur.execute('select * from `%s` limit 0,1' % table)
        index = self.cur.description
        return [i[0] for i in index]

    def addColumns(self,table,fields={}):
        if not self.isExistTable(table) or len(fields) <= 0: return False

        sqlstr = 'ALTER TABLE  `%s`' % table

        for field, types in fields.items(): sqlstr += ' ADD `%s` %s,' % (field, types)

        self.cur.execute(sqlstr[:-1])

    def dropColumns(self,table,fields=[]):
        if not self.isExistTable(table) or len(fields) <= 0: return False

        sql = 'ALTER TABLE  `%s`' % table

        for field in fields: sql += 'DROP `%s`,' % field
        
        self.cur.execute(sql[:-1])

    def closeLink(self):
        self.cur.close()  # 关闭游标
        self.conn.close() # 释放数据库资源

if __name__ == '__main__':

    import datetime

    db = {'host':'localhost','user':'root','password':'root','database':'test1'}
    mysql = MySQL(db)
    fields = {
        'id':'int(11) UNSIGNED NOT NULL AUTO_INCREMENT',
        'sid':'int(11) UNSIGNED',
        'name':'varchar(60)',
        'age':'date',
        'reg':'text',
        'regdate':'datetime',
        'rqi':'time',
        'jut':'bigint(20) UNSIGNED',
        'price':'float(7,3)',
        'total':'double(16,4)'
    }
    key = ['id']
    # mysql.cearteTable('text1',fields,key)
    # mysql.truncateTable('text')
    values = [{
            'sid':53,
            'name':'测试的名字1',
            'age':datetime.date(2017,9,15),
            'reg':"56'as'df'af",
            'regdate':datetime.datetime(2017,9,15,16,9,15),
            'rqi':datetime.time(16,9,15),
            'jut':453434854543,
            'price':36.3251,
            'total':123456789.6952132,
        },
        {
            'sid':53,
            'name':'测试的名字2',
            'age':datetime.date(2017,9,15),
            'reg':"56'as'df'af",
            'regdate':datetime.datetime(2017,9,15,16,9,15),
            'rqi':datetime.time(16,9,15),
            'jut':453434854543,
            'price':36.3251,
            'total':123456789.6952132,
        }]
    # mysql.insertAll('text',values)

    # v = {'name':'没有名字'}

    # mysql.update('text',['`id` = 2'],v)
    d = mysql.select('text',['name','sid','id'],[],['id ASC'],[5,5])
    # mysql.addColumns('text',{'fid':'int(11) UNSIGNED'})
    mysql.dropColumns('text',['fid'])
    print(mysql.getColumns('text'))

