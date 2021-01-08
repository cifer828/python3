# -*- coding: utf-8 -*-
"""
author: cifer_zhang
date: 2017.4.22
利用投资基金业协会网站搜索功能，查询基金管理的所有合伙企业
http://gs.amac.org.cn/amac-infodisc/res/pof/fund/index.html
"""

import requests
import json
from lxml import html
import chardet
import urllib.request, urllib.error, urllib.parse
import urllib.request, urllib.parse, urllib.error

def search_manager(manager_keyword):
    """
    输入：基金管理人关键字
    输出：基金管理人全称及其管理的基金
    """
    manager = manager_keyword.encode("utf-8").decode("latin1")
    headers = {
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
            'content-type': "application/json",
            }
    url = 'http://gs.amac.org.cn/amac-infodisc/res/pof/fund/index.html'
    json_url = "http://gs.amac.org.cn/amac-infodisc/api/pof/fund?rand=0.78840034244678&page=0&size=100"
    data = '{"keyword": "%s"}' % manager
    # data = {'keyword':'a'}
    result = requests.post(json_url, headers=headers ,data = data)
    info_json = json.loads(result.content.decode('utf8'))
    manager_dict = {}
    for item in info_json['content']:
        manager_name = item['managerName'].replace('<em>' , '').replace('</em>', '')
        if manager_keyword in manager_name:
            if manager_name in list(manager_dict.keys()):
                continue
            url =  'http://gs.amac.org.cn/amac-infodisc/res/pof' + item['managerUrl'][2: ]
            manager_dict[manager_name] = search_asset_by_manager(url)
    return manager_dict

def search_asset_by_manager(url):
    """
    爬取指定基金管理人管理的所有基金产品
    """
    result = requests.get(url)
    root = html.fromstring(result.content)
    asset_list = []
    # 基金产品在页面中位置不确定，需拼接所有可能位置
    for i in range(20, 30):
        asset_xpath = '//html/body/div/div[2]/div/table/tbody/tr[%d]/td[2]/p/a/text()' % i
        asset_list += root.xpath(asset_xpath)
    return asset_list

def test():
    manager_dict = search_manager('中信资本（天津）投资管理合伙企业（有限合伙）')
    print(manager_dict)
    for manager, assets in list(manager_dict.items()):
        print(manager)
        for a in assets:
            print(a)
        print('----------------------------------')

if __name__ == '__main__':
    test()