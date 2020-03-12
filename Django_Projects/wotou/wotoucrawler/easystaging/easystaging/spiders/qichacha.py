# -*- coding: utf-8 -*-
import scrapy, xlwt
from easystaging.items import QichachaItem
import time

class QichachaSpider(scrapy.Spider):
    name = "qichacha"
    allowed_domains = ["qichacha.com"]
    needCt = 0
    realGetCt = 0
    delayTime = 1
    key = ''
    connector = ''   #数据库连接接口
    start_urls = (
        'http://www.qichacha.com/search?key='+key,
    )
    def parse(self, response):
        file = open("input.txt", 'r')
        keys = file.readlines()
        file.close()
        for key in keys:
            print key
            url = 'http://www.qiduowei.com/search?key='+key + '&index=3'
            #region 新建excel保存对应相关公司信息
            workBook = xlwt.Workbook(encoding='utf-8')
            workSheet = workBook.add_sheet('My Worksheet')
            workSheet.write(0, 0, label='公司名')
            workSheet.write(0, 1, label='联系方式')
            workSheet.write(0, 2, label='注册编号')
            workSheet.write(0, 3, label='联系邮箱')
            workSheet.write(0, 4, label='网站链接')
            workSheet.write(0, 5, label='公司地址')
            workSheet.write(0, 6, label='经营状况')
            workSheet.write(0, 7, label='公司类别')
            workSheet.write(0, 8, label='注册时间')
            workSheet.write(0, 9, label='法定代表')
            workSheet.write(0, 10, label='注册资本')
            workSheet.write(0, 11, label='所属行业')
            workSheet.write(0, 12, label='经营范围')
            workSheet.write(0, 13, label='股东信息')
            workSheet.write(0, 14, label='对外投资情况')
            workSheet.write(0, 15, label='搜索关键字')
            workBook.save(self.name + '.xls')
            #endregion
            yield scrapy.Request(url, callback=self.parseStartUrl, meta={'key': key})

    def parseStartUrl(self, response):
        url = response.url.split("/")
        key = response.meta['key']
        candidates = response.xpath('//span[@class="tp2_tit clear"]/a/@href').extract()
        candidates = ['https://' + url[2] + newUrl for newUrl in candidates]
        for candidate in candidates:
            time.sleep(self.delayTime)
            self.needCt += 1
            yield scrapy.Request(candidate, callback=self.parse_candidate,  meta={'key': key})

    def parse_candidate(self, response):
        try:
            item = QichachaItem()
            id = u'注册号：  '
            registerId = response.xpath('//ul[@class = "company-base"]/li[label[text()="%s"]]/text()' %(id)).extract()
            item['registerId'] = '' if registerId == [] else registerId[0]
            companyName = response.xpath('//span[@class = "text-big font-bold"]/text()').extract()
            item['companyName'] = '' if companyName == [] else companyName[0]
            legalPerson = u'法定代表：'
            legelPersonName = response.xpath('//ul[@class = "company-base"]/li[label[text()="%s"]]//a/text()' %(legalPerson)).extract()
            item['legalPersonName'] = '' if legelPersonName == [] else legelPersonName[0]
            rtime = u'成立日期：'
            registerTime = response.xpath('//ul[@class = "company-base"]//li[label[text()="%s"]]/text()' %(rtime)).extract()
            item['registerTime'] = '' if registerTime == [] else registerTime[0]
            rmoney = u'注册资本：'
            registerMoney = response.xpath('/ul[@class = "company-base"]//li[label[text()="%s"]]/text()' %(rmoney)).extract()
            item['registerMoney'] = '' if registerMoney == []else registerMoney[0]
            item['businessType'] = ''
            ctype = u'公司类型：'
            companyType = response.xpath('//ul[@class = "company-base"]//li[label[text()="%s"]]/text()' %(ctype)).extract()
            item['companyType'] = '' if companyType else companyType[0]
            scope = u'经营范围：'
            businessScope = response.xpath('//ul[@class = "company-base"]//li[label[text()="%s"]]/text()' %(scope)).extract()
            item['businessScope'] = '' if businessScope == [] else businessScope[1].strip('\n   ')
            address = u'企业地址： '
            locate = response.xpath('//ul[@class = "company-base"]//li[label[text()="%s"]]/text()' %(address)).extract()
            item['locate'] = '' if locate else locate[1]
            phoneNumber = response.xpath('//small[@class = "clear text-ellipsis m-t-xs text-md text-black"]/text()').extract()
            item['phoneNumber'] = '' if phoneNumber == [] else phoneNumber[1]
            emailAddress = response.xpath('//small[@class = "clear text-ellipsis m-t-xs text-md text-black"]//a[1]/text()').extract()
            item['emailAddress'] = '' if emailAddress == [] else emailAddress[0]
            weblinks = response.xpath('//small[@class = "clear text-ellipsis m-t-xs text-md text-black"]//a[2]/text()').extract()
            item['weblinks'] = '' if weblinks else weblinks[0]
            item['key'] = unicode(response.meta['key'], 'utf-8')
            yield item
            self.realGetCt += 1
        except IndexError as e:
            self.logger.info(self.name + '解析错误')
            print self.name + '解析错误'
