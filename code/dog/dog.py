import net
from format import format
import qq
import time,datetime
import json
from decimal import *

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
                    ctime = info['ctime']
                    # title = info['title']
                    content = info['content']
                    # modified_time = info['modified_time']
                    ftime = time.strftime("%H:%M:%S", time.localtime(ctime))
                    qq.sendMsgToGroup('[财联社]' + '[' + ftime + ']' + content)
                    CLS_CATCH_LIST.append(id)

        if len(CLS_CATCH_LIST) > 30:
            CLS_CATCH_LIST.pop()


###############################################################################################
# 沪深股票
###############################################################################################
GP_CATCH_DIC = {}                       # 股票缓存字典
GP_ALL_STR_URL_LIST = []                # sina全部股票拼接url
GP_ALL_STR_CNT = 710                    # sina拼接返回最大个数868
GP_URL = 'http://hq.sinajs.cn/list='    # sina财经url

#初始化
def gpinit():
    global GP_ALL_STR_URL_LIST,GP_ALL_STR_CNT,GP_CUR_DATE
    _URL = GP_URL
    cnt = 0
    # load data
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


GP_ZT_LIST = []                         #涨停列表
GP_DT_LIST = []                         #跌停列表
GP_CUR_DATE = 0                         #当前日期 非交易日向前推
FIRST_INIT = 1
#涨停跌停通知
def zd(id):
    global GP_CATCH_DIC,GP_ZT_LIST,GP_DT_LIST,FIRST_INIT
    data = GP_CATCH_DIC[id]
    _o = data['list'][-1]
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
            if FIRST_INIT > 1:
                s = '[测试][' + _o[31] + '] ' + data['name'] + ' ' + id + ' 涨停'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)
            GP_ZT_LIST.append(id)
            return
    else:
        #涨停开板
        if id in GP_ZT_LIST:
            if FIRST_INIT > 1:
                s = '[测试][' + _o[31] + '] ' + data['name'] + ' ' + id + ' 打开涨停板'
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
            if FIRST_INIT > 1:
                s = '[测试][' + _o[31] + '] ' + data['name'] + ' ' + id + ' 跌停'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)
            GP_DT_LIST.append(id)
            return
    else:
        #跌停开板
        if id in GP_DT_LIST:
            if FIRST_INIT > 1:
                s = '[测试][' + _o[31] + '] ' + data['name'] + ' ' + id + ' 打开跌停板'
                qq.senMsgToBuddy(s)
                qq.sendMsgToGroup(s)
            GP_DT_LIST.remove(id)
            return
    #print('  GP_ZT_LIST cnt:' + str(len(GP_ZT_LIST)) + '  GP_DT_LIST cnt:' + str(len(GP_DT_LIST)))
    #print(GP_ZT_LIST)
#股价新高
def xg(id):
    print('')

#每帧获取数据并运行策略
def gp():
    global GP_CATCH_DIC,GP_ALL_STR_URL_LIST,FIRST_INIT
    _clock = clock()
    _clock.start()

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
                if _len > 0 and tmplist[-1][31] == _31:
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

                #名字 开盘价 昨收价 日期只保存一份
                _o[0] = 0
                _o[1] = 0
                _o[2] = 0
                _o[30] = 0

                #GP_CATCH_DIC[_id]['list'][0] = _o
                GP_CATCH_DIC[_id]['list'].append(_o)

                #以下开始每帧策略
                # 3)
                zd(_id)





    #print(GP_CATCH_DIC)
    _clock.stop()
    FIRST_INIT = 2

###############################################################################################
# main
###############################################################################################
def per_command():
    cls()
    gp()


def per_init():
    gpinit()
    qq.init()


def do_while():
    while True:
        per_command()
        time.sleep(3)

if __name__ == "__main__":
    per_init()
    do_while()
