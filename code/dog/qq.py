from qqbot import _bot as bot

QQ_BOT = None           #实例
QQ_GROUP_LIST = []      #群列表
QQ_BUDDY_LIST = []      #好友列表
QQ_ZH = ''

#################################################################################################################
# qq
def sendMsgToGroup(msg):
    global QQ_GROUP_LIST
    if (len(QQ_GROUP_LIST) > 0 and QQ_GROUP_LIST[0] != ''):
        for group in QQ_GROUP_LIST:
            bg = QQ_BOT.List('group', group)
            if bg is not None:
                ret = QQ_BOT.SendTo(bg[0], msg)
                if ret.find('成功') == -1:
                    outlogin()
                    QQ_BOT.SendTo(bg[0], msg)



def senMsgToBuddy(msg):
    return
    #print('senMsgToBuddy:' + msg)
    global QQ_BUDDY_LIST
    if (len(QQ_BUDDY_LIST) > 0 and QQ_BUDDY_LIST[0] != ''):
        for buddy in QQ_BUDDY_LIST:
            print(buddy)
            bg = QQ_BOT.List('buddy', buddy)
            print(bg)
            if len(bg) > 0:
                ret = QQ_BOT.SendTo(bg[0], msg)
                if ret.find('成功') == -1:
                    outlogin()
                    QQ_BOT.SendTo(bg[0], msg)

def outlogin():
    global QQ_BOT,QQ_ZH
    QQ_BOT.Login(['-q', QQ_ZH])
    print('qq relogin')



def init(qq):
    with open('qq.txt',errors='ignore',encoding='utf-8') as fr:
        qqBuddy = fr.readline().strip()
        qqGroup = fr.readline().strip()
    global QQ_GROUP_LIST,QQ_BUDDY_LIST
    QQ_BUDDY_LIST = qqBuddy.split(',')
    del QQ_BUDDY_LIST[0]
    QQ_GROUP_LIST = qqGroup.split(',')
    del QQ_GROUP_LIST[0]
    print(QQ_BUDDY_LIST)
    print(QQ_GROUP_LIST)
    if (len(QQ_BUDDY_LIST) > 0 and QQ_BUDDY_LIST[0] != '') or (len(QQ_GROUP_LIST) > 0 and QQ_GROUP_LIST[0] != ''):
        global QQ_BOT,QQ_ZH
        QQ_ZH = qq
        QQ_BOT = bot
        outlogin()
        #zh = input('请输入QQ号:')
        #bot.Login(['-q', QQ_ZH])