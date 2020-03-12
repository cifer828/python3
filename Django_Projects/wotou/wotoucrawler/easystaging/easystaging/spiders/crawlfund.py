# -*- coding: utf-8 -*-
import scrapy
import re

import time
from easystaging.items import FundItem

class CrawlfundSpider(scrapy.Spider):
    name = "crawlfund"
    needCt = 0
    realGetCt = 0
    delayTime = 1
    connector = ''   #数据库连接接口
    allowed_domains = ["gs.amac.org.cn"]
    start_urls = [
        'http://gs.amac.org.cn/amac-infodisc/res/pof/fund/index.html'
    ]
    headers = {
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
            'content-type': "application/json",
            'cache-control': "no-cache",
            'postman-token': "a5a8f573-f9c8-07bc-770d-b077a0b86670"
        }
    def parse(self, response):
        urls = "http://gs.amac.org.cn/amac-infodisc/api/pof/fund?rand=0.9741398425548233&page=10000&size=100"
        return scrapy.Request(url=urls, method='POST', headers=self.headers, body="{}",callback=self.parseTotalPages)
    def parseTotalPages(self,response):
        true = True
        false = False
        null = ""
        result = eval(response.body)
        totalPages = result['totalPages']
        print totalPages
        for i in range(0, totalPages):
            time.sleep(self.delayTime)
            urls = "http://gs.amac.org.cn/amac-infodisc/api/pof/fund?rand=0.9741398425548233&page=" + str(i) + "&size=100"
            yield scrapy.Request(url=urls, method='POST', headers=self.headers, body="{}", callback=self.parseFund)

    def parseFund(self, response):
        true = True
        false = False
        null = ""
        result = eval(response.body)
        numberOfFundName = result['numberOfElements']
        pattern = re.compile(r'\S+(有限公司|有限合伙)\S*')
        for i in range(0, numberOfFundName):
            fundName = result['content'][i]['fundName']
            matchResult = pattern.match(fundName)
            if matchResult:
                self.needCt += 1
                #print matchResult.group()
                #self.fundName.append(matchResult.group())
                urls = 'http://gs.amac.org.cn/amac-infodisc/res/pof/fund/' + result['content'][i]['managerUrl']
                yield scrapy.Request(url=urls, callback=self.parseOneFund, headers=self.headers,
                                     meta={'fundName': result['content'][i]['fundName'],
                                           'fundId': result['content'][i]['id']},
                                     dont_filter=True)


    def parseOneFund(self, response):
        item = FundItem()
        item['fundId'] = response.meta['fundId']
        item['fundName'] = unicode(response.meta['fundName'],'utf-8')
        item['managerName'] = response.xpath('//table[@class = "table table-center table-info"]//tbody//tr[3]//td[2]//div[1]/text()').extract()[0]
        item['registerId'] = response.xpath('//table[@class = "table table-center table-info"]//tbody//tr[5]//td[2][@class="td-content"]/text()').extract()[0]
        item['officeLocate'] = response.xpath('//table[@class = "table table-center table-info"]//tbody//tr[9]//td[2][@class="td-content"]/text()').extract()[0]
        item['registerMoney'] = response.xpath('//table[@class = "table table-center table-info"]//tbody//tr[10]//td[2][@class="td-content"]/text()').extract()[0]
        item['realRegisterMoney'] = response.xpath('//table[@class = "table table-center table-info"]//tbody//tr[10]//td[4][@class="td-content"]/text()').extract()[0]
        item['establishTime'] = response.xpath('//table[@class = "table table-center table-info"]//tbody//tr[7]//td[4][@class="td-content"]/text()').extract()[0].strip(u'\r\n ')
        item['manageFundType'] = response.xpath('//table[@class = "table table-center table-info"]//tbody//tr[12]//td[2][@class="td-content"]/text()').extract()[0]
        webLink = response.xpath('//table[@class = "table table-center table-info"]//tbody//tr[13]//td[4][@class="td-content"]//a/text()').extract()
        item['webLink'] = '' if webLink == [] else webLink[0]
        specialMg = response.xpath('//table[@class = "table table-center table-info"]//tbody//tr[26]//td[2][@class="td-content"]/text()').extract()
        item['specialMessage'] = '' if specialMg == [] else specialMg[0].strip(u'\r\n ')
        item['crawlTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        yield item
        self.realGetCt += 1


