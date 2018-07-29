import requests

'''
head
'''
def allheaders():
    headers = {
        'Host':'www.iwencai.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zAj0cAEQKOmPYSZ4PWGXP0lNnT5g22nHvewjVAP-CeRTDNlPK'
                          'h-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding':'gzip,deflate',
        'Referer': 'http://www.iwencai.com/stockpick/search?typed=0&preParams=&ts=1&f=1&qs=result_original&selfsectsn=&querytype=stock&searchfilter=&tid=stockpick&w=2018%2F7%2F5%20%E5%B9%B4%E7%BA%BF%E4%B8%8A&queryarea=',
        'hexin-v': 'Ap--avq0OGnEhzx1GeQN6OVxLfIoBPOfDVn3mjHsOR-VkbHgOdSD9h0oh-xC',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': 'cid=d39902441188593815b9de4a660beafe1512962748; ComputerID=d39902441188593815b9de4a660beafe1512962748; v=Ap--avq0OGnEhzx1GeQN6OVxLfIoBPOfDVn3mjHsOR-VkbHgOdSD9h0oh-xC; guideState=1; PHPSESSID=b9b44bc6f0b2832d1c1d80f334837c15',
        'Connection': 'keep-alive'
    }
    return headers

def defaultheaders():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1;Win64;x64;rv:61.0)Gecko/20100101 Firefox/61.0"
    }
    return headers




#send
def send(url,typ=0,default=0):
    if default == 1:
        headers = allheaders()
    else:
        headers = defaultheaders()

    try:
        code_of_html = requests.get(url,headers=headers)
    except Exception as ee:
        print("net error")
        return -1

    if code_of_html.status_code == 200:
        if typ == 1:
            html_doc = str(code_of_html.content, 'utf-8')
            return html_doc
        else:
            return code_of_html.text
    else:
        print('html error:',code_of_html.status_code)
        return -1


#send
def sendpost(url,param):
    try:
        headers = defaultheaders()
        code_of_html = requests.post(url, data=param, headers=headers)
        if code_of_html.status_code != 200:
            return -1
    except Exception as ee:
        print("net error")
        return -1

    return code_of_html.text