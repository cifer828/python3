# -*- coding: utf-8 -*-
import scrapy, xlwt
from easystaging.items import XizhiItem
import time, os


class XizhiSpider(scrapy.Spider):
    name = "xizhi"
    allowed_domains = ["xizhi.com"]
    needCt = 0
    realGetCt = 0
    delayTime = 1
    key = ''
    connector = ''   #数据库连接接口
    start_urls = (
        "http://www.xizhi.com/search?wd=" + key,
    )

    def parse(self, response):
        file = open("input.txt", 'r')
        keys = file.readlines()
        file.close()
        for key in keys:
            print key
            url = 'http://www.xizhi.com/search?wd=' +key + '&type=holder'
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
        candidates = response.xpath('//div[@class="infor-col2"]//h3//a/@href').extract()
        for candidate in candidates:
            self.needCt += 1
            time.sleep(self.delayTime)
            yield scrapy.Request(candidate, callback=self.parse_candidate)

    def parse_candidate(self, response):
        try:
            item = XizhiItem()
            id = u'注册号：'
            registerId = response.xpath('//div[@class="company-content clearfix"]//table[@class="shareholder-table"]//tbody//tr[1]//td[4]//span/text()').extract()
            item['registerId'] = '' if registerId == [] else registerId[0]
            companyName = response.xpath('//div[@class="top-info"]//h2//a/text()').extract()
            item['companyName'] = '' if companyName == [] else companyName[0].strip(u'\n ')
            legalPersonName = response.xpath('//div[@class="company-content clearfix"]//table[@class="shareholder-table"]//tbody//tr[4]//td[2]/text()').extract()
            item['legalPersonName'] = '' if legalPersonName == [] else legalPersonName[0].strip(u'\n  ')
            registerTime = response.xpath('//div[@class="company-content clearfix"]//table[@class="shareholder-table"]//tbody//tr[4]//td[4]/text()').extract()
            item['registerTime'] = '' if registerTime == [] else registerTime[0]
            registerMoney = response.xpath('//div[@class="company-content clearfix"]//table[@class="shareholder-table"]//tbody//tr[5]//td[2]/text()').extract()
            item['registerMoney'] = '' if registerMoney == [] else registerMoney[0].strip(u' ')
            item['businessType'] = ''
            companyType = response.xpath('//div[@class="company-content clearfix"]//table[@class="shareholder-table"]//tbody//tr[3]//td[2]/text()').extract()
            item['companyType'] = '' if companyType == [] else companyType[0].strip(u' ')
            businessScope = response.xpath('//div[@class="company-content clearfix"]//table[@class="shareholder-table"]//tbody//tr[9]//td[2]/text()').extract()
            item['businessScope'] = '' if businessScope == [] else businessScope[0].strip(u'\n  ')
            locate = response.xpath('//div[@class="company-content clearfix"]//table[@class="shareholder-table"]//tbody//tr[8]//td[2]/text()').extract()
            item['locate'] = '' if locate ==[] else locate[0].strip(u' ')
            item['phoneNumber'] = ''
            item['emailAddress'] = ''
            webLink = response.xpath('//div[@class="company-content clearfix"]//table[@class="shareholder-table"]//tbody//tr[6]//td[3]//span/text()').extract()
            item['webLinks'] = '' if webLink == [] else webLink[0]
            hold = u'股东信息'
            shareHolderInfo = response.xpath('//table[thead[tr[th[1][text()="%s"]]]]//tbody//tr' %(hold)).extract()
            item['shareHolderInfo'] = '' #if shareHolderInfo == [] else shareHolderInfo
            item['opreateCondition'] = ''
            item['investment'] = ''
            yield item
            self.realGetCt += 1
        except IndexError as e:
            self.logger.info(self.name + '解析错误')
            os.abort()
            print self.name + '解析错误'

