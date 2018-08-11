# coding=utf-8
import re
import time,datetime

def format(pre,last,res):
    _tr = pre + '(.*?)' + last
    return re.findall(_tr, res, re.S | re.M)


def test():

    t = time.time()

    print (t) #原始时间数据
    print (int(t)) #秒级时间戳
    print (int(round(t * 1000))) #毫秒级时间戳

    nowTime = lambda:int(t)
    print (nowTime())


test()