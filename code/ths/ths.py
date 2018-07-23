import requests
import json
import time,datetime
#from xlutils.copy import copy
#import xlrd

def perform_command():
    head = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1;Win64;x64;rv:61.0)Gecko/20100101 Firefox/61.0"}
    code_of_html = requests.get("http://q.10jqka.com.cn/api.php?t=indexflash&", headers=head)
    data = json.loads(code_of_html.text)
    res = data['dppj_data']

    now_time = time.strftime('%Y/%m/%d-%H%M')
    print("time:", now_time, "  res:", res)
'''
    xlrd_xls = xlrd.open_workbook('ths.xls')
    r_sheet = xlrd_xls.sheet_by_index(0)
    nrows = r_sheet.nrows
    xlutils_xls = copy(xlrd_xls)
    sheet = xlutils_xls.get_sheet(0)
    sheet.write(nrows, 1, res)
    
    sheet.write(nrows, 0, now_time)
    xlutils_xls.save('ths.xls')
    '''


def do_while():
    while True:
        perform_command()
        time.sleep(3)
        '''
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        if (now.second == 0 and ((hour == 10 and minute == 30) or (hour == 11 and minute == 30) or (hour == 14 and minute == 0) or (hour == 15 and minute == 0))):
            perform_command()
            if hour == 11:
                time.sleep(8980)
            else:
                time.sleep(3580)
                '''

do_while()