# coding=utf-8
import re


def format(pre,last,res):
    _tr = pre + '(.*?)' + last
    return re.findall(_tr, res, re.S | re.M)
