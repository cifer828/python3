# -*- coding: utf-8 -*-
import scrapy
from ..items import Spider36KrItem
import json
import datetime
import re
import chardet

class s36krSpider(scrapy.Spider):
    name = "spider_36kr"
    allowed_domains = ["36kr.com"]
    start_urls = ["http://36kr.com/newsflashes"]

    def __init__(self):
        self.current_id = 0

    def parse(self, response):
        # 获取页面中第一条新闻的id
        first_piece = re.findall('newsflash":\[\{"id":"(\d+)',response.body)[0]
        self.current_id = int(first_piece) + 1
        # 根据id获取api地址
        json_base_url = "http://36kr.com/api/info-flow/newsflash_columns/newsflashes?b_id="
        json_url = json_base_url + str(self.current_id)
        yield scrapy.Request(json_url, callback=self.parse_json)

    def parse_json(self, response):
        info = json.loads(response.body)
        item = Spider36KrItem()
        for a_item in info['data']['items']:
            item['id'] = a_item['id']
            item['title'] = a_item['title'].encode('utf8')
            item['content'] = a_item['description'].encode('utf8')
            item['link'] = a_item['news_url'].encode('utf8')
            item['time'] = a_item['created_at'].encode('utf8')
            yield item
        self.current_id = int(item['id'])
        json_base_url = "http://36kr.com/api/info-flow/newsflash_columns/newsflashes?b_id="
        json_url = json_base_url + str(self.current_id)
        # 遇到过期新闻停止爬取
        if self.stop_at(item['time']):
            return
        yield scrapy.Request(json_url, callback=self.parse_json)

    def stop_at(self, date_string):
        """
        七天以内True
        七天以外False
        """
        date = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        diff = datetime.datetime.now() - date
        print(diff.days)
        return diff.days > 7



