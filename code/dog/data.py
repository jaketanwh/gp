import tushare as ts
import pandas as pd
import pymysql
import re
import logger
from sqlalchemy import create_engine
from pandasql import sqldf

GP_ALL_LIST = []                # 全部股票数据

def table_exists(cursor,table_name):        #这个函数用来判断表是否存在
    sql = "show tables;"
    cursor.execute(sql)
    tables = [cursor.fetchall()]
    table_list = re.findall('(\'.*?\')',str(tables))
    table_list = [re.sub("'",'',each) for each in table_list]
    if table_name in table_list:
        return 1        #存在返回1
    else:
        return 0        #不存在返回0

def readmysql(conn,tname):
    #conn = pymysql.connect(host='localhost', user='root', password='admin123!', db='gp', port=3306,charset='utf8')
    df = pd.read_sql('select * from '+tname,con=conn)
    conn.close()
    return  df


""" 
获取个股历史交易记录 
Parameters ------ 
code:string 股票代码 e.g. 600848 
start:string 开始日期 
format：YYYY-MM-DD 为空时取到API所提供的最早日期数据 
end:string 结束日期 
format：YYYY-MM-DD 为空时取到最近一个交易日数据 
ktype：string 数据类型，D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟，默认为D 
retry_count : int, 默认 3 如遇网络等问题重复执行的次数 
pause : int, 默认 0 重复请求数据过程中暂停的秒数，防止请求间隔时间太短出现的问题 
return ------- 
DataFrame 属性:日期 ，开盘价， 最高价， 收盘价， 最低价， 成交量， 价格变动 ，涨跌幅，5日均价，10日均价，20日均价，5日均量，10日均量，20日均量，换手率 
"""

def updatecode(conn):
    try:
        today = ts.get_today_all()
    except Exception as ee:
        print("today faild")
        return -1

    if today is not None:
        # print(today)
        _list = []
        for i, row in today.iterrows():
            _list.append(row['code'])
            # print('i:'+str(i))
            # print(row)

        # 写入游标
        cursor = conn.cursor()
        # 创建code表
        cursor.execute("CREATE TABLE IF NOT EXISTS code(code text)")
        # 写入code表数据
        for code in _list:
            cursor.execute("SELECT * FROM code WHERE code=%s", code)
            res = cursor.fetchall()
            if len(res) == 0:
                print('insert ' + code)
                cursor.execute("INSERT INTO code(code) VALUES('%s')" % code)

        conn.commit()
        cursor.close()

    return 1

def tosql(code,engine):
    df = ts.get_hist_data(code)  # start=sdate, end=edate
    if df is not None:
        try:
            df.to_sql(code, engine, if_exists='append')
            print("df.to_sql suc")
            return 1
        except Exception as ee:
            print("df.to_sql fialed code:" + code)
            return -1
    else:
        print("股票数据错误 ：" + code)
        return 1
    return -1

def download(conn,engine):
    #updatecode(conn)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM code")
    res = cursor.fetchall()
    for row in res:
        while True:
            code = row[0]
            if table_exists(cursor,code) == 1:
                break

            while True:
                if tosql(code,engine) == 1:
                    break

            break

    '''
    global GP_ALL_LIST


        for code in GP_ALL_LIST:
            df = ts.get_hist_data(code, start=sdate, end=edate)
            if df is not None:
                try:
                    df.to_sql(code, engine, if_exists='append')
                except Exception as ee:
                    print("df.to_sql fialed code:" + code)

'''
    return 1

def gethigh():
    df = ts.get_sina_dd('601318',date='2018-07-20')
    df.sort_values(by='volume', ascending=False).head(100)
    print(df)

if __name__ == "__main__":
    #读取mysql连接
    conn = pymysql.connect(host='localhost', user='root', password='admin123!', db='gp', port=3306, charset='utf8')
    #写入mysql连接
    engine = create_engine('mysql://root:admin123!@localhost/gp?charset=utf8')
    #数据开始结束时间
    #start = '2000-01-01'
    #end = '2018-07-20'
    while download(conn, engine) == 1:
        break
    #gethigh()
    #close
    conn.close()
