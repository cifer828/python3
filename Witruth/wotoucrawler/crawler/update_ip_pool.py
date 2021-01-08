# -*- coding: utf-8 -*-
from time import sleep
from lxml import html
import requests, psycopg2, requests.exceptions, socket
from psycopg2 import errorcodes

user = 'ubuntu'
password = 'wotou123'
database = 'wotou'
host = 'localhost'
proxyUrl = 'http://www.xicidaili.com/nn/'
proxyIpCt = 1000
testUrl = "http://www.tianyancha.com/company/638562997"
header = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0"}
verifyUrl = 'http://antirobot.tianyancha.com/captcha/verify'

def connectPostgersql():#连接数据库
    connector = psycopg2.connect(user=user, password=password, database=database, host=host)
    print 'connect database successfully!'
    return connector

def closeDatabaseConnect(connector, cursor):#关闭数据库连接
    print 'close database connect!'
    cursor.close()
    connector.close()

def clearProxyDB(connector, cursor):#验证已经下载好的代理ip的可用性
    cursor.execute(
        'select * from ip_pool;'
    )
    result = cursor.fetchall()
    for ip in result:
        para = {'ip': ip[1]}
        if ip[2] == "HTTP":
            proxy = {"http": 'http://' + ip[1]}
        else:
            proxy = {"http": 'socks5://user:pass@' + ip[1]}
        try:
            data = requests.get(url=testUrl, headers=header, proxies=proxy, timeout=60)
            #print data, ip, data.status_code, data.url
            if data.status_code != 200 or verifyUrl in data.url:
                cursor.execute(
                        'delete from ip_pool where ip =%(ip)s ', para
                    )
            connector.commit()
        except (requests.exceptions.Timeout, requests.exceptions.ProxyError, requests.exceptions.ConnectionError,
                socket.timeout, AssertionError, socket.error):

            cursor.execute(
                        'delete from ip_pool where ip =%(ip)s ', para
                    )
            connector.commit()


if __name__ == '__main__':
    connector = connectPostgersql()
    cursor = connector.cursor()
    ct = 0
    pageCt = 1
    clearProxyDB(connector, cursor)
    while ct < proxyIpCt:
        url = proxyUrl + str(pageCt)
        pageCt += 1
        rsp = requests.get(url=url, headers=header)
        if rsp.status_code != 200:
            print rsp.status_code
            break
        html1 = html.fromstring(rsp.content)
        ip = html1.xpath("//tr//td[2]/text()")
        port = html1.xpath("//tr//td[3]/text()")
        type = html1.xpath("//tr//td[6]/text()")
        ipList = [ip[i] + ':' + port[i] for i in range(0, len(ip))]
        for i in range(0, len(ipList)):
            para = {
                "ip": ipList[i],
                "type": type[i]
            }
            if para['type'] == "HTTP":
                proxy = {"http": 'http://' + para['ip']}
            else:
                proxy = {"http": 'socks5://user:pass@' + para['ip']}
            cursor.execute(
                'select count(*) from ip_pool where ip =%(ip)s;',
                para
            )
            result = cursor.fetchall()
            try:
                data = requests.get(url=testUrl, headers=header, proxies=proxy, timeout=3)
                if int(result[0][0]) == 0:
                    try:
                         cursor.execute(
                            'INSERT INTO ip_pool(ip, type)'
                            'VALUES(%(ip)s,%(type)s);',
                            para
                         )
                         connector.commit()
                         ct += 1
                    except psycopg2.errorcodes:
                        connector.commit()
                        pass
            except (requests.exceptions.Timeout, requests.exceptions.ProxyError, requests.exceptions.ConnectionError,
                    socket.timeout, AssertionError, socket.error):
                if int(result[0][0]) != 0:
                    cursor.execute(
                        'delete from ip_pool where ip =%(ip)s;',
                        para
                    )
                    connector.commit()
                pass
    closeDatabaseConnect(connector, cursor)

