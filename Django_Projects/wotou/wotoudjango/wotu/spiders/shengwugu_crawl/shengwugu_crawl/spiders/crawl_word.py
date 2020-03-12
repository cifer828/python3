# # -*- coding: utf-8 -*-
# import lxml.html
# import requests
#
#
# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'}
#
#
#
# r=requests.get('http://www.bioon.com',headers=headers,timeout=5)
# print (r.url)
# dom=lxml.html.document_fromstring(r.content)
#
# table=dom.xpath('//div[@class="index_left_menu"]')[0]
# li_len=len(table.xpath('./ul/li'))
#
# print (li_len)
# wordlist=[]
# for i in range(2,li_len+1):
#     p_len=len(table.xpath('./ul/li['+str(i)+']/p/a'))
#     for j in range(1,p_len+1):
#         text=table.xpath('./ul/li[' + str(i) + ']/p/a['+str(j)+']')[0].text
#         sub_url=table.xpath('./ul/li[' + str(i) + ']/p/a['+str(j)+']')[0].get('href')
#
#         print (sub_url)
#         wordlist.append(text)
#
#
# for word in wordlist:
#     print (word)