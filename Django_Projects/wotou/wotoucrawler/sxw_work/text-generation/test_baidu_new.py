#-*-coding:utf-8-*-#
import requests

import sys
import lxml.html
import urllib
import matplotlib.pyplot as plt
import json
import sys
import re
from textrank4zh import TextRank4Keyword, TextRank4Sentence
reload(sys)

sys.setdefaultencoding('utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}
url = 'http://news.baidu.com/ns?'
base_url='http://www.baidu.com'
pattern1 =re.compile(r'^.*《.*》.{20,}$')
pattern2=re.compile(r'^.*报告.{20,}$')
pattern3=re.compile(r'^.*发展趋势.{20,}$')
pattern4=re.compile(r'^.*预测.{20,}$')
pattern5=re.compile(r'^var.*$')

def getText(elem):
    rc = []
    for node in elem.itertext():
        rc.append(node.strip())
    return ''.join(rc)

def reduce_tag(text):
    dr = re.compile(r'<[^>]+>', re.S)
    text = dr.sub('', text)
    text = text.strip()
    return text

def search_one_new(href):
    r=requests.get(href)
    print r.url
    text=reduce_tag(r.content)
    #print text
    tr4s = TextRank4Sentence()
    tr4s.analyze(text=text, lower=True, source='all_filters')
    f1 = open('structrue_word.txt')
    words=f1.read().split(',')
    worddict={}
    for word in words:
        worddict[word]=[]

        #print word+'\n'
    for index in range(len(tr4s.sentences)):
        sentence=tr4s.sentences[index]
        for word in words:
            if word in sentence and ('HER2' in sentence):
                if len(sentence.strip())>40 and sentence.startswith(u'图')==False and sentence.startswith(u'表')==False and (not sentence.encode('utf-8') in worddict[word]):
                    flag=True
                    if u'报告' in sentence and not pattern2.match(sentence):
                        continue
                    if u'发展趋势' in sentence and not pattern3.match(sentence):
                        continue
                    if u'预测' in sentence and not pattern4.match(sentence):
                        continue
                    if u'《' in sentence and not pattern1.match(sentence):
                        continue
                    if pattern5.match(sentence):
                        continue


                    #print sentence.encode('utf-8')
                    lowindex=index-3 if index-3>0 else 0
                    highindex=index+4 if index+4<len(tr4s.sentences) else len(tr4s.sentences)
                    print '|||'.join(tr4s.sentences[lowindex:highindex])
                    worddict[word].append('|||'.join(tr4s.sentences[lowindex:highindex]))
                    break
    return worddict




def search(query,page=3,count=5):
    f1 = open('structrue_word.txt')
    words = f1.read().split(',')
    worddict = {}
    for word in words:
        worddict[word] = []

    for onepage in range(page):
        payload={'tn':'news','word':query,'pn':onepage*10,'ct':0}
        r = requests.get(url + urllib.urlencode(payload), headers=headers, timeout=5)

        print (r.url)
        print (r.status_code)
        dom=lxml.html.document_fromstring(r.content)
        result_count=len(dom.xpath('//div[@class="result"]'))
        print result_count

        for i in range(1,result_count+1):
            title_node=dom.xpath('//div[@class="result"]['+str(i)+']/h3/a')[0]
            title=getText(title_node)
            href=dom.xpath('//div[@class="result"]['+str(i)+']/h3/a')[0].get('href')
            #print title,href
            try:
                one_new_dict=search_one_new(href)
            except:
                continue
            for key in worddict.keys():
                worddict[key].extend(one_new_dict[key])



    f=open('test.txt','w+')
    for key,value in worddict.items():
        f.write(key+'\n')
        f.write('\n'.join(value)+'\n')
        f.write('\n\n\n')
    f.close()

def crawl_baike_sub(url,query):
    r=requests.get(url)
    dom=lxml.html.document_fromstring(r.content)
    defination=dom.xpath('//div[@class="lemma-summary"]/div')[0]
    defination=getText(defination)
    main_content_len=len(dom.xpath('//div[@class="main-content"]/div'))
    main_content=dom.xpath('//div[@class="main-content"]/div')
    jianjie=''
    for i in range(main_content_len):
        if main_content[i].get('class')=='para-title level-2':
            if getText(main_content[i].xpath('./h2')[0])==(query+u'简介'):
                j=i+1
                while True:
                    if main_content[j].get('class')=='para':
                        jianjie+=(getText(main_content[j]).strip()+'\n')
                        j=j+1
                    else:
                        break
                break

    return defination,jianjie



def crawl_baike(query):
    baike_base_url="http://baike.baidu.com/search?&pn=0&rn=0&enc=utf8&sefr=sebtn&word="+query
    r=requests.get(baike_base_url)
    dom=lxml.html.document_fromstring(r.content)
    div=dom.xpath('//dl[@class="search-list"]')[0]
    item_count=len(div.xpath('./dd'))
    item_dict=dict()
    print item_count
    for i in range(item_count):
        url=div.xpath('./dd')[i].xpath('./a')[0].get('href')
        item_name=div.xpath('./dd')[i].xpath('./a')[0]
        item_name=getText(item_name)[:-5]
        #print url
        #print item_name
        item_dict[item_name]=dict()
        item_dict[item_name][u'定义'],item_dict[item_name][u'简介']=crawl_baike_sub(url,item_name)
    #print item_dict
    for key,value in item_dict.items():
        print key
        for key1,value1 in value.items():
            print key1
            print value1
            print '\n'


#crawl_baike(u'单克隆抗体')