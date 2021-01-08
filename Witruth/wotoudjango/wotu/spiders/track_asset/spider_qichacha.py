# -*- coding:utf-8 -*-#
"""
企查查搜索
"""

from lxml import html
import requests
import re
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import time
import random
import datetime
import os
from wotu.spiders.track_asset import proxies
from wotu.config.config import MONGO_SERVER
from wotu.config.config import MONGO_PORT
import pymongo
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.common.by import By

import selenium.webdriver.support.expected_conditions as EC
from wotu.spiders.track_asset import spider_tianyancha as tyc
from bson.dbref import DBRef
from wotu.lib.error import CookiesError
from wotu.spiders.track_asset.cookies_pool_for_qichacha import cookie_dict_list
from selenium.common.exceptions import TimeoutException
from wotu.spiders.track_asset import spider_tianyancha as tyc

CONN = pymongo.MongoClient(MONGO_SERVER, MONGO_PORT)    # 数据库
PROXIES = proxies.abuyun_proxy()    # ip代理
cookie_dict=cookie_dict_list[0]
# cookie_dict=cookie_dict_list[random.randint(0,len(cookie_dict_list)-1)]
# cookie_dict={}

# selenium + phantomjs 配置
caps = DesiredCapabilities.PHANTOMJS
header = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36',
    'host': "www.qichacha.com",
    'Accept': 'text/html, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Connection': 'keep-alive',
    'Content-Length': '0',
    'Origin': 'http://www.qichacha.com',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://www.qichacha.com/search?key=%E6%B7%B1%E5%9C%B3%E5%B8%82%E6%B7%B1%E5%88%9B%E6%8A%95%E5%88%9B%E4%B8%9A%E6%8A%95%E8%B5%84%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8'
}
caps["phantomjs.page.settings.userAgent"] = \
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36"
driver = webdriver.PhantomJS(desired_capabilities=caps)
driver.implicitly_wait(8)
driver.set_page_load_timeout(20)

basic_url = 'http://www.qichacha.com'

# def search_investment_company(asset_name):
#     """
#     :param asset_name: 基金名称
#     :return: 符合要求公司列表，旗下所有公司列表
#     """
#     global wanted_company_list, all_company_list
#     get_info(asset_name)
#     return wanted_company_list, all_company_list

def get_company_list_page_html(company_name, page):
    """
    输入股东，查询其投资的公司
    返回查询结果页面
    """
    base_url = 'http://www.qichacha.com/search_index?'
    data = {'key': company_name,
            'ajaxflag': '1',
            'index': '14',
            'p': str(page),
            '': ''}
    url = base_url + urllib.parse.urlencode(data)
    r = requests.get(url, headers=header, cookies=cookie_dict, proxies=proxies)
    # 企查查故意不闭合<em>标签，导致xpath路径报错
    return r.content.decode('utf8').replace('</em... ', '').replace("<em>", "").replace("</em>","")


def is_cookies_useful(result):
    if "后可以查看更多数据哦" in result:
        return False
    else:
        return True


def change_cookies():
    global cookie_dict, driver
    try:
        cookie_dict_list.remove(cookie_dict)
    except Exception as e:
        pass
    cookie_dict=cookie_dict_list[random.randint(0,len(cookie_dict_list)-1)]
    driver.delete_all_cookies()
    driver.add_cookie(cookie_dict)

def search_single_investment_company(asset_name):
    """
    获取公司列表
    """
    investment_company_list = []
    non_investment_company_list = []

    result = get_company_list_page_html(asset_name, 1)

    if not is_cookies_useful(result):
        raise CookiesError("企查查账户cookies失效")

    root = html.fromstring(result)
    company_num_xpath = '//span[@class="text-danger"]/text()'

    company_num = root.xpath(company_num_xpath)
    if len(company_num) > 0:
        company_num = int(company_num[0])
    else:
        return [], []
    pages = int((company_num - 1) / 10) + 1
    investment_company_list, non_investment_company_list = deal_with_one_page_html(result, investment_company_list,
                                                                                   non_investment_company_list)
    # 翻页
    if pages > 1:
        for i in range(2, pages + 1):
            time.sleep(3)
            investment_company_list, non_investment_company_list = deal_with_one_page_html(
                get_company_list_page_html(asset_name, i), investment_company_list, non_investment_company_list)

    return investment_company_list, non_investment_company_list


def deal_with_one_page_html(content, investment_company_list, non_investment_company_list):
    """
    提取html页面中公司信息
    """
    root = html.fromstring(content)
    name_xpath = '//tbody/tr/td[2]/a/text()'

    name_list = root.xpath(name_xpath)
    if not name_list:
        return investment_company_list, non_investment_company_list

    for item in name_list:
        if is_investment_company(item):
            investment_company_list.append(item)
        else:
            non_investment_company_list.append(item)

    return investment_company_list, non_investment_company_list

def is_investment_company(company_name):
    if '有限合伙' in company_name or '投资' in company_name or '基金管理' in company_name:
        return True
    else:
        return False

def company_detail_by_id(id, times=0):
    """
    获取公司主页内信息
    输入：企查查内公司id
    输出：公司全称、曾用名、地址、地区、省份、行业、注册资本
          股东状况[股东, 出资比例] 成立时间 企业资质[专利数,著作权数] 联系方式[电话，邮箱] 上市情况
    """
    global driver
    href = 'https://www.qichacha.com/firm_%s.shtml' % id
    try:
        #  基本信息标签
        for key, value in cookie_dict.items():
            driver.add_cookie({'domain': '.qichacha.com',
                               'name': key,
                               'value': value,
                               'path':'/',
                               'httponly':'True',
                               'secure':'False'})
        driver.get(href)
        wait = WebDriverWait(driver, 10)

        # **顶部信息**
        top_element = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="company-top"]/div/div[1]/span[2]')))
        # 公司全称
        try:
            full_name =  top_element.find_element_by_xpath('./span/span[1]').text
        except Exception as e:
            full_name = ''
        # 是否上市
        try:
            first_small_text =  top_element.find_element_by_xpath('./small[1]').text
            # 上市公司页面有3个small标签，第一个为"上市详情："
            on_list =  '上市详情' in first_small_text
        except Exception as e:
            on_list = False
        adjust_num = 2 if on_list else 1    # 上市公司small标签延后
        # 电话
        try:
            phone_str =  top_element.find_element_by_xpath('./small[%d]' % adjust_num).text.strip()
            phone = re.findall('：(\S+)', phone_str)[0]
        except Exception as e:
            phone = ''
        # 邮箱
        try:
            email_str =  top_element.find_element_by_xpath('./small[%d]/a[1]' % adjust_num).text.strip()
            email = re.findall('：(\S+)', email_str)[0]
        except Exception as e:
            email = ''
        # 官网
        try:
            website =  top_element.find_element_by_xpath('./small[%d]/a[2]' % adjust_num).get_attribute('href')
        except Exception as e:
            website = ''


        # **基本信息**
        contain_element = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="Cominfo"]/table/tbody')))
        # 曾用名
        try:
            history_name =  contain_element.find_element_by_xpath('./tr[8]/td[2]').text
        except Exception as e:
            history_name = ''
        # 法定代表人
        try:
            principle =  contain_element.find_element_by_xpath('./tr[3]/td[2]/a[1]').text
        except Exception as e:
            principle = ''
        # 公司地址
        try:
            location = contain_element.find_element_by_xpath('./tr[9]/td[2]').text.split()[0]
        except Exception as e:
            location = ''
        # 省市
        try:
            province = re.findall('(.+省)', location)[0]
        except Exception as e:
            province = ''
        try:
            city = re.findall('([^省]+市)', location)[0]
        except Exception as e:
            city = ''
        # 公司行业
        try:
            industry = contain_element.find_element_by_xpath("./tr[7]/td[2]" ).text
        except Exception as e:
            industry = ''
        # 公司注册资本
        try:
            money_str = contain_element.find_element_by_xpath('./tr[3]/td[4]').text
            money = float(re.findall('([\d|\.]+)', money_str)[0])
            if '美元' in money_str:
                money *= 6.8947
        except Exception as e:
            money = ''


        # **股东信息**
        holders_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="Sockinfo"]')))
        # 股东数量
        try:
            holder_num = int(holders_element.find_element_by_xpath('./div[1]/span[2]').text)
        except Exception as e:
            holder_num = 0
        # 股东信息
        try:
            holders = []
            for idx in range(2, holder_num + 2):
                holder = holders_element.find_element_by_xpath('./table/tbody/tr[%d]'% idx)
                holders.append({'股东名称': holder.find_element_by_xpath('./td[1]/a[1]').text,
                                '出资比例': holder.find_element_by_xpath('./td[2]').text})
        except Exception as e:
            holders = []
        # 成立时间
        try:
            founded_time = contain_element.find_element_by_xpath('./tr[4]/td[4]').text
        except Exception as e:
            founded_time = ''


        # **知识产权信息**
        driver.find_element_by_id('assets_title').click()
        time.sleep(3)   # 时间过短可能仍停留在基本信息界面
        wait2 = WebDriverWait(driver, 10)
        asset_element = wait2.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="assets_div"]/section[1]/div')))
        # 专利数量
        try:
            patent = asset_element.find_element_by_xpath('./a[2]').text
            patent_count = int(patent.split()[-1])
        except Exception as e:
            patent_count = 0
        # 著作权 + 软件著作权
        try:
            copyright = asset_element.find_element_by_xpath('./a[4]').text
            software_copyright = asset_element.find_element_by_xpath('./a[5]').text
            copyright_count = int(copyright.split()[-1]) + int(software_copyright.split()[-1])
        except Exception as e:
            copyright_count = 0

        return {"企业全称": full_name, '曾用名':history_name, "公司地址": location, '省份':province, '地区':city,
                "行业": industry, "注册资本": money, "成立日期": founded_time,
                '联系方式': {'电话': phone, '邮箱': email}, '官网':website,
                '链接': href, "股东状况": holders, '主要负责人': principle,
                "企业资质": {'专利数': patent_count, '著作权数': copyright_count}, "是否上市": on_list}

    except TimeoutException as e:
        print(e.args)
        if times < 5:
            print('crawl again')
            times += 1
            return company_detail_by_id(id, times)
        else:
            return {}

def search_detail(company_name):
    """
    药品受理&临床试验-企查查搜索接口
    输入：公司名称
    输出：详细信息
    """
    base_url = 'http://www.qichacha.com/search?'
    data = {'key': company_name}
    url = base_url + urllib.parse.urlencode(data)
    r = requests.get(url, headers=header, cookies=cookie_dict, proxies=PROXIES)
    root = html.fromstring(r.content)
    try:
        match_company_tag = root.xpath('//section[@id="searchlist"]/table/tbody/tr[1]/td[2]/a')[0]
        match_company_em = match_company_tag.xpath('em')[0]     # 没有em标签说明匹配不准确，抛出异常
        match_company_id = re.findall('_(.+)\.', match_company_tag.xpath('@href')[0])[0]
        return company_detail_by_id(match_company_id)  # 借用天眼查过滤函数
    except Exception as e:
        print(e.args)
        return {}
        # raise Exception('未找到匹配企业')

def search_iteration_investment_company(test_company, is_update=False):
    db = CONN['company']
    collection = db['investment_company']
    detail = {'公司名称': test_company}
    ret = collection.find_one(detail)

    non_investment_company_id_list = []
    investment_company_id_list = []

    if not ret:
        _id = collection.insert(detail)
    else:
        _id = ret['_id']

    if (not ret) or ('公司列表' not in ret) or is_update:
        try:
            investment_company_list, non_investment_company_list = search_single_investment_company(test_company)

            for i in non_investment_company_list:

                non_investment_company_detail = search_detail(i)
                if non_investment_company_detail:
                    non_investment_company_id_list.append(DBRef("raw_company", non_investment_company_detail['_id']))

            for i in investment_company_list:
                investment_company_id_list.append(DBRef("investment_company", search_iteration_investment_company(i)))

            collection.update({"公司名称": test_company}, {
                "$set": {"基金公司列表": investment_company_id_list, "公司列表": non_investment_company_id_list,
                         "更新时间": time.strftime('%Y-%m-%d', time.localtime(time.time()))}})
        except CookiesError as e:
            print(e.value,cookie_dict)
            change_cookies()
            return search_iteration_investment_company(test_company,is_update)
        except requests.exceptions.ProxyError as e:
            print("网络中断，重试中")
            return search_iteration_investment_company(test_company,is_update)
        except requests.exceptions.ConnectionError as e:
            print("网络中断，重试中")
            return search_iteration_investment_company(test_company, is_update)
    return _id

if __name__ == '__main__':
    # print(search_company('江苏凌特精密机械有限公司'))
    # print(search_company('连云港润众制药有限公司'))
    # print(search_company('中国科学院上海药物研究所'))
    # white_list2db('business_scope.txt', 'white_list_city')
    # print no_company_stockholder('罗氏（中国）投资有限公司')
    # search_iteration_investment_company('深圳市达晨创业投资有限公司')
    # test_company = get_company_info_in_form('322a269a82343f4a4b67356b26b0cecb', '杭州捷玉投资管理合伙企业（有限合伙）','assets')
    # test_company = get_company_info_in_form('b8870607d3cc6d96bcd6923c87e1116b', '北京丰年微商网络技术服务有限公司', 'assets')
    test_detail = search_detail('怀集登云汽配股份有限公司')
    print(test_detail)
    # for key,value in test_detail.items():
    #     print(key,':', value)
    tyc.filter_company(test_detail)
    # print filter_software_right('5bb5c57393d0c56d3551857ff0bfca05', '北京德同优势投资中心（有限合伙）')
    # print filter_zhuanli('华普生物')
    # test('浙商万嘉（北京）创业投资管理有限公司')
    # print filter_in_search_page('/firm_42a928b566dd27993b6bb9d1364d6ca8.shtml')
    # print filter1('/firm_72461b3134b9c408f5d69d450d538958.shtml')
    # get_info('怀集登云汽配股份有限公司')
    # print(search_company('石药集团中奇制药技术（石家庄）有限公司'))
    pass


