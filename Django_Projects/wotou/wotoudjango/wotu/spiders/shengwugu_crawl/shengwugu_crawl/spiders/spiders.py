# -*- coding: utf-8 -*-
import scrapy

import math
import re
import datetime

import os,sys

from .items import ShengwuguCrawlItem
from wotu.lib.db_connection import *



class shengwuguSpider(scrapy.Spider):
    name = "bioon"
    allowed_domains = ["www.bioon.com","news.bioon.com"]
    needCt = 0
    realGetCt = 0
    connector = ''  #数据库连接接口
    start_urls = [
        'http://www.bioon.com'
    ]

    db = mongodb_connection('news')
    types = [u'肿瘤免疫治疗',u'疫苗',u'CAR-T/TCR-T细胞治疗',u'新药',u'生物仿制药',u'罕见病和孤儿药',u'单抗药物',u'生物反应器',u'癌症研究',
             u'代谢组学',u'生物信息学',u'神经科学',u'基因治疗',u'炎症与疾病',u'生物标志物',u'肿瘤免疫治疗',
             u'微环境',u'细胞治疗',u'微生物组',u'临床研究',u'干细胞&iPS',u'组学',u'糖尿病',u'免疫学',u'肿瘤转化医学',u'高分辨率成像']
    #location:该类别对应的网页上的位置
    #tableId
    #tableName
    #title:对应类别中文转换成字符序列
    #bcId
    #item:每个类别所需要创建的不同的item
    #itemdict：每个item所需要爬取的字段，每个字段对应有两个数，第一个数是所在行数，第二个数是标示是否有超链接

    def modify_time(self,og_time):
        time_list = og_time.split('-')
        new_time = time_list[0] + '-'
        if len(time_list[1]) == 1:
            new_time += ('0' + time_list[1] + '-')
        else:
            new_time += (time_list[1] + '-')
        if len(time_list[2]) == 1:
            new_time += ('0' + time_list[2])
        else:
            new_time += (time_list[2])
        return new_time

    def parse(self, response):
        li_len=len(response.xpath('//div[@class="index_left_menu"]/ul/li'))
        for i in range(2,li_len+1):
            p_len=len(response.xpath('//div[@class="index_left_menu"]/ul/li['+str(i)+']/p/a'))
            for j in range(3,p_len+1):
                url=''.join(response.xpath('//div[@class="index_left_menu"]/ul/li['+str(i)+']/p/a['+str(j)+']/@href').extract())
                type=''.join(response.xpath('//div[@class="index_left_menu"]/ul/li['+str(i)+']/p/a['+str(j)+']/text()').extract())
                if type in self.types:
                    print(1)
                    print((url, type))
                    yield scrapy.Request(url,meta={'type':type},callback=self.parse2)

    def parse2(self,response):
        art_len=len(response.xpath('//ul[@id="cms_list"]/li'))
        type = response.meta['type']
        end_time = datetime.datetime.now()
        start_time = end_time + datetime.timedelta(days=-30)
        end_day = self.modify_time('-'.join([str(end_time.year), str(end_time.month), str(end_time.day)]))
        start_day = self.modify_time('-'.join([str(start_time.year), str(start_time.month), str(start_time.day)]))
        for i in range(1,art_len+1):
            art_name=''.join(response.xpath('//ul[@id="cms_list"]/li['+str(i)+']/div[2]/h4/a/text()').extract())
            try:
                art_time = self.modify_time(''.join(response.xpath('//ul[@id="cms_list"]/li[' + str(i) + ']/div[2]/div[1]/text()').extract()))
            except:
                art_time= end_day
            art_url='http://news.bioon.com'+''.join(response.xpath('//ul[@id="cms_list"]/li['+str(i)+']/div[2]/h4/a/@href').extract())

            count = self.db.shengwugu.find({"url":art_url}).count()
            if art_time>start_day and count==0:
                #print (art_url)
                yield scrapy.Request(art_url,meta={'type':type,'art_name':art_name,'art_url':art_url,'art_time':art_time},callback=self.parse3)


    def parse3(self,response):
        item = ShengwuguCrawlItem()
        item['type'] = response.meta['type']
        item['name'] = response.meta['art_name']
        item['url'] = response.meta['art_url']
        pattern = re.compile('.*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2})')
        print (response.xpath('//div[@class="title5"]/p/text()').extract_first())
        match = pattern.search(response.xpath('//div[@class="title5"]/p/text()').extract_first())
        if match:
            item['time'] = match.group(1)
        else:
            item['time'] = ''

        print(item['time'])

        text = ''.join(response.xpath('//div[@class="text3"]').extract())
        end_time = datetime.datetime.now()
        end_day = self.modify_time('-'.join([str(end_time.year), str(end_time.month), str(end_time.day)]))
        item['spidertime']=end_day
        dr = re.compile(r'<[^>]+>', re.S)
        text = dr.sub('', text)
        text = text.strip()
        item['content'] = text
        yield item
