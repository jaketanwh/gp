
# 财联社
def cls():
    #url = 'https://m.cailianpress.com/' 手机版刷新不及时
    url = 'https://www.cailianpress.com/'
    res = send(url, 0)
    if res != -1:
        global CLS_CATCH_LIST
        baseinfo = format('__NEXT_DATA__ = ', '\n          module=', res)
        if len(baseinfo) <= 0:
            return

        data = json.loads(baseinfo[0])
        dataList = data['props']['initialState']['telegraph']['dataList']
        for info in dataList:
            level = info['level']
            if level == 'B' or level == 'A':
                id = info['id']
                if id not in CLS_CATCH_LIST:
                    ctime = info['ctime']
                    #title = info['title']
                    content = info['content']
                    #modified_time = info['modified_time']
                    ftime = time.strftime("%H:%M:%S", time.localtime(ctime))
                    print(content.replace('\\u200b', '', 1))
                    qq.sendMsgToGroup('[财联社]' + '[' + ftime + ']' + content)
                    CLS_CATCH_LIST.append(id)

        if len(CLS_CATCH_LIST) > 30:
            CLS_CATCH_LIST.pop()