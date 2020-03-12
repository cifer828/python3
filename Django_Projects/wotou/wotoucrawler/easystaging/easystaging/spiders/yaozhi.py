# -*- coding: utf-8 -*-
import scrapy
import xlwt
import time, os
from easystaging.items import YaoZhiGuoChanItem, YaoZhiJinKouItem, YaoZhiZhuCeItem, YaoZhiLinChuangItem, YaoZhiGuoWaiXinYaoItem

class YaozhiSpider(scrapy.Spider):
    name = "yaozhi"
    allowed_domains = ["db.yaozh.com"]
    delayTime = 4
    needCt = 0
    connector = ''   #数据库连接接口
    realGetCt = 0
    start_urls = [
        'http://db.yaozh.com/guowaixinyao',
        'http://db.yaozh.com/jinkou',
        'http://db.yaozh.com/linchuangshiyan',
        'http://db.yaozh.com/pijian',
        'http://db.yaozh.com/zhuce?me_banlizhuangtai=待审批',
        'http://db.yaozh.com/zhuce?me_banlizhuangtai=待审评',
        'http://db.yaozh.com/zhuce?me_banlizhuangtai=在审评',
        'http://db.yaozh.com/zhuce?me_banlizhuangtai=在审批',
        'http://db.yaozh.com/zhuce?me_banlizhuangtai=审批完毕',
        'http://db.yaozh.com/zhuce?me_banlizhuangtai=制证完毕',
        'http://db.yaozh.com/zhuce?me_banlizhuangtai=制证结束',
        'http://db.yaozh.com/zhuce?me_banlizhuangtai=已发件',
    ]
    def parse(self, response):
        totalCt = response.xpath('//div[@class="tr offset-top"]/@data-total').extract()
        totalCt = 0 if totalCt == [] else int(totalCt[0])
        self.needCt += totalCt
        totalpages = totalCt/30 + 1
        totalpages = 10 if totalpages > 10 else totalpages
        list = response.url.split('/')
        databaseName = list[len(list)-1]
        urls = []
        if databaseName == 'pijian':
            print databaseName, totalCt, totalpages
            #region 新建excel保存对应信息
            workBook = xlwt.Workbook(encoding='utf-8')
            workSheet = workBook.add_sheet('My Worksheet')
            workSheet.write(0, 0, label='药物名称')
            workSheet.write(0, 1, label='英文名称')
            workSheet.write(0, 2, label='药品规格')
            workSheet.write(0, 3, label='生产单位')
            workSheet.write(0, 4, label='批准文号')
            workSheet.write(0, 5, label='批准日期')
            workSheet.write(0, 6, label='产品类别')
            workSheet.write(0, 7, label='剂型')
            workBook.save(self.name + '-国产药品.xls')
            #endregion
            for i in range(1, totalCt + 1):
                time.sleep(self.delayTime)
                url = 'http://db.yaozh.com/pijian/' + str(i) + '.html'
                yield scrapy.Request(url, callback=self.parsePijianMedicine)
        elif 'zhuce' in databaseName:
            print databaseName, totalCt, totalpages
            #region 新建excel保存对应信息
            workBook = xlwt.Workbook(encoding='utf-8')
            workSheet = workBook.add_sheet('My Worksheet')
            workSheet.write(0, 0, label='药物名称')
            workSheet.write(0, 1, label='注册分类')
            workSheet.write(0, 2, label='申请类型')
            workSheet.write(0, 3, label='企业名称')
            workSheet.write(0, 4, label='办理状态')
            workSheet.write(0, 5, label='状态开始日')
            workSheet.write(0, 6, label='审评结论')
            workBook.save(self.name + '-药品注册.xls')
            #endregion
            for i in range(1, totalpages + 1):
                time.sleep(self.delayTime)
                url = response.url + '&p=' + str(i) + '&pageSize=30'
                yield scrapy.Request(url, callback=self.parseZhuCeData)
        elif databaseName == 'linchuangshiyan':
            print databaseName, totalCt, totalpages
            #region 新建excel保存对应信息
            workBook = xlwt.Workbook(encoding='utf-8')
            workSheet = workBook.add_sheet('My Worksheet')
            workSheet.write(0, 0, label='实验题目')
            workSheet.write(0, 1, label='适应症')
            workSheet.write(0, 2, label='试验状态')
            workSheet.write(0, 3, label='实验分期')
            workSheet.write(0, 4, label='登记时间')
            workBook.save(self.name + '-临床试验.xls')
            #endregion
            for i in range(1, totalpages+1):
                time.sleep(self.delayTime)
                url = 'http://db.yaozh.com/linchuangshiyan?p=' + str(i) + '&pageSize=30'
                yield scrapy.Request(url, callback=self.parseExperiment)
        elif databaseName == 'jinkou':
            print databaseName, totalCt, totalpages
            #region 新建excel保存对应信息
            workBook = xlwt.Workbook(encoding='utf-8')
            workSheet = workBook.add_sheet('My Worksheet')
            workSheet.write(0, 0, label='药品名称')
            workSheet.write(0, 1, label='公司名称')
            workSheet.write(0, 2, label='发证日期')
            workBook.save(self.name + '-进口药品.xls')
            #endregion
            for i in range(1, totalCt + 1):
                time.sleep(self.delayTime)
                url = 'http://db.yaozh.com/jinkou/' + str(i) + '.html'
                yield scrapy.Request(url, callback=self.parseJinkouMedicine)
        elif databaseName == 'guowaixinyao':
            print databaseName, totalCt, totalpages
            allUrl = []
            #region 新建excel保存对应信息
            workBook = xlwt.Workbook(encoding='utf-8')
            workSheet = workBook.add_sheet('My Worksheet')
            workSheet.write(0, 0, label='药品名称')
            workSheet.write(0, 1, label='类型')
            workSheet.write(0, 2, label='申报公司')
            workSheet.write(0, 3, label='批准国家')
            workSheet.write(0, 4, label='批准日期')
            workSheet.write(0, 5, label='药品作用')
            workSheet.write(0, 6, label='药品简介')
            workBook.save(self.name + '-国外新药.xls')
            #endregion
            for i in range(1, totalpages+1):
                time.sleep(self.delayTime)
                url = response.url + '?p=' + str(i) + '&pageSize=30'
                yield scrapy.Request(url, callback=self.parseNewMedicineUrl, meta={'allUrl': allUrl, 'ct': 300})
    #解析国产药品数据库
    def parsePijianMedicine(self, response):
        try:
            item = YaoZhiGuoChanItem()
            item['crawlTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            name = u'药品名称'
            item['medicineName'] = response.xpath('//tr[th[text()="%s"]]/td/text()' %(name)).extract()[0].strip(u'\r\n ')
            specife = u'规格'
            medicineSpecification = response.xpath('//tr[th[text()="%s"]]/td/text()' %(specife)).extract()
            item['medicineSpecification'] = '' if medicineSpecification == [] else medicineSpecification[0].strip(u'\r\n ')
            produce = u'生产单位'
            item['produceIndustry'] = response.xpath('//tr[th[text()="%s"]]/td/a/text()' %(produce)).extract()[0]
            number = u'批准文号'
            item['approvalNumber'] = response.xpath('//tr[th[text()="%s"]]/td/text()' %(number)).extract()[0].strip(u'\r\n ')
            time1 = u'批准日期'
            item['approvalDate'] = response.xpath('//tr[th[text()="%s"]]/td/text()' %(time1)).extract()[0].strip(u'\r\n ')
            ename = u'英文名称'
            englishName = response.xpath('//tr[th[text()="%s"]]/td/text()' %(ename)).extract()
            item['englishName'] = '' if englishName == [] else englishName[0].strip(u'\r\n ')
            type = u'产品类别'
            item['medicineType'] = response.xpath('//tr[th[text()="%s"]]/td/text()' %(type)).extract()[0].strip(u'\r\n ')
            form = u'剂型'
            item['dosageForms'] = response.xpath('//tr[th[text()="%s"]]/td/text()' %(form)).extract()[0].strip(u'\r\n ')
            item['databaseType'] = 1
            item['crawlTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item['id'] = item['approvalNumber']
            yield item
            self.realGetCt += 1
        except IndexError as e:
            self.logger.info(self.name + '解析错误,关闭爬虫')
            print self.name + '解析错误,关闭爬虫'
            os.abort()
    #解析中国临床试验数据库
    def parseExperiment(self, response):
        try:
            for i in range(1, 31):
                item = YaoZhiLinChuangItem()
                item['id'] = response.xpath('//tbody//tr[%s]//th//a/text()' %(str(i))).extract()[0].strip(u'\n\t ')
                item['expName'] = response.xpath('//tbody//tr[%s]//td[1]/text()' %(str(i))).extract()[0].strip(u'\n\t ')
                item['indication'] = response.xpath('//tbody//tr[%s]//td[2]/text()' %(str(i))).extract()[0].strip(u'\n\t ')
                item['expState'] = response.xpath('//tbody//tr[%s]//td[3]/text()' %(str(i))).extract()[0].strip(u'\n\t ')
                item['expStage'] = response.xpath('//tbody//tr[%s]//td[4]/text()' %(str(i))).extract()[0].strip(u'\n\t ')
                item['registerDate'] = response.xpath('//tbody//tr[%s]//td[5]/text()' %(str(i))).extract()[0].strip(u'\n\t ')
                item['databaseType'] = 4
                item['crawlTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                yield item
                self.realGetCt += 1
        except IndexError as e:
            self.logger.info(self.name + '解析错误,关闭爬虫')
            print self.name + '解析错误,关闭爬虫'
            os.abort()
    #解析进口药品数据库
    def parseJinkouMedicine(self, response):
        try:
            item = YaoZhiJinKouItem()
            item['databaseType'] = 2
            key = u'注册证号'
            item['id'] = response.xpath('//tr[th[text()="%s"]]//td/text()' %(key)).extract()[0].strip(u'\n ')
            name = u'药品名称（中文）'
            item['medicineName'] = response.xpath('//tr[th[text()="%s"]]//td/text()' %(name)).extract()[0].strip(u'\n ')
            cname = u'生产厂商（英文）'
            item['companyName'] = response.xpath('//tr[th[text()="%s"]]//td/text()' %(cname)).extract()[0].strip(u'\n ')
            date = u'发证日期'
            item['date'] = response.xpath('//tr[th[text()="%s"]]//td/text()' %(date)).extract()[0].strip(u'\n ')
            item['crawlTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            yield item
            self.realGetCt += 1
        except IndexError as e:
            self.logger.info(self.name + '解析错误,关闭爬虫')
            print self.name + '解析错误,关闭爬虫'
            os.abort()
    #解析国外新药及新剂型数据库
    def parseNewMedicineUrl(self, response):
        allUrl = response.meta['allUrl']
        urls = response.xpath('//tbody//tr//th//a/@href').extract()
        if urls != []:
            urls = ['http://db.yaozh.com' + url for url in urls]
        for url in urls:
            if url not in allUrl:
                allUrl.append(url)
        if len(allUrl) == response.meta['ct']:
            for url in allUrl:
                time.sleep(1)
                yield scrapy.Request(url, callback=self.parseNewMedicine)
    def parseNewMedicine(self, response):
        try:
            item = YaoZhiGuoWaiXinYaoItem()
            key = u'英文商品名'
            item['id'] = response.xpath('//tr[th[text()="%s"]]//td/text()' %(key)).extract()[0].strip(u'\n ')
            item['crawlTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item['databaseType'] = 5
            name = u'中文名称'
            item['medicineName'] = response.xpath('//tr[th[text()="%s"]]//td/text()' %(name)).extract()[0].strip(u'\n ')
            tp = u'类型'
            item['type'] = response.xpath('//tr[th[text()="%s"]]//td/text()' %(tp)).extract()[0].strip(u'\n ')
            cname = u'申报公司'
            item['companyName'] = response.xpath('//tr[th[text()="%s"]]//td/text()' %(cname)).extract()[0].strip(u'\n ')
            country = u'批准国家'
            item['approvalCountry'] = response.xpath('//tr[th[text()="%s"]]//td/text()' %(country)).extract()[0].strip(u'\n ')
            date = u'批准日期'
            item['approvalDate'] = response.xpath('//tr[th[text()="%s"]]//td/text()' %(date)).extract()[0].strip(u'\n ')
            eff = u'药品作用'
            item['effects'] = response.xpath('//tr[th[text()="%s"]]//td/text()' %(eff)).extract()[0].strip(u'\n ')
            intro = u'药品简介'
            item['introduction'] = response.xpath('//tr[th[text()="%s"]]//td/text()' %(intro)).extract()[0].strip(u'\n ')
            yield item
            self.realGetCt += 1
        except IndexError as e:
            self.logger.info(self.name + '解析错误,关闭爬虫')
            print self.name + '解析错误,关闭爬虫'
            os.abort()
#解析药品注册与受理数据库
    def parseZhuCeData(self, response):
        try:
            for i in range(1, 31):
                item = YaoZhiZhuCeItem()
                item['id'] = response.xpath('//tbody//tr[%s]//td[1]//a/text()' %(str(i))).extract()[0].strip(u'\n\t ')
                item['medicineName'] = response.xpath('//tbody//tr[%s]//td[2]//a/text()' %(str(i))).extract()[0].strip(u'\n\t ')
                item['registerType'] = response.xpath('//tbody//tr[%s]//td[3]/text()' %(str(i))).extract()[0].strip(u'\n\t ')
                item['applyType'] = response.xpath('//tbody//tr[%s]//td[4]/text()' %(str(i))).extract()[0].strip(u'\n\t ')
                item['companyName'] = response.xpath('//tbody//tr[%s]//td[6]//a/text()' %(str(i))).extract()[0].strip(u'\n\t ')
                item['processState'] = response.xpath('//tbody//tr[%s]//td[7]/text()' %(str(i))).extract()[0].strip(u'\n\t ')
                item['stateStartDate'] = response.xpath('//tbody//tr[%s]//td[8]/text()' %(str(i))).extract()[0].strip(u'\n\t ')
                item['valueResult'] = response.xpath('//tbody//tr[%s]//td[11]//a/text()' %(str(i))).extract()[0].strip(u'\n\t ')
                item['databaseType'] = 3
                item['crawlTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                yield item
                self.realGetCt += 1
        except IndexError as e:
            self.logger.info(self.name + '解析错误,关闭爬虫')
            print self.name + '解析错误,关闭爬虫'
            os.abort()

