# -*- coding: utf-8 -*-
import requests
from time import sleep
from lxml import html
from requests import exceptions

hold = 10
header = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0"}
for i in range(0, 100000):
    url = 'http://www.tianyancha.com/company/638562997'
    try:
        rsp = requests.get(headers=header, url=url)
        html1 = html.fromstring(rsp.content)
        print rsp.content
        title = html1.xpath('//title/text()')[0].encode('utf8')
        print i, title, len(rsp.content)
    except requests.exceptions:
        continue

