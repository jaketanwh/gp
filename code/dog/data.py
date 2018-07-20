import tushare as ts
import mysql

def test():
    d = ts.get_tick_data('601318', date='2017-06-26')
    print(d)
    e = ts.get_hist_data('601318', start='2017-06-23', end='2017-06-26')
    print(e)

    hs300 = ts.get_hs300s()
    print(hs300)

    try:
        conn = MySQLdb.connect(user='root')  # cennect the database
        cur = conn.cursor()  # get the cur
        cur.execute('create database if not exists Stock')
        conn.select_db('Stock')
        cur.execute('create table if not exists hs300(code varchar(10),weight integer)')
        hs300 = ts.get_hs300s()  # get all the data and other data will be add to this d
        for cnt in range(0, len(hs300)):  # 将hs300中的数据存储到数据库中
            SQL = 'INSERT INTO hs300 (code,weight) VALUES (%s,%s)' % (hs300['code'][cnt], float(hs300['weight'][cnt]))
            cur.execute(SQL)
        conn.commit()  # 执行上诉操作
        cur.close()
        conn.close()

    except MySQLdb.Error, e:
        print(e)
    "Mysql Error %d: %s" % (e.args[0], e.args[1])

test()