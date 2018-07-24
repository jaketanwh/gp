import tushare as ts
import pandas as pd
import pymysql
import re
import net
#import json
from sqlalchemy import create_engine
#from pandasql import sqldf

######################################################################################
# tools
######################################################################################

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

def getmax(a,b):
    _a = float(a)
    _b = float(b)
    if _a > _b:
        return _a
    else:
        return _b

def getmmin(a, b):
    _a = float(a)
    _b = float(b)
    if _a < _b:
        return _a
    else:
        return _b

######################################################################################
# tushare
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
######################################################################################
#GP_ALL_LIST = []                # tushare全部股票数据
def ts_updatecode(conn):
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

def ts_tosql(code,engine):
    df = ts.get_hist_data(code)  # start=sdate, end=edate
    if df is not None:
        try:
            df.to_sql(code, engine, if_exists='append')
            print(df)
            print("df.to_sql suc")
            return 1
        except Exception as ee:
            print("df.to_sql fialed code:" + code)
            return -1
    else:
        print("股票数据错误 ：" + code)
        return 1
    return -1

#sina二手数据，暂时弃用
def ts_download(conn,engine):
    #ts_updatecode(conn)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM code")
    res = cursor.fetchall()
    for row in res:
        while True:
            code = row[0]
            #if table_exists(cursor,code) == 1:
            #    break
            #while True:
            if ts_tosql(code,engine) == 1:
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

def ts_gethigh():
    df = ts.get_sina_dd('601318',date='2018-07-20')
    df.sort_values(by='volume', ascending=False).head(100)
    print(df)

def testtushare():
    #数据开始结束时间
    #start = '2000-01-01'
    #end = '2018-07-20'
    while ts_download(conn, engine) == 1:
        break
    # ts_gethigh()

######################################################################################
# sina
######################################################################################
SINA_HISTORY_URL = "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=%s&scale=%s&ma=%s&datalen=%s"

#code 代码
#scale 分钟间隔（5、15、30、60、240）
#ma 日均值（5、10、15、20、25）
#len 个数
def sina_get(code,scale,ma,len):
    global SINA_HISTORY_URL
    if int(code) >= 600000:
        symbol = 'sh' + code
    else:
        symbol = 'sz' + code
    url = SINA_HISTORY_URL%(symbol,scale,ma,len)
    res = net.send(url, 0, 0)
    if res != -1:
        res = res.replace('day', '"day"')
        res = res.replace('open', '"open"')
        res = res.replace('low', '"low"')
        res = res.replace('high', '"high"')
        res = res.replace('close', '"close"')
        res = res.replace('volume:', '"volume":')
        res = res.replace('ma_price' + ma, '"ma_price' + ma + '"')
        res = res.replace('ma_volume' + ma, '"ma_volume' + ma + '"')
        return eval(res)
    return -1

def sina_down(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM code")
    res = cursor.fetchall()
    index = 1
    rlen = len(res)
    for row in res:
        print('loading:(' + str(index) + '/' + str(rlen) + ')')
        index = index + 1
        code = row[0]
        ma = '5'
        data = sina_get(code,'240', ma, '1')
        while data == -1:
            data = sina_get(code, '240', ma, '1')

        if table_exists(cursor, code) == 0:
            csql = "CREATE TABLE IF NOT EXISTS `" + code + "`(day text,open float,high float,low float,close float,volume float,ma_price5 float,ma_volume5 float,ma_price10 float,ma_volume10 float,ma_price20 float,ma_volume20 float)"
            cursor.execute(csql)

        for o in data:
            ssql = "SELECT * FROM `"+ code +"` WHERE day = '" + o['day'] + "'"
            has = cursor.execute(ssql)
            if ('ma_price' + ma) in o.keys():
                price = float(o['ma_price' + ma])
            else:
                price = 0
            if ('ma_volume' + ma) in o.keys():
                volme = float(o['ma_volume' + ma])
            else:
                volme = 0
            if has == 0:
                s = "INSERT INTO `" + code + "`(day,open,high,low,close,volume,ma_price" + ma + ",ma_volume" + ma + ") VALUES('%s','%f','%f','%f','%f','%f','%f','%f')"
                sql = s % (o['day'], float(o['open']), float(o['high']), float(o['low']), float(o['close']), float(o['volume']), price,volme)
            else:
                s = "UPDATE `" + code + "` SET open=%f,high=%f,low=%f,close=%f,volume=%f,ma_price" + ma + "=%f,ma_volume" + ma +"=%f WHERE day = '" + o['day'] + "'"
                sql = s % (float(o['open']), float(o['high']), float(o['low']), float(o['close']), float(o['volume']), price,volme)
            cursor.execute(sql)
        conn.commit()
    cursor.close()

######################################################################################
# everyday
######################################################################################
#更新日新高数据
def day_xg(conn):
    print('新高数据开始更新')
    xglist = {}
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM code")
    res = cursor.fetchall()
    lenres = len(res)
    ires = 0
    # 计算日新高
    for row in res:
        ires = ires + 1
        code = row[0]
        if table_exists(cursor, code) == 1:
            cursor.execute("SELECT high FROM `" + code + "` p ORDER BY p.day DESC LIMIT 60")
            _res = cursor.fetchall()
            _day10 = 0
            _day20 = 0
            _day30 = 0
            _day40 = 0
            _day50 = 0
            _day60 = 0
            i = 0
            for _row in _res:
                val = _row[0]
                if i < 10:
                    _day10 = getmax(_day10, val)
                elif i < 20:
                    _day20 = getmax(_day20, val)
                elif i < 30:
                    _day30 = getmax(_day30, val)
                elif i < 40:
                    _day40 = getmax(_day40, val)
                elif i < 50:
                    _day50 = getmax(_day50, val)
                elif i < 60:
                    _day60 = getmax(_day60, val)
                i = i + 1
            _len = len(_res)
            if _len == 60:
                _day20 = getmax(_day10, _day20)
                _day30 = getmax(_day20, _day30)
                _day40 = getmax(_day30, _day40)
                _day50 = getmax(_day40, _day50)
                _day60 = getmax(_day50, _day60)
            elif _len > 50:
                _day20 = getmax(_day10, _day20)
                _day30 = getmax(_day20, _day30)
                _day40 = getmax(_day30, _day40)
                _day50 = getmax(_day40, _day50)
            elif _len > 40:
                _day20 = getmax(_day10, _day20)
                _day30 = getmax(_day20, _day30)
                _day40 = getmax(_day30, _day40)
            elif _len > 30:
                _day20 = getmax(_day10, _day20)
                _day30 = getmax(_day20, _day30)
            elif _len > 20:
                _day20 = getmax(_day10, _day20)

            _daylist = {}
            _daylist['10'] = _day10
            _daylist['20'] = _day20
            _daylist['30'] = _day30
            _daylist['40'] = _day40
            _daylist['50'] = _day50
            _daylist['60'] = _day60
            xglist[code] = _daylist
            print('loading(' + str(ires) + '/' + str(lenres) + ')')

    # 创建xg表
    if table_exists(cursor, 'xg') == 0:
        cursor.execute("CREATE TABLE IF NOT EXISTS xg(code text, h10 float, h20 float, h30 float, h40 float, h50 float, h60 float)")

    # 写入xg表数据
    print('正在写入...')
    for key, value in xglist.items():
        cursor.execute("SELECT * FROM xg WHERE code = "+key)
        res = cursor.fetchall()
        if len(res) == 0:
            cursor.execute("INSERT INTO xg(code,h10,h20,h30,h40,h50,h60) VALUES('%s','%f','%f','%f','%f','%f','%f')"%(key,value['10'],value['20'],value['30'],value['40'],value['50'],value['60']))
        else:
            cursor.execute("UPDATE xg SET h10 = %f, h20 = %f, h30 = %f, h40 = %f, h50 = %f, h60 = %f WHERE code=%s"%(value['10'],value['20'],value['30'],value['40'],value['50'],value['60'],key))

    conn.commit()
    cursor.close()
    print('新高数据更新完成')

#更新平台数据
def day_pt(conn):
    #过去2周数据 每日最高最低价重合 最高最高 最低最低 振幅不超过3%  记录2周最高价
    print('平台数据开始更新')
    xglist = {}
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM code")
    res = cursor.fetchall()
    ires = 0
    lenres = len(res)
    for row in res:
        ires = ires + 1
        print('loading(' + str(ires) + '/' + str(lenres) + ')')
        code = row[0]
        if table_exists(cursor, code) == 1:
            cursor.execute("SELECT high,low FROM `" + code + "` p ORDER BY p.day DESC LIMIT 10")
            _res = cursor.fetchall()
            highlist = []
            lowlist = []
            for _row in _res:
                highlist.append(_row[0])
                lowlist.append(_row[1])
            hmax = max(highlist)
            hmin = min(highlist)
            bh = (hmax - hmin)/hmax < 0.03
            if not bh:
                continue
            lmax = max(lowlist)
            lmin = max(lowlist)
            bl = (lmax - lmin)/lmax < 0.03
            if not bl:
                continue
            hllist = {}
            hllist['high'] = hmax
            hllist['low'] = lmin
            xglist[code] = hllist

    # 创建pt表
    if table_exists(cursor, 'pt') == 1:
        cursor.execute("DROP TABLE pt")
    cursor.execute("CREATE TABLE IF NOT EXISTS pt(code text, high float, low float)")

    # 写入pt表数据
    print('正在写入...')
    for key, value in xglist.items():
        cursor.execute("INSERT INTO pt(code,high,low) VALUES('%s','%f','%f')" % (key, value['high'], value['low']))
    conn.commit()
    cursor.close()
    print('平台数据更新完成')


######################################################################################
# common
######################################################################################
COMMON_TYPE = 1                 #数据接口 1.sina 2.ts
def down(conn):
    global COMMON_TYPE
    if COMMON_TYPE == 1:
        sina_down(conn)

def day(conn):
    #更新新高数据表
    day_xg(conn)
    #更新平台数据
    day_pt(conn)

if __name__ == "__main__":
    #读取mysql连接
    conn = pymysql.connect(host='192.168.1.103', user='root', password='Admin123!', db='gp', port=3306, charset='utf8')
    #conn = pymysql.connect(host='localhost', user='root', password='admin123!', db='gp', port=3306, charset='utf8')
    #写入mysql连接
    #engine = create_engine('mysql://root:Admin123!@192.168.1.103/gp?charset=utf8')
    #engine = create_engine('mysql://root:admin123!@localhost/gp?charset=utf8')
    down(conn)
    day(conn)
    #close
    conn.close()
