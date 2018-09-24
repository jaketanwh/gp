# code表数据
import tools
import net
import kpltools
import t_bk

#更新板块表 13min
GLOBAL_BK = {}
GLOBAL_BK_ID = 1
def updateBK(name,percent):
    global GLOBAL_BK,GLOBAL_BK_ID
    # 没有数据
    if name in GLOBAL_BK.keys():
       return GLOBAL_BK[name][0]
    GLOBAL_BK[name] = [GLOBAL_BK_ID,percent]
    GLOBAL_BK_ID = GLOBAL_BK_ID + 1
    return GLOBAL_BK_ID - 1


#取开盘啦个股数据
def kpl_gg(code):
    print('[kpl] gg update - '+code)
    lastday = tools.getlastday()
    param = kpltools.build_kpl_gg(code,lastday)
    res = -1
    while (res == -1 or isinstance(res['pankou'],dict) == False or isinstance(res['pankou']['real'],dict) == False):
        res = net.kpl(param)

    #timeout
    if res == -2:
        return -1

    info = {}
    real = res['pankou']['real']
    info['pb'] = real['dyn_pb_rate']                #市净率
    info['percent'] = real['px_change_rate']        #涨跌幅
    info['turnover'] = real['turnover_ratio']       #换手率
    info['sjlt'] = int(real['sjlt'])                #真实流通市值
    info['nmc'] = real['circulation_value']         #流通市值
    info['mktcap'] = real['market_value']           #总市值


    #所属板块及板块涨幅
    bklist = []
    stockplate = res['stockplate']
    if stockplate == None:
        print('[code] ' + res['pankou']['name'] + ' stockplate is NoneType')
    else:
        for row in stockplate:
            bkname = row[0]     #板块name
            bkzd = row[1]  # 涨跌幅
            bkid = updateBK(bkname,bkzd)
            bklist.append(bkid)

    info['bk'] = str(bklist) #','.join()# str.split(',')
    return info

# 使用tushare 更新代码，st
def ts_updatecode(conn, today):
    if today.empty:
        return -1

    _list = {}
    for i, row in today.iterrows():
        code = row['code']
        k = code[:2]
        if k != '30' and k != '60' and k != '00':
            continue

        if row['trade'] == 0:
            continue

        info = kpl_gg(code)
        if info == -1:
            continue

        if row['name'].find('ST') >= 0:
            st = 1
        else:
            st = 0

        info['st'] = st                                         # st 1.是 0.否
        info['pb'] = round(info['pb'] * 100)                    # 市净率 保留两位四舍五入
        info['per'] = round(row['per'] * 100)                   # 市盈率 保留两位四舍五入
        info['percent'] = round(info['percent'] * 100)          # 涨跌幅 保留两位四舍五入
        info['turnover'] = round(info['turnover'] * 100)        # 换手率 保留两位四舍五入
        info['sjlt'] = round((info['sjlt']) * 0.0001)           # 真实流通市值 计数万单位
        info['nmc'] = round((info['nmc']) * 0.0001)             # 流通市值 计数万单位
        info['mktcap'] = round((info['mktcap']) * 0.0001)       # 总市值 计数万单位

        _list[code] = info

    # 游标
    cursor = conn.cursor()
    # 创建code表   代码(id) 是否st(st 1.是 0.不是) 涨跌(percent) 市净率(pb) 市盈率(per) 换手(turnover) 总市值(mktcap) 流通市值(nmc) 真实市值(sjlt) 板块[名字1,名字2...](bk)
    if tools.table_exists(cursor, 'code') == 0:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS code(id TEXT,st TINYINT(1),percent SMALLINT,pb MEDIUMINT, per MEDIUMINT,turnover SMALLINT UNSIGNED,nmc INT UNSIGNED,mktcap INT UNSIGNED,sjlt INT UNSIGNED,bk TEXT)")

    # 写入code表数据
    for key, value in _list.items():
        st = value['st']
        nmc = value['nmc']
        mkcap = value['mktcap']
        pb = value['pb']
        per = value['per']
        sjlt = value['sjlt']
        percent = value['percent']
        turnover = value['turnover']
        bk = value['bk']
        cursor.execute("SELECT * FROM code WHERE id=%s", key)
        res = cursor.fetchall()
        if len(res) == 0:
            cursor.execute(
                "INSERT INTO code(id,st,percent,pb,per,turnover,nmc,mktcap,sjlt,bk) VALUES('%s','%d','%d','%d','%d','%d','%d','%d','%d','%s')" % (
                key, st, percent, pb, per, turnover, nmc, mkcap, sjlt, bk))
        else:
            sql = ("UPDATE code SET st=%d,percent=%d,pb=%d,per=%d,turnover=%d,nmc=%d,mktcap=%d,sjlt=%d,bk=%s WHERE id = '" + key + "'") % (
                st, percent, pb, per, turnover, nmc, mkcap, sjlt, "'" + bk + "'")
            cursor.execute(sql)

    conn.commit()
    cursor.close()
    return 0



def update(conn):
    serverTime,serverDay = tools.get_servertime()
    print('code表开始更新' + str(serverTime))
    ret = -1
    while ret == -1:
        ret,today = net.tushare_today()

    ret = ts_updatecode(conn,today)
    if ret != 0:
        print('[code]表更新错误')
        return ret

    global GLOBAL_BK
    print(GLOBAL_BK)
    t_bk.update(conn,GLOBAL_BK)
    print('code表更新完成')
    return ret