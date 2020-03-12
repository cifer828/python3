# -*- coding: utf-8 -*-
"""
author: cifer_zhang
date: 2017.5.6
临床试验追踪
数据源：药智网
https://db.yaozh.com/linchuangshiyan/

date:2017.5.12
增加代理
"""
import socket
import datetime
import time
import urllib.parse
import re
import pymongo
import requests
from lxml import html
from spiders.track_asset import spider_qichacha as qcc
from spiders.track_asset import spider_tianyancha as tyc
from spiders.track_asset import proxies
from wotu.config.config import MONGO_SERVER
from wotu.config.config import MONGO_PORT

CONN = pymongo.MongoClient(MONGO_SERVER, MONGO_PORT)
PROXIES = proxies.abuyun_proxy()

def get_clinical_data_from_db(id):
    '''
    输入：临床试验注册号
    若公司存在于数据库，输出条目
    不存在输出None
    '''
    db=CONN['news']
    collection=db['clinical_trial']
    ret = collection.find_one({'注册号': id})
    if not ret:
        return None
    return ret

def write_updated_item2mongo(item):
    db=CONN['news']
    collection=db['clinical_trial']
    ret = collection.find_one({'注册号': item['注册号']})
    if not ret:
        return None
    if item['试验状态'][0] not in ret['试验状态'][0] or item['试验分期'] not in ret['试验分期']:
        collection.update({'注册号':item['注册号']},{'$set' :{'试验状态': ret['试验状态'] + item['试验状态'],
                                                                '试验分期': ret['试验分期'] + item['试验分期'],
                                                                '登记时间': ret['登记时间'] + item['登记时间'],
                                                                '爬取时间': ret['爬取时间'] + item['爬取时间']}})


def write2mongo(item):
    db=CONN['news']
    collection=db['clinical_trial']
    item['爬取时间'] = [datetime.datetime.now()]
    collection.insert(item)

def update_clinical_data():
    """
    后台更新：上次爬至今该段时间内的临床试验条目信息
    """
    db = CONN['news']
    collection=db['clinical_trial']
    date_time = [item['登记时间'][-1]  for item in collection.find()]
    latest_date_in_db = datetime.datetime.strptime(sorted(date_time)[-1], '%Y-%m-%d')
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    result =get_clinical_data_by_date(latest_date_in_db.strftime('%Y-%m-%d'), today)
    return result

def get_data_from_db_by_date(datestr):
    db = CONN['news']
    collection=db['clinical_trial']
    return [item for item in collection.find({'登记时间':datestr})]

def get_clinical_data_by_date(datestr_str, dateend_str):
    """
    输入：起始日期，终止日期
    输出：该段时间内的临床试验条目信息
    """
    result = []
    datestr = datetime.datetime.strptime(datestr_str, '%Y-%m-%d')
    dateend = datetime.datetime.strptime(dateend_str, '%Y-%m-%d')
    while((dateend - datestr).days > -1):
        one_day_data = get_data_from_db_by_date(datestr.strftime( '%Y-%m-%d'))   # 现在数据库中查找该日数据
        if not one_day_data:
            result += _one_day_clinical_data(datestr)
        else:
            print(datestr)
            result += one_day_data
        datestr = datestr + datetime.timedelta(days = 1)
    return result

def _one_day_clinical_data(datestr,times=0):
    """
    输入：起始日期，终止日期（一次查询）
    输出：该段时间内的临床试验条目信息
    """
    print(datestr)
    base_url = 'https://db.yaozh.com/linchuangshiyan?'
    data = {'p': 1,
            'sort':'全部',
            'type':'全部',
            'pageSize':'30',
            'phase':'全部',
            'status':'全部',
            'datestr':datestr,
            'dateend':datestr, }
    url = base_url + urllib.parse.urlencode(data)
    try:
        response = requests.get(url, proxies = PROXIES)
        root = html.fromstring(response.content)
        total_nums_xpath =  '//div[@data-widget="dbPagination"]/@data-total'
        if root.xpath('//div[@data-widget="dbNoData"]'):    # 无查询结果
            print('Blank Page')
            return []
        total_nums = int(root.xpath(total_nums_xpath)[0])       # 条目总数
        total_pages = int(total_nums / 30) + 1
        not_crawled_list = []
        for i in range(1, total_pages + 1):
            not_crawled_list += one_page_data(datestr, i)
        return not_crawled_list
    except socket.gaierror as e:
        print("网络中断")
    except IndexError as e:
        print("页面信息错误")
    except Exception as e:
        if times < 3:
            times += 1
            return _one_day_clinical_data(datestr, times)
        else:
            return []

def one_page_data(datestr,current_page, times=0):
    """
    输入：起始日期，终止日期，页数
    输出：该页内临床受审条目信息
    注册号 链接 试验题目 适应症 试验状态 试验分期 [申办单位，] 公司名称
    """
    print('page:', current_page)
    base_url = 'https://db.yaozh.com/linchuangshiyan?'
    data = {'p': current_page,
            'sort':'全部',
            'type':'全部',
            'pageSize':'30',
            'phase':'全部',
            'status':'全部',
            'datestr':datestr,
            'dateend':datestr, }
    url = base_url + urllib.parse.urlencode(data)
    try:
        response = requests.get(url, proxies = PROXIES)
        root = html.fromstring(response.content)
        tr_num = 1    # 行数
        items_list = []
        while(True):
            if root.xpath('//tbody/tr[%d]/th/a/text()' % tr_num) == [] or tr_num > 30:   # 该页已爬完
                break
            id = root.xpath('//tbody/tr[%d]/th/a/text()' % tr_num)[0]
            link = 'http://db.yaozh.com' + root.xpath('//tbody/tr[%d]/th/a/@href' % tr_num)[0]
            # item = get_clinical_data_from_db(id)
            # if item:     # 跳过之前爬过的
            #     items_list.append(item)
            #     tr_num += 1   # 下一行
            #     continue
            detail_xpath = root.xpath('//tbody/tr[%d]' % tr_num)[0]
            item = {'注册号': id, '链接':link,'试验题目': detail_xpath.xpath('td[1]/text()')[0]}
            try:
                item['适应症'] = detail_xpath.xpath('td[2]')[0].xpath('string(.)')
            except Exception as e:
                item['适应症'] = ''
            try:
                item['试验状态'] = [detail_xpath.xpath('td[3]/text()')[0]]
            except Exception as e:
                item['试验状态'] = []
            try:
                item['试验分期'] = [detail_xpath.xpath('td[4]/text()')[0]]
            except Exception as e:
                item['试验分期'] = []
            try:
                item['申办单位'] = [cname.strip() for cname in detail_xpath.xpath('td[5]/text()')[0].split('/') if len(cname) > 3]
            except Exception as e:
                item['申办单位'] = []
            try:
                item['登记时间'] = [detail_xpath.xpath('td[6]/text()')[0]]
            except Exception as e:
                item['登记时间'] = []
            if not write_updated_item2mongo(item):  # 更新数据
                write2mongo(item)      # 存入数据库
            tr_num += 1   # 下一行
            items_list.append(item)
            print(item)
        return items_list
    except socket.gaierror as e:
            print("网络中断")
    except IndexError as e:
        print("页面信息错误")
    except Exception as e:
        if times < 3:
            times += 1
            return _one_day_clinical_data(datestr, times)
        else:
            return []

def name_filter(item_list):
    '''
    输入：临床试验条目列表
    输出：不包含stop_word的中国公司
    '''
    blacklist_name = [item['stop_word']for item in CONN['news']['blacklist_clinical_trial'].find()]
    result_set = set([])
    for item in item_list:
        for cname in item['申办单位']:
            if not in_blacklist(cname, blacklist_name) and check_contain_chinese(cname):
                result_set.add(cname)
    return result_set

def check_contain_chinese(check_str):
    """
    判断字符串是否包含中文
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def in_blacklist(check_str, blacklist_name):
    """
    检查是否包含外国国名
    包含返回True
    """
    for bn in blacklist_name:
        if bn in check_str:
            return True
    return False

def clinical_trial_filter_api(datestr, dateend):
    """
    输入：起始日期，终止日期
    输出：期间有临床试验申报的
         [中国企业列表，符合条件企业列表]
    """
    update_item_list = get_clinical_data_by_date(datestr, dateend)    # 实际用
    # update_item_list = one_page_data(datestr, 1)   # 单页测试
    wanted_company_list = []
    apply_company_set = name_filter(update_item_list)
    for com in apply_company_set:
        # if tyc.search_company(tyc.search_detail(com)) == 1:    # 实际用
        #     wanted_company_list.append(com)
        try:    # 测试用
            if tyc.filter_company(qcc.search_detail(com)) == 1:
                wanted_company_list.append(com)
        except:
            pass
    return list(apply_company_set), wanted_company_list

def test():
    result= clinical_trial_filter_api('2017-01-01','2017-05-26')
    print('结果：')
    print('-----------------所有公司--------------------')
    for r in result[0]:
        print(r)
    print('------------------符合要求-------------------')
    for w in result[1]:
        print(w)

if __name__ == '__main__':
    update_clinical_data()   # 定时爬取指令，部署在服务器上时不要注释
    # test()
    # test_dict = {'试验分期': ['治疗新技术临床试验'], '爬取时间': [datetime.datetime(2017, 5, 26, 17, 24, 1, 139043)], '试验题目': '基于Nogo-A/RhoA/ROCK通路研究强制性运动精准治疗偏瘫型脑瘫的作用与机制', '链接': 'http://db.yaozh.com/linchuangshiyan/5219.html', '适应症': '脑性瘫痪', '申办单位': ['广州市妇女儿童医疗中心'], '注册号': 'ChiCTR-ROC-17010309', '试验状态': ['进行中'], '登记时间': ['2017-01-02']}
    # write_updated_item2mongo(test_dict)
    # print(get_data_from_db_by_date('2017-01-01'))
    # get_clinical_data_by_date('2017-01-01','2017-05-26')
    # _one_day_clinical_data('2017-03-20')
    # one_page_data('2017-03-17','2017-03-20', 1)
    # detail('https://db.yaozh.com/linchuangshiyan/23.html')
    # detail('https://db.yaozh.com/linchuangshiyan/93.html')
    pass



