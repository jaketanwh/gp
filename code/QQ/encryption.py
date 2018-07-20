#! /usr/bin/env python
# coding=utf-8


import win32com.server.util, win32com.client
import json

# 以下代码解决输出乱码问题
import sys
from test.test_audioop import datas

# print sys.getdefaultencoding()
reload(sys)
sys.setdefaultencoding('utf8')


# print sys.getdefaultencoding()

class __PyWinQQJsMd5Rsa:

    def __init__(self):

        js = win32com.client.Dispatch('MSScriptControl.ScriptControl')
        js.Language = 'JavaScript'
        js.AllowUI = True
        js.AddCode(self.__readJsFile("jsfiles/loginRsa.js"))
        js.AddCode(self.__readJsFile("jsfiles/loginMd5.js"))
        js.AddCode(self.__readJsFile("jsfiles/loginUtil.js"))
        self.jsengine = js

    def __readJsFile(self, filename):

        fp = file(filename, 'r')
        lines = ''
        for line in fp:
            lines += line
        return lines

    def __driveJsCode(self, func, paras):

        if paras:
            return self.jsengine.Run(func, paras[0], paras[1], paras[2])
        else:
            return self.jsengine.Run(func)

    def GetQQMd5Rsa(self, password, salt, verifycode):
        return self.__driveJsCode("GetQQMd5Rsa", [password, salt, verifycode])


QJsMd5Rsa = __PyWinQQJsMd5Rsa()