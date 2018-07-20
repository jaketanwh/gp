# -*- coding: utf-8 -*-
# 需要先安装pywin32模块
import sys
sys.path.append( r'XXXXXXXXX')
import win32gui
import win32con
import win32clipboard as w
import configparser
import codecs 

def setText( str ):
    w.OpenClipboard()
    w.EmptyClipboard()
    w.SetClipboardData(win32con.CF_UNICODETEXT, str)
    w.CloseClipboard()

class conf():
    def __init__(self ,filename ):
        self.config=configparser.ConfigParser()
        self.config.readfp(codecs.open(filename,"r","utf-8-sig"))
        #self.config.read(filename )
    def get(self , sec , key  ):
        if not sec in self.config.sections():
            return  ''
        return self.config.get(sec , key  )
class windowsop():
    def __init__(self ,config ):
        self.config = config
        setText( self.config.get( 'src' , 'content') )
        self.qqhd = win32gui.FindWindow(None,self.config.get( 'src' , 'handlename') )
    def action(self):
        win32gui.SendMessage(self.qqhd,258,22,2080193)
        win32gui.SendMessage(self.qqhd,770,0,0)

        win32gui.SendMessage(self.qqhd,win32con.WM_KEYDOWN,win32con.VK_RETURN,0)
        win32gui.SendMessage(self.qqhd,win32con.WM_KEYUP,win32con.VK_RETURN,0)
if __name__=='__main__':
    config=conf(r'c:\a.ini')
    ap=windowsop(config)
    ap.action( )