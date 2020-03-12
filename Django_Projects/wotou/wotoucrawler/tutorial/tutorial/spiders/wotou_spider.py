#coding=utf-8
from scrapy.spider import Spider
from scrapy.http import Request
from scrapy.selector import Selector
import json
import time

from tutorial.items import wotouItem


keys = '北京智诚汇志投资有限公司'
class wotouSpider(Spider):
    name = "wotou"
    handle_httpstatus_list = [403]
    #减缓爬取，延迟1s
    download_delay = 1

    #allowed_domains = []
    start_urls = [
        "http://www.qichacha.com/search?key=" + keys,
        "http://www.tianyancha.com/search/" + keys,
        "http://www.qiduowei.com/search?key=" + keys,
        "http://www.xizhi.com/search?wd=" + keys,
        "http://www.qixin.com/search?key=" + keys
    ]

    def parse(self, response):  #提取搜索结果里的公司链接
        url = response.url.split("/")
        filename = url[2].split(".")[1] + '-' + keys
        newUrls = Selector(response).xpath('//span[@class="tp2_tit clear"]/a/@href').extract()
        newUrls = ['https://' + url[2] + newUrl for newUrl in newUrls]
        if newUrls != []:
            for newUrl in newUrls:
                print(newUrl)
                yield Request(newUrl, callback=self.parseCompanyPage)
        with open(filename, 'wb') as f:
            f.write(response.body)

    def parseCompanyPage(self, response): #提取单个公司主页的信息
        print(response.url)
        item = wotouItem()
        item['companyName'] = Selector(response).xpath('//span[@class = "text-big font-bold"]/text()').extract()[0]
        item['phoneNumber'] = Selector(response).xpath('//span[@class="clear text-ellipsis m-t-xs text-md text-black"]/text()').extract()
        item['emailAddress'] = Selector(response).xpath('//i[@class = "fa fa-envelope-o m-l"]/a/herf').extract()
        item['locate'] = Selector(response).xpath('//span[@class = "clear m-t-xs text-md text-black"]/text()').extract()
        yield item

