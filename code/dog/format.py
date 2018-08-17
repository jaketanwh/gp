# coding=utf-8
import re
import time,datetime

def format(pre,last,res):
    _tr = pre + '(.*?)' + last
    return re.findall(_tr, res, re.S | re.M)