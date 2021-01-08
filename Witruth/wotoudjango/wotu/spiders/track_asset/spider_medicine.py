# -*- coding: utf-8 -*-
import requests
import time
from wotu.spiders.track_asset import spider_qichacha as qcc
from wotu.spiders.track_asset import spider_tianyancha as tyc
from lxml import html
import pymongo
from wotu.config.config import MONGO_SERVER
from wotu.config.config import MONGO_PORT
from spiders.track_asset import proxies
import datetime
from spiders.track_asset import spider_tianyancha as sty
import socket

CONN = pymongo.MongoClient(MONGO_SERVER, MONGO_PORT)
PROXIES = proxies.abuyun_proxy()

def get_medicine_data_from_db(item):
    '''
    输入：药品受理号
    若公司存在于数据库，输出条目
    不存在输出None
    '''
    db=CONN['news']
    collection=db['medicine']
    ret = collection.find_one({'受理号': item['受理号']})
    if not ret:
        return None
    return ret

def write2mongo(item):
    db=CONN['news']
    collection=db['medicine']
    item['爬取时间'] = datetime.datetime.now()
    collection.insert(item)

def update_medicine_data():
    """
    后台更新：上次爬至今该段时间内的药品受审条目信息
    """
    db = CONN['news']
    collection=db['medicine']
    date_time = [item['承办日期']  for item in collection.find()]
    latest_date_in_db = datetime.datetime.strptime(sorted(date_time)[-1], '%Y-%m-%d')
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    result =get_update_accept_list(latest_date_in_db.strftime('%Y-%m-%d'), today)
    return result

def get_data_from_db_by_date(datestr):
    db = CONN['news']
    collection=db['medicine']
    return [item for item in collection.find({'承办日期':datestr})]

def get_update_accept_list(str_datestr, str_dateend, times=0):
    """
    输入：起始日期，终止日期
    输出：该段日期内药物受理条目
    """
    url = 'http://www.cde.org.cn/transparent.do'
    payload = {'method': 'list'}
    try:
        response = requests.get(url, payload, proxies= PROXIES)
        url = response.url
        data = {'checktype':'1','pagetotal':'0','statenow':'0','year':'2017','drugtype':'','applytype':'','acceptid':'',
                'drugname':'','company':'','currentPageNumber':'1','pageMaxNumber':'80','totalPageCount':'0','pageroffset':'',
                'pageMaxNum':'80'}                 #POST数据
        response2 = requests.post(url, data=data, proxies= PROXIES)
        root = html.fromstring(response2.content)
        page_num_xpath =  '//td[@id="pageNumber"]/font[2]/text()'        #页码总数
        page_num = int(root.xpath(page_num_xpath)[0])
        page_total_xpath = '//span[@class="STYLE21"]/text()'          #表单条目总数
        page_total = int(root.xpath(page_total_xpath)[0])
        not_crawled_list = []
        for i in range(1, page_num + 1):
            one_page_list = accept_list_one_page(page_num, page_total, i, str_datestr, str_dateend)
            not_crawled_list += one_page_list[0]
            if not one_page_list[1]:
                break
        return not_crawled_list
    except socket.gaierror as e:
            print("网络中断")
    except IndexError as e:
        print("页面信息错误")
    except Exception as e:
        if times < 3:
            times += 1
            return get_update_accept_list(str_datestr, str_dateend, times)
        else:
            return []

def accept_list_one_page(page_num, page_total, current_page, str_datestr, str_dateend, times=0):
    """
    输入：总条目数，总页数，当前页，起始日期，终止日期
    输出：受理号，药品名称，药品类型， 申请类型，注册分类，企业名称，承办日期
    """
    data = {'checktype':'1','pagetotal':page_total, 'statenow':'0','year':'2017','drugtype':'','applytype':'','acceptid':'',
        'drugname':'','company':'','currentPageNumber':current_page,'pageMaxNumber':'80','totalPageCount':page_num,'pageroffset':'20',
        'pageMaxNum':'80','pagenum': current_page}
    url = 'http://www.cde.org.cn/transparent.do?method=list'
    try:
        response = requests.post(url, data=data, proxies= PROXIES)
        root = html.fromstring(response.content)
        item_num = 1
        items_list = []
        while(True):
            item = {}
            if not root.xpath('//tr[@height="30"][%d]' % item_num) or item_num > 80:
                break
            detail_xpath = root.xpath('//tr[@height="30"][%d]' % item_num)[0]
            try:
                item['受理号'] = detail_xpath.xpath('td[1]/text()')[0].strip()
            except Exception as e:
                item['受理号'] = ''
            try:
                item['药品名称'] = detail_xpath.xpath('td[2]/text()')[0].strip()
            except Exception as e:
                item['药品名称'] = ''
            try:
                item['药品类型'] = detail_xpath.xpath('td[3]/text()')[0].strip()
            except Exception as e:
                item['药品类型'] = ''
            try:
                item['申请类型'] = detail_xpath.xpath('td[4]/text()')[0].strip()
            except Exception as e:
                item['申请类型'] = ''
            try:
                item['注册分类'] = detail_xpath.xpath('td[5]/text()')[0].strip()
            except Exception as e:
                item['注册分类'] = ''
            try:
                item['企业名称'] =  [cname.strip() for cname in detail_xpath.xpath('td[6]/text()')[0].split() if check_contain_chinese(cname)]
            except Exception as e:
                item['企业名称'] = []
            try:
                item['承办日期'] = detail_xpath.xpath('td[7]/text()')[0].strip()
            except Exception as e:
                item['承办日期'] = ''
            print(item)
            if not get_medicine_data_from_db(item):
                write2mongo(item)
            item_num += 1
            item_date = datetime.datetime.strptime(item['承办日期'], '%Y-%m-%d')
            if (item_date - datetime.datetime.strptime(str_datestr, '%Y-%m-%d')).days < 0:     # 承办日期小于起始日期，搜索终止
                return items_list, False
            if (item_date - datetime.datetime.strptime(str_dateend, '%Y-%m-%d')).days < 0:     # 承办日期小于终止日期，添加条目
                items_list.append(item)
        return items_list, True
    except socket.gaierror as e:
            print("网络中断")
    except IndexError as e:
        print("页面信息错误")
    except Exception as e:
        if times < 3:
            times += 1
            return accept_list_one_page(page_num, page_total, current_page, str_datestr, str_dateend, times)
        else:
            return items_list, True

def check_contain_chinese(check_str):
    """
    判断字符串是否包含中文
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def name_filter(item_list):
    '''
    输入：药品受理条目列表
    输出：受理号第一位为C，申请类型不为进口，且不包含'（中国）'的公司
    '''
    result_set = set([])
    for item in item_list:
        if item['受理号'][0] == 'C' or '进口' in item['申请类型']:
            for cname in item['企业名称']:
                if '（中国）' not in cname:
                    result_set.add(cname)
    return result_set

def medicine_filter_api(str_datestr, str_dateend):
    """
    输入：起始日期，终止日期
    输出：期间有药物受审的
         [中国企业列表，符合条件企业列表]
    """
    update_item_list = get_update_accept_list(str_datestr, str_dateend)    # 正式爬虫
    # update_item_list = accept_list_one_page(0, 0, 1, str_datestr, str_dateend)[0]   # 单页测试
    apply_company_set = name_filter(update_item_list)
    wanted_company_list = []
    # for com in apply_company_set:
    #     # if tyc.search_company(tyc.search_detail(com)) == 1:    # 实际用
    #     #     wanted_company_list.append(com)
    #     try:    # 测试用
    #         if tyc.filter_company(qcc.search_detail(com)) == 1:
    #             wanted_company_list.append(com)
    #     except:
    #         pass
    return list(apply_company_set), wanted_company_list

def test(str_datestr, str_dateend):
    result = medicine_filter_api(str_datestr, str_dateend)
    print('结果：')
    print('-----------------所有公司--------------------')
    for r in result[0]:
        print(r)
    print('------------------符合要求-------------------')
    for w in result[1]:
        print(w)

if __name__ == '__main__':
    update_medicine_data()   # 定时爬取指令，部署在服务器上时不要注释
    # test('2017-01-01', '2017-01-02')
    # print get_update_accept_list()



