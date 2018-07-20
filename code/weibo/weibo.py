# -*- coding: utf-8 -*-

import requests
import urllib.request
import json
import time
import operator
from qqbot import _bot as bot
import itchat

# 定义要爬取的微博大V的微博ID
id = '5828706619'
#id = '2442366541'

# 设置代理IP
proxy_addr = "122.241.72.191:808"

# wchat
def sendMsgToWChat(msg,wchatList):
    for wchat in wchatList:
        print('wchat:'+wchat)
        users = itchat.search_friends(name=wchat)
        userName = users[0]['UserName']
        print('userName:'+userName)
        itchat.send(msg,toUserName=userName)

# wroom
def sendMsgToWRoom(msg,wroomList):
    itchat.get_chatrooms(update=True)
    for wroom in wroomList:
        print('wroom:' + wroom)
        iRoom = itchat.search_chatrooms(wroom)
        for room in iRoom:
            if room['NickName'] == wroom:
                userName = room['UserName']
                print('userName:'+userName)
                itchat.send_msg(msg, userName)
                break



#################################################################################################################
# qq
def sendMsgToGroup(msg,groupList,bot):
    for group in groupList:
        bg = bot.List('group', group)
        if bg is not None:
            bot.SendTo(bg[0], msg)

def senMsgToBuddy(msg,buddyList,bot):
    for buddy in buddyList:
        bg = bot.List('buddy', buddy)
        if bg is not None:
            bot.SendTo(bg[0], msg)

#################################################################################################################
# weibo
# 定义页面打开函数
def use_proxy(url, proxy_addr):
    req = urllib.request.Request(url)
    req.add_header("User-Agent",
                   "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0")
    proxy = urllib.request.ProxyHandler({'http': proxy_addr})
    opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    try:
        print('url get')
        response = urllib.request.urlopen(req)
        data = response.read().decode('utf-8', 'ignore')
        return data
    except:
        print('url error')
        return '-1'
    return data


# 获取微博主页的containerid，爬取微博内容时需要此id
def get_containerid(url):
    data = use_proxy(url, proxy_addr)
    o = json.loads(data)
    if o != None:
        content = json.loads(data).get('data')
        for data in content.get('tabsInfo').get('tabs'):
            if (data.get('tab_type') == 'weibo'):
                containerid = data.get('containerid')
                return containerid
    return -1



# 获取微博大V账号的用户基本信息，如：微博昵称、微博地址、微博头像、关注人数、粉丝数、性别、等级等
def get_userInfo(id):
    url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + id
    data = use_proxy(url, proxy_addr)
    content = json.loads(data).get('data')
    profile_image_url = content.get('userInfo').get('profile_image_url')
    description = content.get('userInfo').get('description')
    profile_url = content.get('userInfo').get('profile_url')
    verified = content.get('userInfo').get('verified')
    guanzhu = content.get('userInfo').get('follow_count')
    name = content.get('userInfo').get('screen_name')
    fensi = content.get('userInfo').get('followers_count')
    gender = content.get('userInfo').get('gender')
    urank = content.get('userInfo').get('urank')
    '''
    print("微博昵称：" + name + "\n" + "微博主页地址：" + profile_url + "\n" + "微博头像地址：" + profile_image_url + "\n" + "是否认证：" + str(
        verified) + "\n" + "微博说明：" + description + "\n" + "关注人数：" + str(guanzhu) + "\n" + "粉丝数：" + str(
        fensi) + "\n" + "性别：" + gender + "\n" + "微博等级：" + str(urank) + "\n")
        '''


# 获取微博内容信息,并保存到文本中，内容包括：每条微博的内容、微博详情页面地址、点赞数、评论数、转发数等
def get_weibo(id, file):
    i = 1
    while True:
        url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + id
        ss = get_containerid(url)
        if ss == -1:
            continue
        weibo_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + id + '&containerid=' + ss + '&page=' + str(i)
        try:
            data = use_proxy(weibo_url, proxy_addr)
            content = json.loads(data).get('data')
            cards = content.get('cards')
            if (len(cards) > 0):
                for j in range(len(cards)):
                    print("-----正在爬取第" + str(i) + "页，第" + str(j) + "条微博------")
                    card_type = cards[j].get('card_type')
                    if (card_type == 9):
                        mblog = cards[j].get('mblog')
                        attitudes_count = mblog.get('attitudes_count')
                        comments_count = mblog.get('comments_count')
                        created_at = mblog.get('created_at')
                        reposts_count = mblog.get('reposts_count')
                        scheme = cards[j].get('scheme')
                        text = mblog.get('text')
                        with open(file, 'a', encoding='utf-8') as fh:
                            fh.write("----第" + str(i) + "页，第" + str(j) + "条微博----" + "\n")
                            fh.write("微博地址：" + str(scheme) + "\n" + "发布时间：" + str(
                                created_at) + "\n" + "微博内容：" + text + "\n" + "点赞数：" + str(
                                attitudes_count) + "\n" + "评论数：" + str(comments_count) + "\n" + "转发数：" + str(
                                reposts_count) + "\n")
                i += 1
            else:
                break
        except Exception as e:
            print(e)
            pass


def url_download(image,name):
    r = requests.get(image)
    with open(name+'.jpg', 'wb') as f:
        f.write(r.content)

def check_time(time):
    index2 = time.find('秒前',0,len(time))
    index3 = time == '刚刚'
    if index2 > 0 or index3:
        return 1

    smin = '分钟前'
    index = time.find(smin, 0, len(time))
    if index > 0:
        time = time.replace(smin, '', 1)
        return int(time)

    return -1

# 获取比对是否新发微博
def get_newweibo(id,laststring):
    i = 1
    url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + id
    weibo_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=' + id + '&containerid=' + get_containerid(
        url) + '&page=' + str(i)
    #print(weibo_url)
    try:
        data = use_proxy(weibo_url, proxy_addr)
        while data == -1:
            data = use_proxy(weibo_url, proxy_addr)
        content = json.loads(data).get('data')
        cards = content.get('cards')
        #print('get msg suc  len(cards):'+str(len(cards)))
        if (len(cards) > 0):
            card_type = cards[0].get('card_type')
            if card_type == 9:
                mblog = cards[0].get('mblog')
                text = mblog.get('text')
                text = text.replace('<br /><br />', '。')
                #print('消息返回 text:'+text)
                if operator.__eq__(laststring, '') == True:
                    print('first get suc')
                    print(text)
                    return False, text

                rtime = mblog.get('created_at')
                tmin = check_time(rtime)
                if tmin > 0 and tmin < 4:
                    if operator.__eq__(laststring, text) == True:
                        return False, laststring
                    #pic = mblog.get('original_pic')
                    #if pic is not None:
                    #    now_time = time.strftime('%Y/%m/%d-%H%M')
                    #    url_download(pic, now_time + '-' + picid)
                    #    picid = picid + 1
                    #else:
                    #    print('pic none')
                    print('get suc:' + text)
                    return True, text
                else:
                    print('get False and  tmin:' + str(tmin))
                    return False, laststring
    except Exception as e:
        print(e)

    return False,laststring


if __name__ == "__main__":
    #file = id + ".txt"
    #get_userInfo(id)
    #get_weibo(id, file)
    with open('weibo.txt', 'r') as fr:
        qqGroup = fr.readline().strip()
        qqBuddy = fr.readline().strip()
        wchat = fr.readline().strip()
        wroomchat = fr.readline().strip()
    qqGroupList = qqGroup.split(',')
    qqBuddyList = qqBuddy.split(',')
    wChatList = wchat.split(',')
    wRoomList = wroomchat.split(',')
    qqinit = 1
    #print(' cnt :' + str(len(qqGroupList)) + ' cnt2:' + str(len(qqBuddyList)))
    if (len(qqGroupList) > 0 and qqGroupList[0] != '' ) or (len(qqBuddyList) > 0 and qqBuddyList[0] != ''):
        zh = input('请输入QQ号:')
        bot.Login(['-q',zh])
        qqinit = 2

    wchatinit = 1
    if (len(wChatList) > 0 and wChatList[0] != '') or (len(wRoomList) > 0 and wRoomList[0] != ''):
        itchat.auto_login(hotReload=True)  # 首次扫描登录后后续自动登录
        wchatinit = 2

    laststring = '' # 临时内存内容比较
    while True:
        print("正在爬取最新一条微博...")
        isnew,laststring = get_newweibo(id,laststring)
        if isnew == True:
            print('监控到新消息')
            if qqinit == 2:
                if (len(qqGroupList) > 0 and qqGroupList[0] != ''):
                    sendMsgToGroup('[狂龙十八段]'+laststring, qqGroupList, bot)
                if (len(qqBuddyList) > 0 and qqBuddyList[0] != ''):
                    senMsgToBuddy('[狂龙十八段]'+laststring, qqBuddyList, bot)
            if wchatinit == 2:
                if (len(wChatList) > 0 and wChatList[0] != ''):
                    sendMsgToWChat('[狂龙十八段]'+laststring, wChatList)
                if (len(wRoomList) > 0 and wRoomList[0] != ''):
                    sendMsgToWRoom('[狂龙十八段]'+laststring, wRoomList)
            # attitudes_count = mblog.get('attitudes_count')
            # comments_count = mblog.get('comments_count')
            # created_at = mblog.get('created_at')
            # reposts_count = mblog.get('reposts_count')
            # scheme = cards[j].get('scheme')
        else:
            print('未监控到新消息')
        time.sleep(10)

