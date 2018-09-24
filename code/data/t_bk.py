# bk表数据
import tools

def update(conn,t_bk):
    print('bk表开始更新')
    # 写入游标
    cursor = conn.cursor()

    # 创建bk表 板块id(id) 名字(name) 涨跌(percent)
    if tools.table_exists(cursor, 'bk') == 1:
        cursor.execute("DROP TABLE bk")
    cursor.execute("CREATE TABLE IF NOT EXISTS bk(id SMALLINT UNSIGNED,name TEXT,percent SMALLINT)")


    for name,row in t_bk.items():
        id      = row[0]                    #板块id
        percent = round(row[1] * 100)       #涨跌幅 保留两位四舍五入
        cursor.execute("INSERT INTO bk(id,name,percent) VALUES('%d','%s','%d')" % (id, name, percent))

    conn.commit()
    cursor.close()
    print('bk表更新完成')
