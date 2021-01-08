# -*- coding: utf-8 -*-
import scrapy
import re
import time
import json
from ..items import SimuItem
import time

class SimuSpider(scrapy.Spider):
    name =  "simu"
    allowed_domains = ["gs.amac.org.cn"]
    start_urls = [
        'http://gs.amac.org.cn/amac-infodisc/res/pof/fund/index.html'
    ]
    headers = {
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36',
            'content-type': "application/json",
        }

    def parse(self, response):
        urls = "http://gs.amac.org.cn/amac-infodisc/api/pof/fund?rand=0.78840034244678&page=0&size=100"
        yield scrapy.Request(url=urls, method='POST', headers=self.headers, body="{}",callback=self.parseTotalPages)

    def parseTotalPages(self,response):
        result = json.loads(response.body)
        # print '1111111111111111111111111111111111111111'
        totalPages = result['totalPages']
        for i in range(0, totalPages):
            time.sleep(1)
            urls = "http://gs.amac.org.cn/amac-infodisc/api/pof/fund?rand=0.9741398425548233&page=" + str(i) + "&size=100"
            yield scrapy.Request(url=urls, method='POST', headers=self.headers, body="{}", callback=self.parseFund)

    def parseFund(self, response):
        results = json.loads(response.body)['content']
        for result in results:
            item = SimuItem()
            item['id'] = result['id']
            item['fundName'] = result['fundName']
            if u'有限公司' not in item['fundName'] and u'有限合伙' not in item['fundName'] :
                 continue
            item['fundNo'] = result['fundNo']
            item['managerName'] = result['managerName']
            item['managerType'] = result['managerType']
            item['workingState'] = result['workingState']
            item['putOnRecordDate'] = self.time_stamp(result['putOnRecordDate'])
            item['lastQuarterUpdate'] =  1 if result['lastQuarterUpdate'] == 'true' else 0
            item['isDeputeManage'] = result['isDeputeManage']
            item['url'] = 'http://gs.amac.org.cn/amac-infodisc/res/pof/fund/' + result['url']
            item['establishDate'] = self.time_stamp(result['establishDate'])
            item['managerUrl'] = 'http://gs.amac.org.cn/amac-infodisc/res/pof' + result['managerUrl'][2: ]
            yield item

    def time_stamp(self, time_string):
        t = time.localtime(int(time_string) / 1000)
        return time.strftime('%Y-%m-%d',t)


