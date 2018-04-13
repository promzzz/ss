import psycopg2
import psycopg2.extras
import re

class PostgreSQL:
    """docstring for PostgreSQL"""
    def __init__(self,db):

        self.conn = psycopg2.connect(database = db['database'], user=db['user'], password=db['password'], host=db['host'], port="5432")
        # self.conn = psycopg2.connect(user=db['user'], password=db['password'], host=db['host'], port="5432")
        # self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.cur = self.conn.cursor()

        self.cur.execute('SELECT datname FROM pg_database;')
        self.databaseList = [db[0] for db in self.cur.fetchall()]

        # print(self.databaseList)

        # 判断数据库是否存在，如果不存在则建立
        # self.cearteDatabase(db['database'])

        # # 使用数据库
        # self.cur.execute('USE ' + db['database'])

        self.cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        self.tableList = [table[0] for table in self.cur.fetchall()]

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
        self.conn.commit()

    # 创建数据表
    def cearteTable(self, table='test', fields={}, primary=[], index=[], drop=False):
        if self.isExistTable(table) and drop is False: return False
        if type(table) is not str or len(table) <= 0: return False

        sqlstr = 'CREATE TABLE public.%s (' % table

        # 数据类型：
        # 整数---smallint、integer和bigint对应int2、int4和int8
        #        serial、bigserial自增的整数分别是4 8
        #        例如：int4 or int4 NOT NULL
        # 小数---float4(7位) float8(17位)
        # 字符---varchar、char和text
        #        例如 varchar(255) char(255) text
        # 日期---date time timestamp timestamptz
        #        例如 date time(6) timestamp(6) timestamptz(6)
        # 布尔---
        # 位串---
        # 数组---
        # 复合---

        for field, types in fields.items(): sqlstr += '"%s" %s,' % (field, types)

        if len(primary) == 0: sqlstr = sqlstr[:-1]

        if len(primary) > 0: sqlstr += ' PRIMARY KEY ('

        for field in primary: sqlstr += '%s,' % field

        if len(primary) > 0: sqlstr = sqlstr[:-1] + ')'

        sqlstr += ');'

        if len(index) > 0:
            indexName = columns = ''
            for i in index:
                indexName += '_%s' % i
                columns += '"%s",' % i

            sqlstr += ' CREATE INDEX "%s%s" ON "%s" USING btree (%s);' % (table, indexName, table, columns[:-1])

        if drop == True: self.dropTable(table)

        # print(sqlstr)
        self.cur.execute(sqlstr)
        self.conn.commit()
        self.tableList.append(table)

    # 删除数据表
    def dropTable(self,table = 'test'):
        self.cur.execute('DROP TABLE '+ table)
        self.tableList.remove(table)
        self.conn.commit()

    # 清空数据表
    def truncateTable(self,table):
        self.cur.execute('TRUNCATE '+table)
        self.conn.commit()

    # 增加内容
    def insert(self,table = 'test',value = {}):
        if len(value) == 0: return
        columns = ''
        values = ''
        for key,val in value.items():
            columns += '"%s",' % key

            if type(val) is str and len(val) == 0 or val is None:
                val = 'NULL'
            else:
                val = "'%s'" %  re.sub("'", r"''", str(val))

            values += '%s,' % val

        sqlstr = 'INSERT INTO %s (%s) VALUES (%s);' % (table, columns[:-1], values[:-1])
        # INSERT INTO "public"."test" ("id", "name") VALUES ('6', 'a');
        # print(sqlstr)
        self.cur.execute(sqlstr)
        result = self.cur.fetchone()[0]
        self.conn.commit()
        return result

    def insertAll(self,table = 'test',value = []):
        if len(value) == 0: return
        sql = 'INSERT INTO %s (' % table

        columns = ''
        for i in value[0]: columns += '"%s",' % i

        values = ''
        for i in value:
            values += '('
            for j in i:
                if type(i[j]) is str and len(i[j]) == 0 or i[j] is None:
                    v = 'NULL'
                else:
                    v = "'%s'" %  re.sub("'", r"''", str(i[j]))
                values += '%s,' % v
            values = values[:-1] +'),'

        sql += '%s) VALUES %s' % (columns[:-1], values[:-1])
        # INSERT INTO "public"."test" ("id", "name") VALUES ('6', 'a'),('5', '3');
        self.cur.execute(sql)
        self.conn.commit()

    # 更新内容
    def update(self,table = 'test',where = [],value = {}):

        sqlstr = 'UPDATE %s SET ' % table
        for key, val in value.items():

            if type(val) is str and len(val) == 0 or val is None:
                val = 'NULL'
            else:
                val = "'%s'" %  re.sub("'", r"''", str(val))

            sqlstr += '"%s" = %s,' % (key, val)

        sqlstr = sqlstr[:-1] +' WHERE '

        for field in where: sqlstr += field + ' and '

        # print(sqlstr[:-5])
        self.cur.execute(sqlstr[:-5])
        self.conn.commit()

    # 删除内容
    def delete(self,table = 'test',where = []):
        if len(where) == 0: return

        sqlstr = 'DELETE FROM %s where ' % table

        for field in where: sqlstr += field + ' and '

        self.cur.execute(sqlstr[:-5])
        self.conn.commit()

    # 查找内容
    def select(self,table = 'test',fields = [],where = [],order = [],limit = []):

        if len(fields) > 0:
            string = ''
            for field in fields: string += '"%s",' % field
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

        if len(limit) > 1: condition += ' LIMIT %s OFFSET %s' % (limit[1],limit[0])

        sqlstr = 'SELECT %s FROM %s%s' % (fields, table, condition)
        # print(sqlstr)
        self.cur.execute(sqlstr)
        self.conn.commit()
        return self.cur.fetchall()

    def custom(self,sql):
        self.cur.execute(sql)
        self.conn.commit()
        return self.cur.fetchall()

    # 获取表字段名
    def getColumns(self,table):
        self.cur.execute('SELECT * FROM %s LIMIT 0 OFFSET 1' % table)
        index = self.cur.description
        return [i[0] for i in index]

    # 添加表字段
    def addColumns(self,table,fields={}):
        if not self.isExistTable(table) or len(fields) <= 0: return False

        sqlstr = 'ALTER TABLE  %s' % table
        for field, types in fields.items():
            sqlstr += ' ADD %s %s,' % (field, types)

        self.cur.execute(sqlstr[:-1])
        self.conn.commit()

    # 删除表字段
    def dropColumns(self,table,fields=[]):
        if not self.isExistTable(table) or len(fields) <= 0: return False

        sqlstr = 'ALTER TABLE %s' % table
        for field in fields:
            sqlstr += ' DROP %s,' % field
        self.cur.execute(sqlstr[:-1])
        self.conn.commit()

    def closeLink(self):
        self.cur.close()  # 关闭游标
        self.conn.close() # 释放数据库资源

if __name__ == '__main__':

    import datetime
    db = {'host':'localhost','user':'postgres','password':'root','database':'test1'}

    psql = PostgreSQL(db)

    # print(psql.databaseList)
    # print(psql.tableList)
    fields = {
        'id':'serial4 NOT NULL',
        'sid':'int4',
        'name':'varchar(60)',
        'age':'char(3)',
        'reg':'text',
        'regdate':'timestamp(6)',
        'rqi':'date',
        'jut':'time(6)',
        'price':'float4',
        'total':'float8'
    }
    key = ['id']
    # psql.cearteTable('e',fields,key)
    # psql.cearteTable('e',fields)
    # psql.dropTable('e')
    # psql.truncateTable('e')
    values = {
        'sid':53,
        'name':'测试的名字',
        'age':'15',
        'reg':'56asd"fa"f',
        'regdate':datetime.datetime(2017,9,15,16,9,15),
        'rqi':datetime.date(2017,9,15),
        'jut':datetime.time(16,9,15),
        'price':36.3251,
        'total':123456789.6952132,
    }
    values2 = {
        'sid':100,
        'name':'测试i"kii的"名字',
    }
    where = ["id = '17'"]

    # psql.insert('e',values)
    # psql.insertAll('e',[values,values2])
    # psql.update('e',where,values2)
    # psql.delete('e',where)
    # a = psql.select('e',[],where,[],[])
    # a = psql.addColumns('e',{'name4':'varchar(60)','name5':'varchar(60)'})
    # a = psql.dropColumns('e',['name4','name5'])
    # a = psql.getColumns('e')
    # a = psql.dropDatabase('test')
    # print(a)