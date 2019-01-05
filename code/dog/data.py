import tushare as ts
import pandas as pd
import pymysql
import re
import net
from decimal import *
#import json
#from sqlalchemy import create_engine
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

def getdt(close,st):
    if st:
        _corl = 1.05
    else:
        _corl = 1.1
    _dtj = Decimal(close / _corl).quantize(Decimal('0.00'))
    _dtj = '{:g}'.format(float(_dtj))
    return float(_dtj)

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
        _list = {}
        for i, row in today.iterrows():
            if row['name'].find('ST') >= 0:
                st = 1
            else:
                st = 0
            _list[row['code']] = st
            #_list.append(row['code'])
            # print('i:'+str(i))
            # print(row)

        # 写入游标
        cursor = conn.cursor()
        # 创建code表
        if table_exists(cursor, 'code') == 0:
            cursor.execute("CREATE TABLE IF NOT EXISTS code(id text,st tinyint(1))")

        # 写入code表数据
        for key, value in _list.items():
            cursor.execute("SELECT * FROM code WHERE id=%s", key)
            res = cursor.fetchall()
            if len(res) == 0:
                print('insert ' + key)
                cursor.execute("INSERT INTO code(id,st) VALUES('%s','%d')" % (key,value))
            else:
                print('update ' + key)
                cursor.execute(("UPDATE code SET st=%d WHERE id = '" + key + "'")%value)

        conn.commit()
        cursor.close()
    return 1


#写入mysql连接
#engine = create_engine('mysql://root:Admin123!@192.168.1.103/gp?charset=utf8')
#engine = create_engine('mysql://root:admin123!@localhost/gp?charset=utf8')
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
SINA_DAY = "2"
#code 代码
#scale 分钟间隔（5、15、30、60、240）
#ma 日均值（5、10、15、20、25）
#len 个数
def sina_get(code,scale,ma,len):
    global SINA_HISTORY_URLs
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
        try:
            rres = eval(res)
        except Exception as ee:
            print("rres faild")
            return -1
        return rres
    return -1

def sina_down(conn):
    global SINA_DAY
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

        data = sina_get(code,'240', ma, SINA_DAY)
        while data == -1:
            data = sina_get(code, '240', ma, SINA_DAY)

        if table_exists(cursor, code) == 0:
            csql = "CREATE TABLE IF NOT EXISTS `" + code + "`(day date,open mediumint unsigned,high mediumint unsigned,low mediumint unsigned,close mediumint unsigned,volume bigint unsigned,ma_price5 mediumint unsigned,ma_volume5 bigint unsigned,ma_price10 mediumint unsigned,ma_volume10 bigint unsigned,ma_price20 mediumint unsigned,ma_volume20 bigint unsigned)"
            cursor.execute(csql)

        for o in data:

            ssql = "SELECT * FROM `"+ code +"` WHERE day = '" + o['day'] + "'"
            has = cursor.execute(ssql)
            if ('ma_price' + ma) in o.keys():
                price = int(float(o['ma_price' + ma]) * 100)
            else:
                price = 0
            if ('ma_volume' + ma) in o.keys():
                volme = int(o['ma_volume' + ma])
            else:
                volme = 0
            if has == 0:
                s = "INSERT INTO `" + code + "`(day,open,high,low,close,volume,ma_price" + ma + ",ma_volume" + ma + ") VALUES('%s','%d','%d','%d','%d','%d','%d','%d')"
                sql = s % (o['day'], int(float(o['open'])*100), int(float(o['high'])*100), int(float(o['low'])*100), int(float(o['close'])*100), int(o['volume']), price,volme)
            else:
                s = "UPDATE `" + code + "` SET open=%d,high=%d,low=%d,close=%d,volume=%d,ma_price" + ma + "=%d,ma_volume" + ma +"=%d WHERE day = '" + o['day'] + "'"
                sql = s % (int(float(o['open'])*100), int(float(o['high'])*100), int(float(o['low'])*100), int(float(o['close'])*100), int(o['volume']), price,volme)
            cursor.execute(sql)
        conn.commit()
    cursor.close()

######################################################################################
# everyday
######################################################################################
#更新日新高数据
def day_xg_calculate(res):
    _day10 = 0
    _day20 = 0
    _day30 = 0
    _day40 = 0
    _day50 = 0
    _day60 = 0
    i = 0
    for _row in res:
        val = _row[0]
        if i < 10:
            _day10 = max(_day10, val)
        elif i < 20:
            _day20 = max(_day20, val)
        elif i < 30:
            _day30 = max(_day30, val)
        elif i < 40:
            _day40 = max(_day40, val)
        elif i < 50:
            _day50 = max(_day50, val)
        elif i < 60:
            _day60 = max(_day60, val)
        i = i + 1
        if i == 60:
            break

    _len = len(res)
    if _len >= 60:
        _day20 = max(_day10, _day20)
        _day30 = max(_day20, _day30)
        _day40 = max(_day30, _day40)
        _day50 = max(_day40, _day50)
        _day60 = max(_day50, _day60)
    elif _len > 50:
        _day20 = max(_day10, _day20)
        _day30 = max(_day20, _day30)
        _day40 = max(_day30, _day40)
        _day50 = max(_day40, _day50)
    elif _len > 40:
        _day20 = max(_day10, _day20)
        _day30 = max(_day20, _day30)
        _day40 = max(_day30, _day40)
    elif _len > 30:
        _day20 = max(_day10, _day20)
        _day30 = max(_day20, _day30)
    elif _len > 20:
        _day20 = max(_day10, _day20)

    _daylist = {}
    _daylist['10'] = _day10
    _daylist['20'] = _day20
    _daylist['30'] = _day30
    _daylist['40'] = _day40
    _daylist['50'] = _day50
    _daylist['60'] = _day60
    return _daylist

def day_xg(xglist,cursor):
    # 创建xg表
    if table_exists(cursor, 'xg') == 0:
        cursor.execute("CREATE TABLE IF NOT EXISTS xg(id text, h10 mediumint unsigned, h20 mediumint unsigned, h30 mediumint unsigned, h40 mediumint unsigned, h50 mediumint unsigned, h60 mediumint unsigned)")

    # 写入xg表数据
    for key, value in xglist.items():
        cursor.execute("SELECT * FROM xg WHERE id = "+key)
        res = cursor.fetchall()
        if len(res) == 0:
            cursor.execute("INSERT INTO xg(id,h10,h20,h30,h40,h50,h60) VALUES('%s','%d','%d','%d','%d','%d','%d')"%(key,value['10'],value['20'],value['30'],value['40'],value['50'],value['60']))
        else:
            cursor.execute("UPDATE xg SET h10 = %d, h20 = %d, h30 = %d, h40 = %d, h50 = %d, h60 = %d WHERE id=%s"%(value['10'],value['20'],value['30'],value['40'],value['50'],value['60'],key))

    print('新高数据更新完成')

#更新平台数据
def day_pt_calculate(res):
    # 过去2周数据 每日最高最低价重合 最高最高 最低最低 振幅不超过3%  记录2周最高价
    highlist = []
    lowlist = []
    i = 0
    for _row in res:
        highlist.append(_row[0])
        lowlist.append(_row[1])
        i = i + 1
        if i == 10:
            break

    hmax = max(highlist)
    hmin = min(highlist)
    bh = (hmax - hmin) / hmax < 0.03
    if not bh:
        return -1

    lmax = max(lowlist)
    lmin = max(lowlist)
    bl = (lmax - lmin) / lmax < 0.03
    if not bl:
        return -1

    hllist = {}
    hllist['high'] = hmax
    hllist['low'] = lmin
    return hllist

def day_pt(ptlist,cursor):
    # 创建pt表
    if table_exists(cursor, 'pt') == 1:
        cursor.execute("DROP TABLE pt")
    cursor.execute("CREATE TABLE IF NOT EXISTS pt(id text, high mediumint unsigned, low mediumint unsigned)")

    # 写入pt表数据
    for key, value in ptlist.items():
        cursor.execute("INSERT INTO pt(id,high,low) VALUES('%s','%d','%d')" % (key, value['high'], value['low']))
    print('平台数据更新完成')

#更新连板数据
def day_lb_calculate(res,st):
    _ban = 0
    _lastclose = 0
    for _row in res:
        _close = _row[2] / 100
        if _lastclose == 0:
            _lastclose = _close
        else:
            _tmp = getdt(_lastclose, st == 1)
            if _tmp == _close:
                _lastclose = _close
                _ban = _ban + 1
            else:
                break
    if _ban > 0:
        return _ban

    return -1

def day_lb(lblist,cursor):
    # 创建lb表
    if table_exists(cursor, 'lb') == 1:
        cursor.execute("DROP TABLE lb")
    cursor.execute("CREATE TABLE IF NOT EXISTS lb(id text, ban tinyint(1))")

    # 写入lb表
    for key, value in lblist.items():
        cursor.execute("INSERT INTO lb(id,ban) VALUES('%s','%d')" % (key, value))

    print('连板数据更新完成')


######################################################################################
# common
######################################################################################
#COMMON_TYPE = 1                 #数据接口 1.sina 2.ts
def down(conn):
    sina_down(conn)

def day(conn):
    xglist = {}         #新高
    ptlist = {}         #平台
    lblist = {}         #连板

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM code")
    res = cursor.fetchall()
    ires = 0
    lenres = len(res)
    for row in res:
        ires = ires + 1
        print('loading(' + str(ires) + '/' + str(lenres) + ')')
        code = row[0]
        st = row[1]
        if table_exists(cursor, code) == 1:
            cursor.execute("SELECT high,low,close FROM `" + code + "` p ORDER BY p.day DESC LIMIT 60")
            res = cursor.fetchall()
            xglist[code] = day_xg_calculate(res)
            _pt = day_pt_calculate(res)
            if _pt != -1:
                ptlist[code] = _pt
            _lb = day_lb_calculate(res,st)
            if _lb != -1:
                lblist[code] =_lb

    #更新新高数据表
    day_xg(xglist,cursor)
    #更新平台数据
    day_pt(ptlist,cursor)
    #更新连板数据
    day_lb(lblist,cursor)

    conn.commit()
    cursor.close()

def update(conn):
    #更新code表
    ts_updatecode(conn)


if __name__ == "__main__":
    #读取mysql连接
    conn = pymysql.connect(host='192.168.1.103', user='root', password='Admin123!', db='gp', port=3306, charset='utf8')
    #conn = pymysql.connect(host='106.14.152.18', user='stockMarket', password='kdarrkmpjX5kCbTe', db='stockMarket', port=3306, charset='utf8')
    #conn = pymysql.connect(host='localhost', user='root', password='admin123!', db='gp', port=3306, charset='utf8')
    update(conn)
    down(conn)
    day(conn)
    conn.close()
