import requests
import json
import time,datetime
from xlutils.copy import copy
import xlrd
#import re
'''
条件
'''
conditions = [
        '最高价创新高',
        '最低价创新低',
        '最高价创3日新高',
        '最低价创3日新低',
        '均线多头',
        '5日线上',
        '10日线上',
        '20日线上',
        '30日线上',
        '60日线上',
        '120日线上',
        '250日线上'
    ]
'''
head
'''
def getheaders():
    headers = {
        'Host':'www.iwencai.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zAj0cAEQKOmPYSZ4PWGXP0lNnT5g22nHvewjVAP-CeRTDNlPK'
                          'h-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding':'gzip,deflate',
        'Referer': 'http://www.iwencai.com/stockpick/search?typed=0&preParams=&ts=1&f=1&qs=result_original&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w=2018%2F7%2F5%20%E5%B9%B4%E7%BA%BF%E4%B8%8A&queryarea=',
        'hexin-v': 'Ap--avq0OGnEhzx1GeQN6OVxLfIoBPOfDVn3mjHsOR-VkbHgOdSD9h0oh-xC',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': 'cid=d39902441188593815b9de4a660beafe1512962748; ComputerID=d39902441188593815b9de4a660beafe1512962748; v=Ap--avq0OGnEhzx1GeQN6OVxLfIoBPOfDVn3mjHsOR-VkbHgOdSD9h0oh-xC; guideState=1; PHPSESSID=b9b44bc6f0b2832d1c1d80f334837c15',
        'Connection': 'keep-alive'
    }
    return headers

'''
页面查询 页面数据需解析
'''
#问财页面查询
def geturl(input):
    base = "http://www.iwencai.com/stockpick/search?typed=1&preParams=&ts=1&f=1&qs=result_rewrite&selfsectsn=&querytype=&searchfilter=&tid=stockpick&w="
    return base + ''.join(input)

'''
数据查询 json
'''
#上证成交额
def getszcje():
    return "http://www.iwencai.com/diag/block-detail?pid=12167&codes=000001&codeType=zhishu&info={%22view%22:{%22nolazy%22:1,%22parseArr%22:{%22_v%22:%22new%22,%22dateRange%22:[%2220180705%22,%2220180705%22],%22staying%22:[],%22queryCompare%22:{%22index1%22:%22\u6307\u6570\u7b80\u79f0%22,%22op%22:%22%3E%3E%22,%22opVal%22:%22\u4e0a\u8bc1\u6307\u6570%22},%22comparesOfIndex%22:[]},%22asyncParams%22:{%22tid%22:9834}}}"

def parseszcje(jdata):
    o = jdata['data']['data']['option']['series'][0]['data']
    val = o[-1]
    print('上证成交额:',val)
    return val

#通用url拼接
def commonUrls():
    return "http://www.iwencai.com/stockpick/load-data?typed=1&preParams=&ts=1&f=1&qs=result_rewrite&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w="

def commonUrle():
    return "&queryarea="

def commonUrl(conditions):
    return commonUrls() + ''.join(conditions) + commonUrle()

#通用url解析
def commonParse(jdata):
    if jdata != -1:
        has = jdata and jdata['data'] and jdata['data']['natural'] and jdata['data']['natural']['ck0']
        if has:
            return jdata['data']['natural']['ck0']
    return -1

#isjson
def check_json(str):
    try:
        json.loads(str)
    except ValueError:
        return False
    return True

#send
def send(headers,url):
    code_of_html = requests.get(url,headers=headers)
    if code_of_html.status_code == 200:
        data = code_of_html.text
        o = check_json(data)
        if o:
            return json.loads(data)
    else:
        print('html error:',code_of_html.status_code)
        return -1

#构造实例
def sendCommonByCondition(con):
    headers = getheaders()
    url = commonUrl([con])
    tex = send(headers, url)
    print(tex)
    val = commonParse(tex)
    if val != -1:
        print(con,': ', val)
    return val

#每日统计
def everyday():
    for _index in range(len(conditions)):
        val = sendCommonByCondition(conditions[_index])

#多日统计
def timeday(begin,end,cons):
    xlrd_xls = xlrd.open_workbook('data.xls')
    r_sheet = xlrd_xls.sheet_by_index(0)
    nrows = r_sheet.nrows - 1
    xlutils_xls = copy(xlrd_xls)
    sheet = xlutils_xls.get_sheet(0)

    for i in range((end - begin).days + 1):
        day = begin + datetime.timedelta(days=i)
        if day.weekday() >= 0 and day.weekday() < 5:
            nrows = nrows + 1
            ctime = day.strftime('%Y/%m/%d')
            sheet.write(nrows, 0, ctime)
            for _index in range(len(cons)):
                con = ctime + ' ' + conditions[_index]
                res = sendCommonByCondition(con)
                while res == -1:
                    time.sleep(1)
                    res = sendCommonByCondition(con)
                sheet.write(nrows, _index + 1, res)
                time.sleep(1)
            xlutils_xls.save('data.xls')
    xlutils_xls.save('data.xls')

def szcjl():
    xlrd_xls = xlrd.open_workbook('cjl.xlsx')
    r_sheet = xlrd_xls.sheet_by_index(0)
    nrows = r_sheet.nrows
    ncols = r_sheet.ncols
    xlutils_xls = copy(xlrd_xls)
    sheet = xlutils_xls.get_sheet(0)

    url = getszcje()
    tex = send(getheaders(),url)
    while(tex == -1):
        tex = send(getheaders(), url)
        time.sleep(1)
    val = parseszcje(tex)
    sheet.write(nrows, ncols, val)

    xlutils_xls.save('cjl.xlsx')

#input = []#['条件 ']
#url = geturl(input)
def perform_command():
    #szcjl()
    everyday()
    #timeday(datetime.date(2017,1,1),datetime.date(2018,1,1),conditions)

def do_while():
    sendCommonByCondition('股票简称')
    time.sleep(1780)
    #perform_command()
    '''
    while True:
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        ht = hour == 10 or hour == 11 or (hour == 13 and minute == 30) or hour == 14 or hour == 15
        mt = minute == 0 or minute == 30
        if ht and mt:
            perform_command()
            time.sleep(1780)
'''
do_while()