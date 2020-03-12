# -*- coding: utf-8 -*-
"""
佰腾专利搜索
"""
import multiprocessing
import urllib.request, urllib.parse, urllib.error
from collections import defaultdict

import jieba
import lxml.html
import pymongo
import requests
import itertools
import pandas as pd


from .trie_search import LBTrie
from lib.db_connection import *


db = mongodb_connection('news')

"""抽取内容"""
def getText(elem):
    rc = []
    for node in elem.itertext():
        rc.append(node.strip())
    return ''.join(rc)

"""多页搜索"""
def search_more_pages(url,query,intent_dict):

    r=requests.get(url)
    dom=lxml.html.document_fromstring(r.content)
    content_div=dom.xpath('//div[@id="srl-m-vc"]')[0]
    intent_len=len(content_div.xpath('./div[@class="sm-c clearfix"]'))
    intent_total=content_div.xpath('./div[@class="sm-c clearfix"]')
    for i in range(intent_len):
        type=intent_total[i].xpath('./ul/li[1]/span[4]')[0].text
        intent_url='http://so.baiten.cn'+intent_total[i].xpath('./ul/li[1]/a[1]')[0].get('href').strip()
        name=intent_total[i].xpath('./ul/li[1]/a[1]')[0]
        name = getText(name)
        apply_name=intent_total[i].xpath('./ul/li[3]/span/a[1]')[0]
        apply_name=getText(apply_name)
        keywords = title_based([name])
        query = ' '.join(keywords[0][1])
        intent_dict[name]={'type':type,'intent_url':intent_url,'apply_name':apply_name,'key':query}

    return intent_dict

#searchtype=0：按照企业名称进行搜索
#searchtype=1:按照专利关键字进行搜索
"""搜索主入口，输入搜索词，得到搜索结果"""
def search(query):

    #type的意思是抓取的专利类型,只抓取发明专利和发明授权专利，type为9
    para={
        'type':9,
        's':0,
        'law':0,
        'v':'s'
    }
    para['q']=query

    url='http://so.baiten.cn/results?'+urllib.parse.urlencode(para)

    r=requests.get(url)

    dom=lxml.html.document_fromstring(r.content)
    content_div=dom.xpath('//div[@id="srl-m-vc"]')[0]
    intent_len=len(content_div.xpath('./div[@class="sm-c clearfix"]'))
    intent_total=content_div.xpath('./div[@class="sm-c clearfix"]')
    #print intent_len
    intent_dict=dict()
    for i in range(intent_len):
        type=intent_total[i].xpath('./ul/li[1]/span[4]')[0].text
        intent_url='http://so.baiten.cn'+intent_total[i].xpath('./ul/li[1]/a[1]')[0].get('href').strip()
        name=intent_total[i].xpath('./ul/li[1]/a[1]')[0]
        name=getText(name)
        apply_name=intent_total[i].xpath('./ul/li[3]/span/a[1]')[0]
        apply_name=getText(apply_name)
        if type!='失效专利' and name!=None:
            keywords = title_based([name])
            query = ' '.join(keywords[0][1])
            print(name)
            intent_dict[name]={'type':type,'intent_url':intent_url,'apply_name':apply_name,'key':query}
    pages=len(dom.xpath('//div[@class="pages"]/span[@class="item"]'))
    #print pages
    #如果有多页，进一步进行爬取
    for i in range(2,pages+2):
        new_url=url+'&page='+str(i)
        intent_dict=search_more_pages(new_url,query,intent_dict)
       # print len(intent_dict.keys())

    for key,value in list(intent_dict.items()):
        intent_url=value['intent_url']
        r=requests.get(intent_url)
        dom=lxml.html.document_fromstring(r.content)
        try:
            summary=dom.xpath('//p[@class="pd-d-c-g-txt"]')[0].text.strip()
        except:
            summary=''
        value['summary']=summary
    #print len(intent_dict.keys())
    return intent_dict

def process(keys,samiliar_intent_dict):
    for key in keys:
        keywords=title_based([key])
        samiliar_intent_dict[key]=dict()
        #print key
        samiliar_intent_dict[key]=dict()
        if len(keywords[0][1])>4:
            # #print keywords[0][1]
            # for t in range(4,5):
            #     querylist = [' '.join(x) for x in itertools.combinations(list(keywords[0][1]), t)]
            #     print querylist
            #     for word in querylist:
            #         query = word
            #         #print query
            #         samiliar_intent_dict[key] = dict(samiliar_intent_dict[key].items() + search(query.encode('utf-8')).items())
            query = ' '.join(keywords[0][1][:4])
        else:
            query=' '.join(keywords[0][1])
            #print query
        #samiliar_intent_dict[key] = dict(samiliar_intent_dict[key].items() + search(query.encode('utf-8')).items())
        samiliar_intent_dict[key]=search(query.encode('utf-8'))
        #print samiliar_intent_dict

def get_stopcompanys():
    """得到过滤公司"""
    return [item['name'] for item in db.stopcompanys.find()]

def search_samiliar(intent_dict,samiliar_intent_dict):
    keys=list(intent_dict.keys())
    splitlist = [0, len(keys) // 4, len(keys) // 4 * 2, len(keys) // 4 * 3, len(keys)]
    process_dict={}
    for i in range(4):
        process_dict[i] = multiprocessing.Process(target=process, args=(keys[splitlist[i]:splitlist[i + 1]],samiliar_intent_dict))
        process_dict[i].start()
    while True:
        if not (process_dict[0].is_alive() or process_dict[1].is_alive() or process_dict[2].is_alive() or process_dict[3].is_alive()):
            break
    #print samiliar_intent_dict

"""得到停用词列表"""
def get_stopwords():


    stopwords = [item['stopword'] for item in db.stopwords.find()]
    #conn.close()
    return stopwords



"""提取专利标题中的关键词"""
def title_based(titles):
    keywords = []
    # flag_dic = defaultdict(int)#词性过滤
    trie_obj = LBTrie()
    # 添加单词
    corpus = open('content.txt', 'r')
    countdic = defaultdict(int)
    for record in corpus.readlines():
        recordlist = record.split(' ')
        # 去掉一条专利中的重复词语
        recordlist = list(set(recordlist))
        for word in recordlist:
            # word = word.decode('utf-8', 'ignore').encode('GBK', 'ignore').decode('GBK', 'ignore')
            check = trie_obj.add(word)

            if check:
                countdic[word] += 1
    for title in titles:
        #stopwords = ([line.rstrip() for line in open('stopword.txt')])
        stopwords = get_stopwords()
        new_countdic = defaultdict(int)
        lt = jieba.cut(title)
        keyword = []
        for w in lt:
            if w not in stopwords:
                # flag_dic[w.flag] += 1
                keyword.append(w)

        for l in keyword:
            if countdic[l]:
                new_countdic[l] = countdic[l]
            else:
                new_countdic[l] = 0
        resortedcountdic = sorted(list(new_countdic.items()), key=lambda item: item[1])  # ascending order
        fil_list = []

        for tup in resortedcountdic:
            fil_list.append(tup[0])
        keywords.append((title, fil_list))
    return keywords

"""搜索企业的时候先搜索mongodb"""
def findInMongo(query):
    conn = pymongo.MongoClient('106.75.65.56', 27017)
    db=conn['CFDA']
    account_baiteng=db['baiteng']
    result = account_baiteng.find_one({'公司名称':query})
    #如果数据库中不存在记录，则进行抓取
    if result:
        return result
    else:
        intent_dict, company_list = findInWeb(query)
        return intent_dict, company_list

def getCompanyName(similiar_intent_dict,query):
    company_list=dict()
    i=1
    for key,value in list(similiar_intent_dict.items()):
        for key1,value1 in list(value.items()):
            if ('公司' in value1['apply_name']) and (value1['apply_name'] != query):
                #print value1['apply_name']

                company_list[i]={'intent':key1,'s_intent':key,'apply_name':value1['apply_name']}
                i+=1
                    #([key,key1,value1['apply_name']])

    return company_list

"""mongodb中没有的话，再进行信息抓取"""
def findInWeb(query):
    manager = multiprocessing.Manager()
    samiliar_intent_dict=manager.dict()
    intent_dict = search(query)
    print(intent_dict)
    search_samiliar(intent_dict,samiliar_intent_dict)
    #print len(samiliar_intent_dict.keys())
    company_list=getCompanyName(samiliar_intent_dict,query)
    return intent_dict,company_list


#samiliar_intent=search_samiliar(intent_dict,company_name)
#print samiliar_intent

def baiteng_search(wordlist):
    """两两组合关键词进行搜索"""
    newlist=[]
    print(wordlist)

    for i in range(len(wordlist)-2):
        for j in range(i+1,len(wordlist)-1):
            query = wordlist[i]+" "+wordlist[j]
            """搜索专利数量"""
            count = baiteng_search_count(query)

            print (query)
            if count > 0 and count <= 500:
                """如果专利数在[0,500]之间，得到相应的公司列表"""
                company_list = baiteng_search_company(query)
                newlist.append((query,count,company_list))
    return newlist


def baiteng_search_count(query):
    """搜索对应query的专利数量"""
    para = {
        'type': 9,
        's': 0,
        'law': 0,
        'v': 's'
    }
    para['q'] = query
    url = 'http://so.baiten.cn/results?' + urllib.parse.urlencode(para)
    r = requests.get(url)
    dom=lxml.html.document_fromstring(r.content)
    #提取数量
    count = dom.xpath('//span[@id="sop-totalCount"]')[0].text if dom.xpath('//span[@id="sop-totalCount"]') else 0
    return int(count)

def get_search_html(url):
    """得到搜索结果的页面内容"""
    try:
        r = requests.get(url)
        return r.content
    except :
        print('搜索错误')
        return None

def get_pages(html):
    """得到搜索结果一共有多少页"""
    try:
        dom = lxml.html.document_fromstring(html)
        pages = len(dom.xpath('//div[@class="pages"]/span[@class="item"]'))
        return pages
    except:
        return 0


def getText(elem):
    """抽取内容"""
    rc = []
    for node in elem.itertext():
        rc.append(node.strip())
    return ''.join(rc)

def baiteng_search_company(query):
    """得到对应query的生产企业"""
    apply_list = []
    para = {
        'type': 9,
        's': 0,
        'law': 0,
        'v': 's'
    }
    para['q'] = query
    url = 'http://so.baiten.cn/results?' + urllib.parse.urlencode(para)
    html = get_search_html(url)
    """得到该页的公司名称"""
    apply_list.extend(parse_company_name(html))
    pages = get_pages(html)

    for page in range(2,pages+2):
        new_url = url + '&page=' + str(page)
        html = get_search_html(new_url)
        apply_list.extend(parse_company_name(html))
    return apply_list

def parse_company_name(html):
    """得到公司名称"""
    dom = lxml.html.document_fromstring(html)
    content_div = dom.xpath('//div[@id="srl-m-vc"]')[0]
    intent_len = len(content_div.xpath('./div[@class="sm-c clearfix"]'))
    intent_total = content_div.xpath('./div[@class="sm-c clearfix"]')
    # print intent_len
    intent_dict = dict()
    apply_list = []

    for i in range(intent_len):

        name = intent_total[i].xpath('./ul/li[1]/a[1]')[0]
        name = getText(name)
        apply_name = intent_total[i].xpath('./ul/li[3]/span/a[1]')[0]
        apply_name = getText(apply_name)
        db = mongodb_connection('news')
        stopcompanys = get_stopcompanys()
        if ('公司' in apply_name) and (apply_name not in stopcompanys):
            print(apply_name)
            apply_list.append([name,apply_name])
    return apply_list

