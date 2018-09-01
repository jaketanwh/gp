import net
from format import format
import qq
import time
#,datetime
import json
from decimal import *
import pymysql
import re
import beijingtime

FIRST_INIT = 1                          #初始化第一次是否send msg
###############################################################################################
# mysql
###############################################################################################
MYSQL_CONN = 0
def mysql():
    global MYSQL_CONN
    #MYSQL_CONN = pymysql.connect(host='localhost', user='root', password='admin123!', db='gp', port=3306, charset='utf8')
    MYSQL_CONN = pymysql.connect(host='192.168.1.103', user='root', password='Admin123!', db='gp', port=3306, charset='utf8')


def closemysql():
    global MYSQL_CONN
    MYSQL_CONN.close()
    MYSQL_CONN = 0

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


###############################################################################################
# 计算公式
###############################################################################################
class clock:
    def __init__(self):
        self.durtime = 0
        self.durclock = 0

    def start(self):
        self.durtime = time.time()
        self.durclock = time.clock()

    def stop(self):
        print('clock time:' + str(time.clock() - self.durclock))
        print('real time:' + str(time.time() - self.durtime))

def getmax(a,b):
    _a = float(a)
    _b = float(b)
    if _a > _b:
        return _a
    else:
        return _b

###############################################################################################
# 开盘啦
###############################################################################################
#KPL_RUL = 'https://pchis.kaipanla.com/w1/api/index.php'
KPL_RUL = 'https://pchq.kaipanla.com/w1/api/index.php'
KPL_CATCH_LIST = [] #开盘啦缓存列表
def kpl():
    global KPL_RUL
    param = {}
    param['a'] = 'GetPointPlate'
    param['c'] = 'PCArrangeData'
    param['Index'] = '0'
    param['PointType'] = '1,2,3'
    param['st'] = '1'
    #param['Date'] = '2018-07-30'#time.strftime("%Y-%m-%d", time.localtime())#
    param['Token'] = '5905a7ec37fa0f49a74b8bcef802cea7'
    param['UserID'] = '228432'
    res = net.sendpost(KPL_RUL,param)
    if res != -1:
        global KPL_CATCH_LIST,FIRST_INIT
        try:
            data = json.loads(res)
        except Exception as ee:
            print("json error")
            return -1
        for row in data['content']['List']:
            tid = row['Time']
            if tid in KPL_CATCH_LIST:
                continue

            KPL_CATCH_LIST.append(tid)
            comment = row['Comment']
            stock = row['Stock']
            for stk in stock:
                name = stk[1]
                tip = '[' + name + ',' + stk[0] + ',' + str(stk[2]) + '%]'
                comment = comment.replace(name,tip)

            if FIRST_INIT != 1:
                time_local = time.localtime(tid)
                stime = time.strftime("%H:%M:%S", time_local)
                s = '[开盘啦][' + stime + '] ' + comment
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)

KPL_ZLJE_LIST = [] #开盘啦主力净额列表
def kplje():
    global KPL_RUL
    param = {}
    param['a'] = 'KanPanNew'
    param['c'] = 'YiDongKanPan'
    param['Index'] = '0'
    param['Order'] = '9'
    param['st'] = '24'
    param['Token'] = '5905a7ec37fa0f49a74b8bcef802cea7'
    param['UserID'] = '228432'
    res = net.sendpost(KPL_RUL,param)
    if res != -1:
        try:
            data = json.loads(res)
        except Exception as ee:
            print("json error")
            return -1

        global KPL_ZLJE_LIST,FIRST_INIT
        for row in data['List']:
            code = row['stock_code']
            if code in KPL_ZLJE_LIST:
                continue

            ZJJE = row['ZJJE']
            jz = Decimal(ZJJE / 100000000).quantize(Decimal('0.00'))
            jz = '{:g}'.format(float(jz))
            jz = float(jz)
            if jz > 2:
                if FIRST_INIT != 1:
                    s = '[主力净额][' + time.strftime("%H:%M:%S", time.localtime()) + '] ' + row['stock_name'] + ' ' + code + ' 本日净流入' + str(jz) + '亿'
                    qq.senMsgToBuddy(s)
                    qq.sendMsgToGroup(s)
                KPL_ZLJE_LIST.append(code)

###############################################################################################
# 财联社
###############################################################################################
CLS_CATCH_LIST = []  # 财联社缓存列表
CLS_URL = 'https://www.cailianpress.com/'  # 'https://m.cailianpress.com/' 手机版刷新不及时
def cls():
    global CLS_URL
    res = net.send(CLS_URL, 0)
    if res != -1:
        global CLS_CATCH_LIST
        baseinfo = format('__NEXT_DATA__ = ', '\n          module=', res)
        if len(baseinfo) <= 0:
            return
        global FIRST_INIT
        data = json.loads(baseinfo[0])
        dataList = data['props']['initialState']['telegraph']['dataList']
        for info in dataList:
            level = info['level']
            if level == 'B' or level == 'A':
                id = info['id']
                if id not in CLS_CATCH_LIST:
                    CLS_CATCH_LIST.append(id)
                    if FIRST_INIT != 1:
                        ctime = info['ctime']
                        # title = info['title']
                        content = info['content']
                        pat = re.compile(r'<[^>]+>', re.S)
                        content = pat.sub('', content)
                        # modified_time = info['modified_time']
                        ftime = time.strftime("%H:%M:%S", time.localtime(ctime))
                        qq.sendMsgToGroup('[财联社]' + '[' + ftime + ']' + content)

        if len(CLS_CATCH_LIST) > 30:
            CLS_CATCH_LIST.pop()

###############################################################################################
#  同花顺问财
 ###############################################################################################
THS_URL = "http://www.iwencai.com/stockpick/load-data?typed=1&preParams=&ts=1&f=1&qs=result_rewrite&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w=%s&queryarea="
def thsdata(condition):
    global THS_URL
    url = THS_URL % (condition)
    res = net.send(url, 1, 1)
    if res != -1:
        jdata = json.loads(res)
        if jdata and jdata['data'] and jdata['data']['result'] and jdata['data']['result']['result']:
            return jdata['data']['result']['result']
    return -1

THS_TIP_DIC = []                    # 提示列表
def ths(condition):
    res = thsdata(condition)
    if res != -1:
        global FIRST_INIT
        for row in res:
            id = row[0].split('.')[0]
            if id in THS_TIP_DIC:
                continue
            if FIRST_INIT != 1:
                jz = Decimal(row[4] / 100000000).quantize(Decimal('0.00'))
                jz = '{:g}'.format(float(jz))
                jz = float(jz)
                s = '[净额][' + time.strftime("%H:%M:%S", time.localtime()) + '] ' + row[1] + ' ' + id + ' 两小时净流入' + str(jz) + '亿'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)

            THS_TIP_DIC.append(id)


###############################################################################################
GP_CATCH_DIC = {}                       # 股票缓存字典

###############################################################################################
# sina大单
# symbol name ticktime price volume prev_price kind
# 代码 名字 时间 价格 量 上一笔价格 E中性盘 U买盘 D卖盘
# {symbol:"sz300292",name:"吴通控股",ticktime:"15:00:03",price:"3.630",volume:"194700",prev_price:"3.630",kind:"E"
###############################################################################################
SINA_RUL = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_Bill.GetBillList?num=1000&page=1&sort=ticktime&asc=0&volume=%s&type=0"
SINA_BUY_TIP_LIST = []          #主买tip
SINA_SELL_TIP_LIST = []         #主卖tip
def sina(cnt):
    global SINA_RUL
    url = SINA_RUL % (str(cnt))
    res = net.send(url)
    if res == -1:
        return

    global GP_CATCH_DIC,SINA_BUY_TIP_LIST,SINA_SELL_TIP_LIST,FIRST_INIT
    res = res.replace('symbol', '"symbol"')
    res = res.replace('name', '"name"')
    res = res.replace('ticktime', '"ticktime"')
    res = res.replace(',price', ',"price"')
    res = res.replace('volume', '"volume"')
    res = res.replace('prev_price', '"prev_price"')
    res = res.replace('kind:', '"kind":')
    if res == 'null':
        return
    #print(res)
    res = eval(res)
    for row in res:
        kind = row['kind']
        if kind == 'E':
            continue
        code = row['symbol'][2:]
        data = GP_CATCH_DIC.get(code,{})
        _ozsp = float(data.get('ed',0))   # 昨日收盘价格
        cur = float(row['price'])
        prev = float(row['prev_price'])
        volume = float(row['volume'])
        if cur > prev and kind == 'D':
            ctime = row['ticktime']
            sign = ctime + code
            if sign in SINA_BUY_TIP_LIST:
                continue

            SINA_BUY_TIP_LIST.append(sign)
            # 单笔拉升3%
            if _ozsp != 0 and ((cur / _ozsp) - (prev / _ozsp)) > 0.3:
                if FIRST_INIT != 1:
                    s = '[拉盘][' + row['ticktime'] + '] ' + row['name'] + ' ' + code + ' 单笔拉升超3%'
                    qq.senMsgToBuddy(s)
                    qq.sendMsgToGroup(s)

            money = int(volume * cur / 10000)
            if money < 50:
                continue

            #大单主买
            if FIRST_INIT != 1:
                s = '[主买][' + ctime + '] ' + row['name'] + ' ' + code + ' ' + str(int(volume/100)) + '手超大单买盘,金额:' + str(money) + '万元'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)


        elif cur < prev and kind == 'D':
            ctime = row['ticktime']
            sign = ctime + code
            if sign in SINA_SELL_TIP_LIST:
                continue
            SINA_SELL_TIP_LIST.append(sign)

            # 单笔砸盘3%
            if _ozsp != 0 and ((prev / _ozsp) - (cur / _ozsp)) > 0.3:
                if FIRST_INIT != 1:
                    s = '[砸盘][' + row['ticktime'] + '] ' + row['name'] + ' ' + code + ' 单笔砸盘超3%'
                    qq.senMsgToBuddy(s)
                    qq.sendMsgToGroup(s)

            money = int(volume * cur / 10000)
            if money < 500:
                continue

            #大单主卖
            if FIRST_INIT != 1:
                s = '[主卖][' + row['ticktime'] + '] ' + row['name'] + ' ' + code + ' ' + str(int(volume/100)) + '手超大单抛盘,金额:' + str(money) + '万元'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)


###############################################################################################
# main
###############################################################################################
def execute():
    cls()
    bjtime,weekday = beijingtime.get_time()
    if bjtime == -1 or weekday == -1:
        return
    #时间判定
    if weekday == 0 and weekday > 5:
        return
    hour = bjtime.tm_hour
    minute = bjtime.tm_min
    #second = bjtime.tm_sec

    if (hour == 9 and minute > 23) or (hour > 9 and hour < 11) or (hour == 11 and minute < 32) or (hour > 12 and hour < 15) or (hour == 15 and minute < 2):
        #盘中
        sina(50000)
        kpl()
        kplje()

    #ths('过去两小时资金流入大于2亿')

def _init():
    mysql()
    qq.init('2649419635')

def _del():
    closemysql()

def do_while():
    global FIRST_INIT
    while True:
        execute()
        if FIRST_INIT == 1:
            print('init finished')
            #qq.sendMsgToGroup('init finished')
            FIRST_INIT = 2
        time.sleep(3)

if __name__ == "__main__":
    _init()
    do_while()
    _del()

#  2649419635