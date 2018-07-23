# /usr/bin/env python3
import pymysql

class MySQL(object):
    def __init__(self):
        try:
            self.ip = 'localhost'
            #self.ip = '192.168.1.103'
            self.db = 'gp'
            self.conn = pymysql.connect(
                host=self.ip,
                port=3306,
                user='root',
                passwd='admin123!',
                db=self.db,
                charset='utf8'
            )
        except Exception as e:
            print(e)
        else:
            print('连接成功')
            self.cur = self.conn.cursor()

    def close(self):
        self.cur.close()
        self.conn.close()

    def execute(self,sql):
        print('sql:' + sql)
        return self.cur.execute(sql)

    def create_table(self,tname,tparam):
        sql = 'create table if not exists ' + tname + tparam     # +'(id int, name varchar(10),age int)'
        res = self.cur.execute(sql)

    def add(self,tname,tkey,tparam):  # 增
        sql = 'insert into ' + tname + ' ' + tkey + ' values ' + tparam      #(1,"Tom",18),(2,"Jerry",16),(3,"Hank",24)'
        res = self.cur.execute(sql)
        if res:
            self.conn.commit()
        else:
            self.conn.rollback()
        return res

    def show(self,tname):  # 查
        sql = 'select * from tname'
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print(i)

'''

    def rem(self):  # 删
        sql = 'delete from testtb where id=1'
        res = self.cur.execute(sql)
        if res:
            self.conn.commit()
        else:
            self.conn.rollback()
        print(res)

    def mod(self):  # 改
        sql = 'update testtb set name="Tom Ding" where id=2'
        res = self.cur.execute(sql)
        if res:
            self.conn.commit()
        else:
            self.conn.rollback()
        print(res)



if __name__ == "__main__":
    mysql = MySQL()
    mysql.create_table()
    mysql.add()
    mysql.mod()
    mysql.rem()
    mysql.show()
    mysql.close()
'''