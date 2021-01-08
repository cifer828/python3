# -*- coding: utf-8 -*-
import scrapy, jieba, jieba.analyse
import xlwt, xlrd
from xlutils.copy import copy
import time
from easystaging.items import BaiTengItem

class BaiTengSpider(scrapy.Spider):
    name = "baiteng"
    allowed_domains = ["so.baiten.cn"]
    needCt = 0
    realGetCt = 0
    connector = ''  #数据库连接接口
    start_urls = [
        'http://so.baiten.cn/'
    ]

    def parse(self, response):
        file = open("zhuanli_input.txt", 'r')
        keys = file.readlines()
        file.close()
        #region 新建excel保存对应相关公司信息
        workBook = xlwt.Workbook(encoding='utf-8')
        workSheet = workBook.add_sheet('My Worksheet')
        workSheet.write(0, 0, label='专利名称')
        workSheet.write(0, 1, label='申请人')
        workSheet.write(0, 2, label='专利日期')
        workSheet.write(0, 3, label='申请号')
        workSheet.write(0, 4, label='状态')
        workSheet.write(0, 5, label='摘要')
        workBook.save(self.name + '.xls')
        #endregion
        for key in keys:
            url = 'http://so.baiten.cn/results?q=' + key + '&type=9'
            yield scrapy.Request(url, callback=self.parseStartUrl, meta={'companyName': key})

    def parseStartUrl(self, response):
        patentCount = response.xpath('//span[@id = "sop-totalCount"]/text()').extract()
        patentCount = 0 if patentCount == [] else int(patentCount[0])
        allUrl = []
        if patentCount != 0:
            requestTimes = patentCount/10 + 1
            #region 相似企业excel
            workBook = xlwt.Workbook(encoding='utf-8')
            workSheet = workBook.add_sheet('My Worksheet')
            workSheet.write(0, 0, label='公司名')
            workSheet.write(0, 1, label='搜索关键字')
            workBook.save(response.meta['companyName'] + '.xls')
            #endregion
            for i in range(1, requestTimes+1):
                url = 'http://so.baiten.cn/results?q=' + response.meta['companyName'] +'&type=9&page=' + str(i)
                yield scrapy.Request(url, callback=self.parseAllUrl, meta={
                    'patentCount': patentCount,
                    'allUrl': allUrl,
                    'companyName': response.meta['companyName']
                })

    def parseAllUrl(self, response):
        allUrl = response.meta['allUrl']
        url = response.url.split("/")
        urls = response.xpath('//a[@class = "srl-detail-ti f16"]/@href').extract()
        urls = [url1.strip('\n ') for url1 in urls]
        urls = ['http://' + url[2] + newUrl for newUrl in urls]
        for url in urls:
            allUrl.append(str(url).strip('\r'))
        if len(allUrl) == response.meta['patentCount']:
            for url in allUrl:
                yield scrapy.Request(url, callback=self.parse_patent, meta={
                    'companyName': response.meta['companyName'],
                    'patentCount': response.meta['patentCount'],
                })

    def parse_patent(self, response):
        item = BaiTengItem()
        item['companyName'] = unicode(response.meta['companyName'], 'utf-8')
        patentName = response.xpath('//a[@id = "patTitle"]/text()').extract()
        item['patentName'] = '' if patentName == [] else patentName[0]
        applyPerson = response.xpath('//table[@class = "pd-d-c-g-infoTable"]//tr[3]//td[2]//a/text()').extract()
        item['applyPerson'] = '' if applyPerson == [] else applyPerson[0]
        applyId = response.xpath('//table[@class = "pd-d-c-g-infoTable"]//tr[1]//td[1]//span/text()').extract()
        item['applyId'] = '' if applyId == [] else applyId[0]
        state = response.xpath('//span[@class= "lawState f12"]/text()').extract()
        item['state'] = '' if state == [] else state[0]
        abstract = response.xpath('//div[@class= "pd-d-c-g-col fl"]//p/text()').extract()
        item['abstract'] = '' if abstract == [] else abstract[0]
        patentTime = response.xpath('//table[@class = "pd-d-c-g-infoTable"]//tr[2]//td[1]//a/text()').extract()
        item['patentTime'] = '' if patentTime == [] else patentTime[0]
        item['crawlTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        yield item
        #region split word
        searchKey=''
        print '-keys-name-'
        print '-keys-combination'
        for x in jieba.analyse.extract_tags(item['patentName']+item['abstract'], 10):
            #print x
            url = 'http://so.baiten.cn/results?q=' + x + '&type=9'
            yield scrapy.Request(url, callback=self.parseSimliarCompanyUrl, meta={
                                    'key': searchKey,
                                    'companyName': response.meta['companyName']
                                })
        #endregion


    def parseSimliarCompanyUrl(self, response):
        patentCount = response.xpath('//span[@id = "sop-totalCount"]/text()').extract()
        patentCount = 0 if patentCount == [] else int(patentCount[0])
        if patentCount != 0:
            requestTimes = patentCount/10 + 1
            for i in range(1, requestTimes+1):
                url = 'http://so.baiten.cn/results?q=' + response.meta['key'] + '&type=9&page=' + str(i)
                yield scrapy.Request(url, callback=self.parseSimliarCompany, meta={
                    'patentCount': patentCount,
                    'key': response.meta['key'],
                    'companyName': response.meta['companyName']
                })

    def parseSimliarCompany(self, response):
        companyName = response.xpath('//li[@class = "sm-c-r-color"]//span/a/text()').extract()
        companyName = list(set(companyName))
        file = xlrd.open_workbook(response.meta['companyName'] + '.xls')
        sheet = file.sheets()[0]
        nrows = sheet.nrows
        fileWrite = copy(file)
        writeSheet = fileWrite.get_sheet(0)
        for name in companyName:
            writeSheet.write(nrows, 0, name)
            writeSheet.write(nrows, 1, response.meta['key'])
        fileWrite.save(response.meta['companyName'] + '.xls')

