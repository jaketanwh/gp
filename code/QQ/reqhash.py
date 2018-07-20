#! /usr/bin/env python
# coding=utf-8


import win32com.server.util, win32com.client

# 以下代码解决输出乱码问题
import sys

# print sys.getdefaultencoding()
reload(sys)
sys.setdefaultencoding('utf8')


# print sys.getdefaultencoding()

class __PyWinQQJsHash:

    def __init__(self):

        js = win32com.client.Dispatch('MSScriptControl.ScriptControl')
        js.Language = 'JavaScript'
        js.AllowUI = True
        js.AddCode(self.__readJsFile("jsfiles/reqHash.js"))
        self.jsengine = js

    def __readJsFile(self, filename):

        fp = file(filename, 'r')
        lines = ''
        for line in fp:
            lines += line
        return lines

    def __driveJsCode(self, func, paras):

        if paras:
            return self.jsengine.Run(func, paras[0], paras[1])
        else:
            return self.jsengine.Run(func)

    def GetQQHash(self, qqnum, ptwebqq):
        return self.__driveJsCode("GetQQHash", [qqnum, ptwebqq])


QJsHash = __PyWinQQJsHash()