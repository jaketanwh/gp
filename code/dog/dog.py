import net
from format import format
import qq
import time,datetime
import json
from decimal import *
import pymysql
import re

FIRST_INIT = 1
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
        if jdata and jdata['data'] and jdata['data']['natural'] and jdata['data']['natural']['ck0']:
            val = jdata['data']['natural']['ck0']
            print(val)
            return val

THS_TIP_DIC = {}                    # 提示列表
def ths(condition):
    print('send ths')
    val = thsdata(condition)

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
            if money < 100:
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
# 沪深股票
###############################################################################################
GP_ALL_STR_URL_LIST = []                # sina全部股票拼接url
GP_ALL_STR_CNT = 710                    # sina拼接返回最大个数868
GP_URL = 'http://hq.sinajs.cn/list='    # sina财经url

#初始化
def gpinit():
    global GP_ALL_STR_URL_LIST,GP_ALL_STR_CNT,GP_CUR_DATE,GP_XG_DIC,GP_PT_DIC,MYSQL_CONN
    _URL = GP_URL
    cnt = 0

    if MYSQL_CONN != 0:
        # local xg
        cursor = MYSQL_CONN.cursor()
        cursor.execute("SELECT * FROM xg")
        res = cursor.fetchall()
        for row in res:
            rlist = {}
            rlist[10] = row[1]
            rlist[20] = row[2]
            rlist[30] = row[3]
            rlist[40] = row[4]
            rlist[50] = row[5]
            rlist[60] = row[6]
            GP_XG_DIC[row[0]] = rlist

        # local pt
        cursor.execute("SELECT * FROM pt")
        res = cursor.fetchall()
        for row in res:
            rlist = {}
            rlist['high'] = row[1]
            rlist['low'] = row[2]
            GP_PT_DIC[row[0]] = rlist

        cursor.close()



    # load data for sina
    fr = open('gp.txt', 'r',encoding='UTF-8')
    for line in fr:
        tmp = line.split(',')
        dic = {}
        id = tmp[0]
        url = tmp[1] + id
        #dic['url'] = url
        #dic['name'] = tmp[2].replace('\\n','',1)
        dic['list'] = []
        GP_CATCH_DIC[id] = dic
        _URL += url + ','
        cnt = cnt + 1
        if cnt >= GP_ALL_STR_CNT:
            _URL = _URL[:-1]
            GP_ALL_STR_URL_LIST.append(_URL)
            _URL = GP_URL
            cnt = 0

    if cnt > 0:
        _URL = _URL[:-1]
        GP_ALL_STR_URL_LIST.append(_URL)

    lastdate = datetime.date.today()
    oneday = datetime.timedelta(days = 1)
    while lastdate.weekday() > 4:
        lastdate -= oneday
    GP_CUR_DATE = lastdate.strftime('%Y-%m-%d')

#涨停跌停通知
GP_ZT_LIST = []                         #涨停列表
GP_DT_LIST = []                         #跌停列表
GP_CUR_DATE = 0                         #当前日期 非交易日向前推
def zd(id):
    global GP_CATCH_DIC,GP_ZT_LIST,GP_DT_LIST,FIRST_INIT
    data = GP_CATCH_DIC[id]
    _o = data['list']#[-1]
    _ozsp = float(data['ed'])       #昨日收盘价格
    _ocur = float(_o[3])            #当前价格
    _ost = data['st']              #是否st

    #停盘 或 平盘
    if _ozsp == _ocur:
        return

    #涨停
    if _ost:
        _corl = 1.05
    else:
        _corl = 1.1
    _ztj = Decimal(_ozsp * _corl).quantize(Decimal('0.00'))
    _ztj = '{:g}'.format(float(_ztj))
    _ztj = float(_ztj)
    #_ztj = round(_ozsp * _corl,2)
    if _ztj == _ocur:
        #新增涨停板
        if id not in GP_ZT_LIST:
            if FIRST_INIT != 1:
                s = '[涨停][' + _o[31] + '] ' + data['name'] + ' ' + id + ' 冲击涨停'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)
            GP_ZT_LIST.append(id)
            return
    else:
        #涨停开板
        if id in GP_ZT_LIST:
            if FIRST_INIT != 1:
                s = '[开板][' + _o[31] + '] ' + data['name'] + ' ' + id + ' 打开涨停板'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)
            GP_ZT_LIST.remove(id)
            return

    #跌停
    if _ost:
        _corl = 0.95
    else:
        _corl = 0.9
    _dtj = Decimal(_ozsp * _corl).quantize(Decimal('0.00'))
    _dtj = '{:g}'.format(float(_dtj))
    _dtj = float(_dtj)
    #_dtj = round(_ozsp * _corl,2)
    if _dtj == _ocur:
        #新增跌停板
        if id not in GP_DT_LIST:
            if FIRST_INIT != 1:
                s = '[跌停][' + _o[31] + '] ' + data['name'] + ' ' + id + ' 跌停'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)
            GP_DT_LIST.append(id)
            return
    else:
        #跌停开板
        if id in GP_DT_LIST:
            if FIRST_INIT != 1:
                s = '[翘板][' + _o[31] + '] ' + data['name'] + ' ' + id + ' 打开跌停板'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)
            GP_DT_LIST.remove(id)
            return
    #print('  GP_ZT_LIST cnt:' + str(len(GP_ZT_LIST)) + '  GP_DT_LIST cnt:' + str(len(GP_DT_LIST)))
    #print(GP_ZT_LIST)

#股价新高通知
GP_XG_DIC = {}                        # 股票新高记录
GP_XG_TIP_DIC = {}                    # 新高提示列表
def xg(id):
    global GP_CATCH_DIC,GP_XG_DIC,GP_XG_TIP_DIC,FIRST_INIT
    data = GP_CATCH_DIC[id]
    _o = data['list']#[-1]
    #_ocur = float(_o[3])            #当前价格
    _omax = float(_o[4])            # 今日最高价

    #没有数据
    if id not in GP_XG_DIC:
        return

    xgdata = GP_XG_DIC.get(id,{})
    maxkey = 0
    for key, value in xgdata.items():
        if _omax > value and value != 0:
            maxkey = getmax(maxkey,key)

    maxkey = int(maxkey)
    if maxkey == 0 or maxkey == 10 or maxkey == 20:
        return

    if id not in GP_XG_TIP_DIC:
        GP_XG_TIP_DIC[id] = {}

    maxkey = str(maxkey)
    if maxkey not in GP_XG_TIP_DIC[id]:
        GP_XG_TIP_DIC[id][maxkey] = 1
        if FIRST_INIT != 1:
            s = '[新高][' + _o[31] + '] ' + data['name'] + ' ' + id + ' ' + maxkey + '日新高'
            qq.senMsgToBuddy(s)
            qq.sendMsgToGroup(s)


#平台突破通知
GP_PT_DIC = {}            #平台数据
GP_PT_TIP_U_LIST = []       #突破平台提示 向上
GP_PT_TIP_D_LIST = []     #突破平台提示 向下
def pt(id):
    global GP_CATCH_DIC,GP_PT_DIC,GP_PT_TIP_U_LIST,GP_PT_TIP_D_LIST,FIRST_INIT
    data = GP_CATCH_DIC[id]
    _o = data['list']#[-1]
    _ocur = float(_o[3])  # 当前价格

    # 停牌
    if _ocur == 0:
        return

    # 没有数据
    if id not in GP_PT_DIC:
        return
    ptdata = GP_PT_DIC.get(id,{})

    # 向上
    if id not in GP_PT_TIP_U_LIST:
        hightip = ptdata['high'] * 1.1
        if _ocur > hightip:
            GP_PT_TIP_U_LIST.append(id)
            if FIRST_INIT != 1:
                s = '[平台][' + _o[31] + '] ' + data['name'] + ' ' + id + ' 向上平台突破'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)

    # 向下
    if id not in GP_PT_TIP_D_LIST:
        downtip = ptdata['low'] * 0.9
        if _ocur < downtip:
            GP_PT_TIP_D_LIST.append(id)
            if FIRST_INIT != 1:
                s = '[平台][' + _o[31] + '] ' + data['name'] + ' ' + id + ' 向下平台突破'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)


#快速拉升3%以上
GP_KS_TIP_DIC = []          #快速提示记录
def ks(id):
    global GP_CATCH_DIC,GP_KS_TIP_DIC,FIRST_INIT
    if id in GP_KS_TIP_DIC:
        return

    data = GP_CATCH_DIC[id]
    _o = data['list']#[-1]
    _olast = float(data['last'])    # 上次价格
    _ocur = float(_o[3])            # 当前价格
    if _ocur > _olast * 1.3:
        GP_KS_TIP_DIC.append(id)
        if FIRST_INIT != 1:
            s = '[拉升][' + _o[31] + '] ' + data['name'] + ' ' + id + ' 快速拉升超过3%'
            qq.senMsgToBuddy(s)
            qq.sendMsgToGroup(s)


#每帧获取数据并运行策略
def gp():
    global GP_CATCH_DIC,GP_ALL_STR_URL_LIST,FIRST_INIT
    #_clock = clock()
    #_clock.start()

    # TODO 待优化:
    # 1.多线程发送协议,运行策略与请求数据分别进行
    # 2.停盘 新股去除判定
    for url in GP_ALL_STR_URL_LIST:
        res = net.send(url, 0, 0)
        if res != -1:
            first = 1
            first2 = 1
            gpArray = res.split(';')
            for gp in gpArray:
                if len(gp) < 20:
                    continue

                if first == 1:
                    o = gp[13:]
                    first = None
                else:
                    o = gp[14:]

                _id = o[:6]
                data = o[8:][:-1]
                _o = data.split(',')
                _31 = _o[31]  # 时间
                #dic['list'] = []
                tmplist = GP_CATCH_DIC[_id]['list']

                # 1)数据去重
                _len = len(tmplist)
                if _len > 0 and tmplist[31] == _31:#[-1]
                    continue

                # 2)收集数据
                '''
                _0 = _o[0]  # 名字
                _1 = _o[1]  # 今日开盘价
                _2 = _o[2]  # 昨日收盘价
                _3 = _o[3]  # 当前价格
                _4 = _o[4]  # 今日最高价
                _5 = _o[5]  # 今日最低价
                _6 = _o[6]  # 竞买价，即“买一”报价
                _7 = _o[7]  # 竞卖价，即“卖一”报价
                _8 = _o[8]  # 成交的股票数，由于股票交易以一百股为基本单位，所以在使用时，通常把该值除以一百
                _9 = _o[9]  # 成交金额，单位为“元”，为了一目了然，通常以“万元”为成交金额的单位，所以通常把该值除以一万
                _10 = _o[10]  # “买一”申请4695股，即47手
                _11 = _o[11]  # “买一”报价
                _12 = _o[12]  # 买二 申请
                _13 = _o[13]  # 买二 报价
                _14 = _o[14]  # 买三 申请
                _15 = _o[15]  # 买三 报价
                _16 = _o[16]  # 买四 申请
                _17 = _o[17]  # 买四 报价
                _18 = _o[18]  # 买五 申请
                _19 = _o[19]  # 买五 报价
                _20 = _o[20]  # “卖一”申报3100股，即31手
                _21 = _o[21]  # “卖一”报价
                _22 = _o[22]  # 卖二
                _23 = _o[23]  # 卖二
                _24 = _o[24]  # 卖三
                _25 = _o[25]  # 卖三
                _26 = _o[26]  # 卖四
                _27 = _o[27]  # 卖四
                _28 = _o[28]  # 卖五
                _29 = _o[29]  # 卖五
                _30 = _o[30]  # 日期
                _31 = _o[31]  # 时间
                '''
                if _len == 0:
                    _oname = _o[0]
                    GP_CATCH_DIC[_id]['name'] = _oname
                    GP_CATCH_DIC[_id]['st'] = _o[1]
                    GP_CATCH_DIC[_id]['ed'] = _o[2]
                    GP_CATCH_DIC[_id]['date'] = _o[30]
                    GP_CATCH_DIC[_id]['st'] = _oname.find('ST') >= 0
                    GP_CATCH_DIC[_id]['last'] = _o[3]

                #名字 开盘价 昨收价 日期只保存一份
                _o[0] = 0
                _o[1] = 0
                _o[2] = 0
                _o[30] = 0

                GP_CATCH_DIC[_id]['list'] = _o
                #GP_CATCH_DIC[_id]['list'].append(_o)

                #以下开始每帧策略
                # 3)
                zd(_id)

                # 4)
                #xg(_id)

                # 5)
                #pt(_id)

                # 6)
                ks(_id)

                GP_CATCH_DIC[_id]['last'] = _o[3]

    # 7)
    #ths('过去五小时资金流入大于2亿')

    # 8)
    sina(50000)
    #print(GP_CATCH_DIC)
    #_clock.stop()
    FIRST_INIT = 2



###############################################################################################
# main
###############################################################################################
def execute():
    cls()
    gp()


def _init():
    mysql()
    gpinit()
    #qq.init()

def _del():
    closemysql()

def do_while():
    while True:
        execute()
        time.sleep(3)

if __name__ == "__main__":
    _init()
    #_update()
    do_while()
    _del()
