# coding:utf-8
"""
create on Apr 6, 2017 By Wenyan Yu
website:www.mryu.top
该文件主要实现主要的爬虫功能
(1)针对某一关键词对百度的进行新闻咨询的获取

"""

import requests
import urllib.request, urllib.parse, urllib.error
import sys
import lxml.html
import json
import sys
import re
from textrank4zh import TextRank4Keyword, TextRank4Sentence

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}

def reduce_tag(text):
    dr = re.compile(r'<[^>]+>', re.S)
    text = dr.sub('', text)
    text = text.strip()
    return text

def get_text(elem):
    rc = []
    for node in elem.itertext():
        rc.append(node.strip())
    return ''.join(rc)

def search_one_new(href):
    r=requests.get(href)
    print(r.url)
    text=reduce_tag(r.content)
    return text


def baidu_news_search(keyword, page_cnt=3,news_cnt=10):
    """
    该方法主要是实现对百度新闻资讯的获取。
    其中keyword为关键字,page_cnt为获取页面列表的数量,news_cnt为获取新闻的数量
    百度新闻搜索链接样式如下:

    http://news.baidu.com/ns?word=抗体&pn=10&cl=2&ct=0&tn=news&ie=utf-8&bt=0&et=0

    :param keyword:
    :param page_cnt:
    :param news_cnt:
    :return: news_list
    """
    news_list = []  # 搜索百度新闻结果返回列表
    url = 'http://www.baidu.com/ns?'
    try:

        for page in range(page_cnt):
            payload = {'tn': 'news', 'word': keyword, 'pn': page*10, 'ct': 0}
            r=requests.get(url+urllib.parse.urlencode(payload),headers=headers,timeout=5)
           # print (r.url)
            dom = lxml.html.document_fromstring(r.content)
            result_cnt = len(dom.xpath('//div[@class="result"]'))
           # print ("news_cnt",result_cnt)
            news_cnt_temp = 1
            for i in range(1,result_cnt+1):
                title_node = dom.xpath('//div[@class="result"]['+str(i)+']/h3/a')[0]
                href = dom.xpath('//div[@class="result"]['+str(i)+']/h3/a')[0].get('href')
                detail_info = str(dom.xpath('//p[@class="c-author"]/text()')[i-1])
                first_number_index = detail_info.index('2')
                title = get_text(title_node)
                time = detail_info[first_number_index:]
                stem_from = detail_info[0:first_number_index]
                temp = []
                temp.append(time)
                temp.append(title)
                temp.append(stem_from)
                temp.append(href)
                temp.append(news_cnt_temp)
                news_list.append(temp)
                news_cnt_temp += 1
                if news_cnt_temp > news_cnt:
                    return news_list
                # print (time)
                # print (title)
                # print (stem_from)
                # print (href)
    except (ValueError,AttributeError):
            return news_list

    return news_list

#baidu_news_search(u"单克隆抗体",2)

