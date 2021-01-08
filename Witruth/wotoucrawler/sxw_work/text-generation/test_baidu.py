#-*-coding:utf-8-*-#
import requests

import sys
import lxml.html

import urllib
import matplotlib.pyplot as plt
import json
import sys
reload(sys)

sys.setdefaultencoding('utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}
url = 'http://www.baidu.com/s?'
base_url='http://www.baidu.com'




def search(payload):

    r = requests.get(url+urllib.urlencode(payload), headers=headers, timeout=5)
    print (r.url)
    print (r.status_code)
    #print (r.content)

    map_dict=dict()


    dom = lxml.html.document_fromstring(r.content)
    if len(dom.xpath('//div[@class="opr-recommends-merge-content"]'))>0:
        table=dom.xpath('//div[@class="opr-recommends-merge-content"]')[0]
        div_len=len(table.xpath('./div'))
        print (div_len)
        for i in range(1,div_len+1,2):
            #index=0
            type=table.xpath('./div['+str(i)+']/span')[0].text
            #print (type)
            map_dict[type]=[]
            first_low=len(table.xpath('./div['+str(i+1)+']/div[1]/div'))
            for j in range(1,first_low+1):
                #url1=table.xpath('./div['+str(i+1)+']/div[1]/div['+str(j)+']/div[2]/a')[0].get('href')[3:]
                #print (url1)
                text1=table.xpath('./div['+str(i+1)+']/div[1]/div['+str(j)+']/div[2]/a')[0].text
                #print (text1)1
                map_dict[type].append(text1)

            if len(table.xpath('./div['+str(i+1)+']/textarea'))>0:
                show_up=table.xpath('./div['+str(i+1)+']/textarea')[0].value
                sub_dom = lxml.html.document_fromstring(show_up.strip())
                domdiv=sub_dom.xpath('//div[@class="opr-recommends-merge-morelists"]')[0]
                row_len=len(domdiv.xpath('./div'))
                #print (row_len)
                for t in range(1,row_len+1):
                    col_len=len(domdiv.xpath('./div['+str(t)+']/div'))
                    #print (col_len)
                    for s in range(1,col_len):
                        #print (len(domdiv.xpath('./div['+str(t)+']/div['+str(s)+']/div')))
                        #url1=domdiv.xpath('./div['+str(t)+']/div['+str(s)+']/div[2]/a')[0].get('href')[3:]
                        text1=domdiv.xpath('./div['+str(t)+']/div['+str(s)+']/div[2]/a')[0].text
                        #print (url1)
                        #print (text1)
                        map_dict[type].append(text1)
        return map_dict



first_word=u'生物医药'
payload = {'wd': first_word}
word_dict=dict()

word_dict[first_word]=search(payload)

for key,value in word_dict[first_word].items():
    for i in range(len(value)):
        payload={'wd':value[i].encode('utf-8')}
        word_dict[value[i]]=search(payload)
        # for key1,value1 in word_dict[value[i]].items():
        #     for t in range(len(value1)):
        #         payload={'wd':value1[t]}
        #         word_dict[value1[t]]=search(payload)
#createPlot(word_dict)
print (word_dict)

jsObj = json.dumps(word_dict,ensure_ascii=False)

fileObject = open('jsonFile_baidu.json', 'w')
fileObject.write(jsObj)
fileObject.close()
