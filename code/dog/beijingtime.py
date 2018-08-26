import http.client
import time,datetime

def get_webservertime():
    conn = http.client.HTTPConnection('www.baidu.com')
    conn.request("GET", "/")
    r = conn.getresponse()
    # r.getheaders() #获取所有的http头
    ts = r.getheader('date')  # 获取http头date部分
    # 将GMT时间转换成北京时间
    ltime = time.strptime(ts[5:25], "%d %b %Y %H:%M:%S")
    ttime = time.localtime(time.mktime(ltime) + 8 * 60 * 60)
    #dat = "date %u-%02u-%02u" % (ttime.tm_year, ttime.tm_mon, ttime.tm_mday)
    #tm = "time %02u:%02u:%02u" % (ttime.tm_hour, ttime.tm_min, ttime.tm_sec)
    whatday = datetime.datetime(ttime.tm_year, ttime.tm_mon, ttime.tm_mday).strftime("%w")
    return ttime,whatday

def get_time():
    return get_webservertime()