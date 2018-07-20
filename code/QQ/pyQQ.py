#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import random
import re
from encryption import QJsMd5Rsa
from reqhash import QJsHash
import urllib


class WebQQ():

    def __init__(self, user, pwd):
        self.user = user
        self.pwd = pwd
        self.htp = requests.Session()

    def __printlog(self, title, url, text, newcookies, allcookies, data=''):
        print
        '步骤:', title
        print
        '地址:', url
        print
        '发送:', data
        print
        '返回:', text

        print
        '-' * 20, 'cookies', '-' * 20
        print
        '新增:', newcookies
        print
        '所有:', allcookies

        print
        '*' * 49

    def __checkVerify(self):
        url = ('https://ssl.ptlogin2.qq.com/check?pt_tea=1&uin=%s&appid=501004106' % self.user
               + '&r=%s' % str(random.random()))
        r = self.htp.get(url)
        self.__printlog('检查验证码', url, r.text, r.cookies, self.htp.cookies)

        '''
        r.text:

        ptui_checkVC('0','!UCA','\x00\x00\x00\x00\x3a\x02\x14\xcc','8e3d94255c24398ca0efd3b19aebb1386d0ac31b8ca2266267e7f4436d94c6edfb2e8ec953bfb70d731c0efdca63dc030e8d1a120fa2a0b8','0');

        参数 1：“0” 表示不需要验证码，但需要使用随后的缺省验证码来登录。“1” 表示需要验证码。
        参数 2：如果以 “！” 开头则是传递给服务器的缺省验证码。
        参数 3：QQ号码的十六进制格式。(登录加密时会用到)
        参数4：登录参数的 pt_verifysession_v1
        参数6：是否使用随机盐(pt.isRandSalt = c)

        '''

        pattern = re.compile("ptui_checkVC\('(.*)','(.*)','(.*)','(.*)','(.*)'\);")
        checkdatas = pattern.search(r.text).groups()

        self.needpic = checkdatas[0]
        self.verifycode = checkdatas[1]
        self.pt_verifysession_v1 = checkdatas[3]

        #         if self.checkdatas[0] == '1':

    #             print '需要处理密码问题'
    #             pass

    def userLogin(self):
        # 先搞验证码的问题
        self.__checkVerify()

        # 下面开始做密码加密运算，为登录做准备
        rsapwd = QJsMd5Rsa.GetQQMd5Rsa(self.pwd, self.user, self.verifycode)
        #         print rsapwd

        # 密码登录  需要替换4个参数 分别是u=%s&p=%s&verifycode=%s*****pt_verifysession_v1=%s
        url = (
                    'https://ssl.ptlogin2.qq.com/login?u=%s&p=%s&verifycode=%s&webqq_type=10&remember_uin=1&login2qq=1&aid=501004106' % (
            self.user, rsapwd, self.verifycode)
                    + '&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&h=1&ptredirect=0&ptlang=2052&daid=164'
                    + '&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-76-43894&mibao_css=m_webqq&t=3&g=1&js_type=0&js_ver=10126'
                    + '&login_sig=&pt_randsalt=0&pt_vcode_v1=0&pt_verifysession_v1=%s' % self.pt_verifysession_v1)
        ref = (
                    'https://ui.ptlogin2.qq.com/cgi-bin/login?daid=164&target=self&style=16&mibao_css=m_webqq&appid=501004106&enable_qlogin=0'
                    + '&no_verifyimg=1&s_url=http://w.qq.com/proxy.html&f_url=loginerroralert&strong_login=1&login_state=10&t=20131024001')
        headers = {'Accept': 'application/javascript, */*;q=0.8', 'Referer': ref}

        # 这个地方是GET登录
        r = self.htp.get(url, headers=headers)
        self.__printlog('GET登录', url, r.text, r.cookies, self.htp.cookies)

        # 这个值后面需要用到(POST登录的时候)
        self.ptwebqq = r.cookies['ptwebqq']
        #         print ptwebqq

        # 获取密码登录后的回调地址
        # text = '''ptuiCB('0','0','http://ptlogin4.web2.qq.com/check_sig?pttype=1&uin=973214924&service=login&nodirect=0&ptsigx=8be9168e06bf82a19e05108cdce9a5d351aea559057553e6482b68414b364ddc556d468bffedfc35df1f87bb6faca53161e109b1790ad236a36426f8b3d2b232&s_url=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&f_url=&ptlang=2052&ptredirect=100&aid=501004106&daid=164&j_later=0&low_login_hour=0&regmaster=0&pt_login_type=1&pt_aid=0&pt_aaid=0&pt_light=0&pt_3rd_aid=0','0','登录成功！', '旺旺雪饼');'''
        pattern = re.compile("ptuiCB\('(.*)','(.*)','(.*)','(.*)','(.*)',\s+'(.*)'\);")
        logindatas = pattern.search(r.text).groups()
        #         print logindatas

        # 回调成功登录地址（拿到对应的cookies，POST登录的时候要）
        url = logindatas[2]
        r = self.htp.get(url, allow_redirects=False)
        self.__printlog('回调登录返回的地址 拿Cookies', url, r.text, r.cookies, self.htp.cookies)

        # Post Login登录
        url = 'http://d.web2.qq.com/channel/login2'
        datas = 'r={"ptwebqq":"%s","clientid":53999199,"psessionid":"","status":"online"}' % self.ptwebqq
        ref = ('http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2')
        # 'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; WOW64; Trident/7.0; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 1.1.4322; InfoPath.3)'\
        # 这地方一直报错 500 ，尼玛！通过各种抓包对比发现是少了请求头  Content-Type: application/x-www-form-urlencoded
        headers = {'Referer': ref, 'Content-Type': 'application/x-www-form-urlencoded'}

        # POST登录 到这个地方为止  已经成功登录 ，下一步就是去拿好友列表了
        r = self.htp.post(url, data=datas, headers=headers)
        self.__printlog('POST登录', url, r.text, r.cookies, self.htp.cookies, datas)
        # r.text
        '''
            {
            "retcode":0,
            "result":{
                "uin":973214924,
                "cip":1017527010,
                "index":1075,
                "port":58759,
                "status":"online",
                "vfwebqq":"500df48dc767afb6e82d850e795340b16a6e42542bc63890f80fb172c2f7c37b3ec41ad817ad4771",
                "psessionid":"8368046764001d636f6e6e7365727665725f77656271714031302e3133392e372e31363400000b190000106e036e0400cc14023a6d0000000a4077494e50395a55474c6d00000028500df48dc767afb6e82d850e795340b16a6e42542bc63890f80fb172c2f7c37b3ec41ad817ad4771",
                "user_state":0,
                "f":0
            }
        }
        '''
        self.result = json.loads(r.text)
        self.vfwebqq = self.result['result']['vfwebqq']
        self.psessionid = self.result['result']['psessionid']

    def getGroups(self):
        # 获取群组列表
        hashkey = QJsHash.GetQQHash(self.user, self.ptwebqq)
        url = 'http://s.web2.qq.com/api/get_group_name_list_mask2'

        datas = 'r={"vfwebqq":"%s","hash":"%s"}' % (self.vfwebqq, hashkey)
        ref = 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'
        headers = {'Referer': ref, 'Content-Type': 'application/x-www-form-urlencoded'
            ,
                   'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; WOW64; Trident/7.0; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 1.1.4322; InfoPath.3)'
            , 'Accept-Language': 'zh-CN,zh;q=0.8'
            , 'Origin': 'http://s.web2.qq.com'}

        # 去拿群组列表
        r = self.htp.post(url, data=datas, headers=headers)
        self.__printlog('获取群组列表', url, r.text, r.cookies, self.htp.cookies, datas)

        self.groups = json.loads(r.text)

        '''
        {
        "retcode":0,
        "result":{
            "gmasklist":[
            ],
            "gnamelist":[
                {
                    "flag":17826817,
                    "name":"20班",
                    "gid":2019657155,
                    "code":707730478
                },
                {
                    "flag":1090520065,
                    "name":"低调点",
                    "gid":4242729568,
                    "code":3367636394
                }
            ],
            "gmarklist":[
            ]
        }
    }
    '''

    def getFriends(self):
        # 获取好友列表
        # hash算法 不对，一次哈希还不行。得到的值不对，拿不到好友列表
        # 搞错对象，Hash用的是ptwebqq值
        hashkey = QJsHash.GetQQHash(self.user, self.ptwebqq)
        url = 'http://s.web2.qq.com/api/get_user_friends2'

        # 获取自己的详细信息
        datas = 'r={"vfwebqq":"%s","hash":"%s"}' % (self.vfwebqq, hashkey)
        ref = 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'
        # 这地方一直报错 500 ，尼玛！通过各种抓包对比发现是少了请求头  Content-Type: application/x-www-form-urlencoded
        headers = {'Referer': ref, 'Content-Type': 'application/x-www-form-urlencoded'
            ,
                   'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; WOW64; Trident/7.0; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 1.1.4322; InfoPath.3)'
            , 'Accept-Language': 'zh-CN,zh;q=0.8'
            , 'Origin': 'http://s.web2.qq.com'}

        # 去拿好友列表了
        r = self.htp.post(url, data=datas, headers=headers)
        self.__printlog('获取好友列表', url, r.text, r.cookies, self.htp.cookies, datas)

        self.friends = json.loads(r.text)

    def sendGroupMsg(self, uin, msg, face=None):
        '''
        r=
            {
                "group_uin":4242729568,
                "content":"["饿了",["font",{"name":"宋体","size":10,"style":[0,0,0],"color":"000000"}]]",
                "face":774,
                "clientid":53999199,
                "msg_id":44050002,
                "psessionid":"8368046764001d636f6e6e7365727665725f77656271714031302e3133392e372e31363400004881000010a5036e0400cc14023a6d0000000a40644f787a776b7454646d00000028b33a3a944975b00083704a7669f6f720d797f6eb2c8fd7df5ed4d17c98375e7b009e8b8d93bbe2fb"
            }

        '''
        msg = urllib.quote(msg, ":?=/")
        datas = ('r={"group_uin":%s,' % uin +
                 u'"content":"[\\\"%s\\\",[\\\"font\\\",{\\\"name\\\":\\\"\\u5B8B\\u4F53\\\",\\\"size\\\":10,\\\"style\\\":[0,0,0],\\\"color\\\":\\\"000000\\\"}]]",' % msg +
                 '"face":774,' +
                 '"clientid":53999199,' +
                 '"msg_id":44050002,' +
                 '"psessionid":"%s"' % self.psessionid +
                 '}')

        # 发送群组消息
        url = 'http://d.web2.qq.com/channel/send_qun_msg2'

        ref = 'http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2'
        headers = {'Referer': ref
            , 'Content-Type': 'application/x-www-form-urlencoded'
            ,
                   'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; WOW64; Trident/7.0; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 1.1.4322; InfoPath.3)'
                   #                    , 'Accept-Language': 'zh-CN,zh;q=0.8'
                   }

        # 去拿群组列表
        r = self.htp.post(url, data=datas, headers=headers)
        self.__printlog('发送群组消息', url, r.text, r.cookies, self.htp.cookies, datas)

        pass

    def sendFriendMsg(self, uin, msg):
        '''
        r={
        "to":3709697278
        ,"content":"[\"给我自己发\",[\"font\",{\"name\":\"宋体\",\"size\":10,\"style\":[0,0,0],\"color\":\"000000\"}]]"
        ,"face":774
        ,"clientid":53999199
        ,"msg_id":35090001
        ,"psessionid":"8368046764001d636f6e6e7365727665725f77656271714031302e3133392e372e31363400004881000010a5036e0400cc14023a6d0000000a40644f787a776b7454646d00000028e8f2fd0393d150b2404a4d198f196be7132786a4e3fc28c6b4014b78bcd1eda6bad51ef92d5e0862"
        }

        '''
        msg = urllib.quote(msg, ":?=/")
        datas = ('r={' +
                 '"to":%s' % uin +
                 ',"content":"[\\\"%s\\\",[\\\"font\\\",{\\\"name\\\":\\\"\u5B8B\u4F53\\\",\\\"size\\\":10,\\\"style\\\":[0,0,0],\\\"color\\\":\\\"000000\\\"}]]"' % msg +
                 ',"face":774' +
                 ',"clientid":53999199' +
                 ',"msg_id":35090001' +
                 ',"psessionid":"%s"' % self.psessionid +
                 '}')

        url = 'http://d.web2.qq.com/channel/send_buddy_msg2'
        ref = 'http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2'
        headers = {'Referer': ref
            , 'Content-Type': 'application/x-www-form-urlencoded'
            ,
                   'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.3; WOW64; Trident/7.0; .NET4.0E; .NET4.0C; .NET CLR 3.5.30729; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 1.1.4322; InfoPath.3)'
                   }

        # 发消息给好友
        r = self.htp.post(url, data=datas, headers=headers)
        self.__printlog('发送好友消息', url, r.text, r.cookies, self.htp.cookies, datas)
        pass


if __name__ == '__main__':
    qq = WebQQ('这是帐号', '这是密码')
    qq.userLogin()

    qq.getGroups()
    quin = qq.groups['result']['gnamelist'][1]['gid']
    qq.sendGroupMsg(str(quin), '其实我是想写个聊天机器人的，不过有点高深，另外，登录验证码的破解逻辑，还没写')

    qq.getFriends()
    fuin = qq.friends['result']['info'][6]['uin']
    print
    fuin
    qq.sendFriendMsg(str(fuin), 'shen me qing kuang ')