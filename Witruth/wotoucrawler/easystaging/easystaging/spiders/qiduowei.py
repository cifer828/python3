# -*- coding: utf-8 -*-
import scrapy
from easystaging.items import QiduoweiItem
import time, xlwt


class QiduoweiSpider(scrapy.Spider):
    name = "qiduowei"
    allowed_domains = ["qiduowei.com"]
    needCt = 0
    realGetCt = 0
    delayTime = 1
    key = ''
    connector = ''   #数据库连接接口
    start_urls = (
         'http://www.qiduowei.com/search?key='+key + '&cate=3',
    )
    def parse(self, response):
        file = open("input.txt", 'r')
        keys = file.readlines()
        file.close()
        for key in keys:
            print key
            url = 'http://www.qiduowei.com/search?key='+key + '&cate=3'
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
            yield scrapy.Request(url, callback=self.parseAllUrl, meta={'key': key,'url':url})
    def parseAllUrl(self, response):
        totalCt = response.xpath('//div[@class="result-tip"]//span/text()').extract()[0]
        totalpages = int(totalCt)/10
        print totalpages
        if totalpages != 0:
            for i in range(1, totalpages+2):
                url = response.meta['url'] + '&key=' + response.meta['key'] + '&p=' + str(i)
                print url
                yield scrapy.Request(url, callback=self.parseStartUrl, meta={'key': response.meta['key']})

    def parseStartUrl(self, response):
        url = response.url.split("/")
        key = response.meta['key']
        candidates = response.xpath('//div[@class="list-item"]//a[@class="content"]/@href').extract()
        candidates = ['http://' + url[2] + newUrl for newUrl in candidates]
        for candidate in candidates:
            self.needCt += 1
            time.sleep(self.delayTime)
            yield scrapy.Request(candidate, callback=self.parse_candidate, meta={'key': key})

    def parse_candidate(self, response):
        try:
            item = QiduoweiItem()
            number = u'注册号：'
            registerId = response.xpath('//div[@class = "col-md-6 col-xl-6"][span[text()="%s"]]/text()' %(number)).extract()
            item['registerId'] = '' if registerId == [] else registerId[1].strip(u' ')
            companyName = response.xpath('//div[@class = "company-name"]//h1/text()').extract()
            item['companyName'] = '' if companyName == [] else companyName[0]
            legalPerson = u'法定代表：'
            legalPersonName = response.xpath('//div[@class = "col-md-6 col-xl-6"][span[text()="%s"]]//a/text()' %(legalPerson)).extract()
            item['legalPersonName'] = '' if legalPersonName == [] else legalPersonName[0]
            register = u'成立日期：'
            registerTime = response.xpath('//div[@class = "col-md-6 col-xl-6"][span[text()="%s"]]//a/@href' %(register)).extract()
            item['registerTime'] = '' if registerTime == [] else registerTime[0].split('=')[1]
            money = u'注册资本：'
            registerMoney = response.xpath('//div[@class = "col-md-6 col-xl-6"][span[text()="%s"]]//a/text()' %(money)).extract()
            item['registerMoney'] = '' if registerMoney == [] else registerMoney[0]
            item['businessType'] = ''
            ctype=u'公司类型：'
            companyType = response.xpath('//div[@class = "col-md-6 col-xl-6"][span[text()="%s"]]/text()' %(ctype)).extract()
            item['companyType'] = '' if companyType == [] else companyType[1]
            scope = u'经营范围 ：'
            businessScope = response.xpath('//div[@class = "col-md-12 col-xl-12"][span[text()="%s"]]//p//a/text()' %(scope)).extract()
            item['businessScope'] = u'、'.join(businessScope)
            address = u'地址：'
            locate = response.xpath('//div[@class = "col-md-12 col-xl-12"][span[text()="%s"]]/text()' %(address)).extract()
            item['locate'] = '' if locate == [] else locate[1]
            phoneNumber = response.xpath('//div[@class="contact-list"]//div[2]//span/text()').extract()
            item['phoneNumber'] = '' if phoneNumber == [] else phoneNumber
            emailAddress = response.xpath('//div[@class="contact-list"]//div[3]//a/text()').extract()
            item['emailAddress'] = '' if emailAddress == [] or emailAddress[0] == u'查看地图' else emailAddress[0]
            webLinks = response.xpath('//div[@class="contact-list"]//div//a[@class="enterprise-website"]/text()').extract()
            item['webLinks'] = '' if webLinks == [] else webLinks[0]
            opreateCondition = response.xpath('//div[@class = "company-name"]//span/text()').extract()
            item['opreateCondition'] = '' if opreateCondition == [] else opreateCondition[0]
            investCt = response.xpath('//div[@class = "content-item invest-info"]//div[@class = "title"]//span//text()').extract()
            item['shareHolderInfo'] = ''
            item['investment'] = []
            item['crawlTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item['key'] = unicode(response.meta['key'], 'utf-8')
            if investCt != []:
                investCt = int(investCt[0])
                requestTimes = investCt/3 if investCt % 3 == 0 else (investCt/3)+1
                for x in range(1, requestTimes+1):
                    url = 'http://www.qiduowei.com/index/detail/getInvestPaging'
                    formData = {
                        "p": str(x),
                        "name": item['companyName'].encode('utf-8')
                    }
                    #yield scrapy.FormRequest(url=url, formdata=formData, meta={'item': item}, callback=self.parse_invest)
            yield item
            self.realGetCt += 1
        except IndexError as e:
            self.logger.info(self.name + '解析错误')
            print self.name + '解析错误'

    def parse_invest(self, response):
        true = True
        false = False
        item =response.meta['item']
        item['investment'].append(eval(response.body)['data'])
        yield item

