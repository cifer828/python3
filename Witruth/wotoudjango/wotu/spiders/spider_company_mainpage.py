#coding:utf-8

import requests
import lxml.html
import re

#搜索product所在的url
def search_product_url(url):
    r=requests.get(url)
    content = r.content
    str='<a title="产品" href="/html/zhongwen/product/">产品</a>'
    pattern=re.compile(r'<a.*href=".*">.*产品.*</a>')
    result = re.findall(pattern,content)
    print(result)




if __name__ == '__main__':
    search_product_url('http://www.aheadx.com')

