import tushare as ts
from sqlalchemy import create_engine

def download(id,sdate,edate,engine):
    #d = ts.get_tick_data('601318', date='2017-06-26')
    #print(d)
    #e = ts.get_hist_data('601318', start='2017-06-23', end='2017-06-26')
    #print(e)

    #hs300 = ts.get_hs300s()
    #print(hs300)

        df = ts.get_hist_data(id,start=sdate,end=edate)
        print(df)
        df.to_sql(id,engine)

        '''
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
        '''


if __name__ == "__main__":
    engine = create_engine('mysql://root:Admin123!@192.168.1.103/gp?charset=utf8')
    download('601318','2017-06-26','2017-06-27',engine)
