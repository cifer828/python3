# -*- coding: utf-8 -*-
import scrapy, jieba, jieba.analyse, nltk
import MySQLdb
import xlwt, xlrd
#from xlutils.copy import copy
import time
#from easystaging.items import BaiTengItem
from searchreport.items import SearchreportItem
class BaiTengSpider(scrapy.Spider):
    name = "sina"
    allowed_domains = ["vip.stock.finance.sina.com.cn",'finance.sina.com.cn']
    needCt = 0
    realGetCt = 0
    connector = ''  #数据库连接接口
    start_urls = [
        'http://vip.stock.finance.sina.com.cn/q/go.php/vReport_List/kind/lastest/index.phtml'
    ]
    conn = MySQLdb.connect(host='localhost', user='root', passwd='0845', port=3306, charset='utf8')
    cur = conn.cursor()
    conn.select_db('searchreport')
    #cur.execute('select id,visittime from modify_scenes_v1')
    def parse(self, response):
        for i in range(1,100):
            url='http://vip.stock.finance.sina.com.cn/q/go.php/vReport_List/kind/industry/index.phtml?p='+str(i)
            yield scrapy.Request(url,callback=self.parse2)


    def parse2(self,response):
        item=SearchreportItem()
        articlelen=len(response.xpath('//div[@class="main"]/table[1]/tr'))
        print articlelen
        #print articlelen
        for i in range(3,articlelen+1):
            print i
            item['artname']=''.join(response.xpath('//div[@class="main"]/table[1]/tr['+str(i)+']/td[2]/a/text()').extract()).strip()
            item['arturl']=''.join(response.xpath('//div[@class="main"]/table[1]/tr['+str(i)+']/td[2]/a/@href').extract())
            item['arttype']=''.join(response.xpath('//div[@class="main"]/table[1]/tr['+str(i)+']/td[3]/text()').extract())
            item['artdate']= ''.join(response.xpath('//div[@class="main"]/table[1]/tr[' + str(i) + ']/td[4]/text()').extract())
            item['artcompany'] = ''.join(response.xpath('//div[@class="main"]/table[1]/tr[' + str(i) + ']/td[5]/a/div/span/text()').extract())
            item['searchpeople'] = ''.join(response.xpath('//div[@class="main"]/table[1]/tr[' + str(i) + ']/td[6]/div/span/text()').extract())
            #print arturl
            #print [artname,arturl,arttype,artdate,artcompany,searchpeople]
            count=self.cur.execute('select * from sina where arturl="'+item['arturl']+'"')
            if count==0:
                yield scrapy.Request(item['arturl'],callback=self.parse3,meta={'item':item})

    def parse3(self,response):
        #articlecontent=1
        item=response.meta['item']
        item['content']=''.join(response.xpath('//div[@class="blk_container"]/p/text()').extract())
        yield item














