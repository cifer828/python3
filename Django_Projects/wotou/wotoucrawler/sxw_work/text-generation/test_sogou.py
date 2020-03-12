#-*-coding:utf-8-*-#
import requests

import lxml.html
import selenium
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import urllib
import time
import urllib2
import socket
from httplib import BadStatusLine
import json
import sys
reload(sys)

sys.setdefaultencoding('utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}

time_out=20
url1 = 'https://www.sogou.com/web?'
base_url='http://www.baidu.com'

def driver_config():
 #dcap['phantomjs.page.settings.userAgent']=random.choice(user_agent)

    driver=webdriver.PhantomJS()

    driver.implicitly_wait(10)
    driver.set_page_load_timeout(20)
    return driver

def search(payload,driver):

    url=url1+urllib.urlencode(payload)
    print url
   # r = requests.get(url+urllib.parse.urlencode(payload), headers=headers, timeout=5)
    driver.get(url)
    try:
        WebDriverWait(driver, time_out).until(
            EC.presence_of_element_located((By.ID, 'kmap_entity_div')))

    except TimeoutException:
        return {}


    map_dict=dict()

    source = driver.page_source
    dom = lxml.html.document_fromstring(source)
    if len(dom.xpath('//div[@id="kmap_entity_div"]'))>0:
        table=dom.xpath('//div[@id="kmap_entity_div"]')[0]
        print (table)


        h3_len=len(table.xpath('./ul'))
        print (h3_len)
        for i in range(1,h3_len+1):
            #index=0
            type=table.xpath('./h3['+str(i)+']/span')[0].text
            print (type)
            #print (type)
            map_dict[type]=[]
            first_low=len(table.xpath('./ul['+str(i)+']/li'))
            print first_low
            for j in range(1,first_low+1):
                #url1=table.xpath('./div['+str(i+1)+']/div[1]/div['+str(j)+']/div[2]/a')[0].get('href')[3:]
                #print (url1)
                #print j
                #if table.xpath('./ul['+str(i)+']/li['+str(j)+']/span')!=[]:
                text1=table.xpath('./ul['+str(i)+']/li['+str(j)+']/a[2]/span')[0].text.strip()
                #print (text1)1
                #print text1
                map_dict[type].append(text1)

            # if len(table.xpath('./div['+str(i+1)+']/textarea'))>0:
            #     show_up=table.xpath('./div['+str(i+1)+']/textarea')[0].value
            #     sub_dom = lxml.html.document_fromstring(show_up.strip())
            #     domdiv=sub_dom.xpath('//div[@class="opr-recommends-merge-morelists"]')[0]
            #     row_len=len(domdiv.xpath('./div'))
            #     #print (row_len)
            #     for t in range(1,row_len+1):
            #         col_len=len(domdiv.xpath('./div['+str(t)+']/div'))
            #         #print (col_len)
            #         for s in range(1,col_len):
            #             #print (len(domdiv.xpath('./div['+str(t)+']/div['+str(s)+']/div')))
            #             #url1=domdiv.xpath('./div['+str(t)+']/div['+str(s)+']/div[2]/a')[0].get('href')[3:]
            #             text1=domdiv.xpath('./div['+str(t)+']/div['+str(s)+']/div[2]/a')[0].text
            #             #print (url1)
            #             #print (text1)
            #             map_dict[type].append(text1)
    return map_dict

r=requests.get('http://www.bioon.com',headers=headers,timeout=5)
print (r.url)
dom=lxml.html.document_fromstring(r.content)

table=dom.xpath('//div[@class="index_left_menu"]')[0]
li_len=len(table.xpath('./ul/li'))

print (li_len)
wordlist=[]
crawllist=[]
for i in range(2,li_len+1):
    p_len=len(table.xpath('./ul/li['+str(i)+']/p/a'))
    for j in range(1,p_len+1):
        text=table.xpath('./ul/li[' + str(i) + ']/p/a['+str(j)+']')[0].text
        sub_url=table.xpath('./ul/li[' + str(i) + ']/p/a['+str(j)+']')[0].get('href')
        #print (text)
        #print (sub_url)
        if text!="" and text!=None:
            wordlist.append(text)

wordlist=[u'生物医药']
for word in wordlist:
    print word
    driver=driver_config()
    payload = {'query': word}
    word_dict=dict()

    word_dict[word]=search(payload,driver)
    driver.close()

    for key,value in word_dict[word].items():
        for i in range(len(value)):
            print value[i].encode('utf-8')
            driver = driver_config()
            payload={'query':value[i].encode('utf-8')}
            word_dict[value[i]]=search(payload,driver)
            driver.close()

            # for key1,value1 in word_dict[value[i]].items():
            #     for t in range(len(value1)):
            #         payload={'wd':value1[t]}
            #         word_dict[value1[t]]=search(payload)
    #createPlot(word_dict)
            #print (word_dict)

    jsObj = json.dumps(word_dict,ensure_ascii=False)

    fileObject = open('sougou/sougou_'+word+'.json', 'w')
    fileObject.write(jsObj)
    fileObject.close()
    crawllist.append(word)
    print crawllist




