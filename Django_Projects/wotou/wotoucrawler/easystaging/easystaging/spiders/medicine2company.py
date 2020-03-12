# -*- coding: utf-8 -*-
import scrapy, psycopg2
from psycopg2 import errorcodes
import xlwt
import time, os
from easystaging.items import YaoZhiGuoChanItem, YaoZhiJinKouItem, YaoZhiZhuCeItem, YaoZhiLinChuangItem, YaoZhiGuoWaiXinYaoItem

class Medicine2CompanySpider(scrapy.Spider):
    name = 'medicine2company'
    allowed_domains = ["db.yaozh.com"]
    delayTime = 2
    needCt = 0
    realGetCt = 0
    connector = ''   #数据库连接接口
    start_urls = [
        'http://db.yaozh.com'
    ]
    def parse(self, response):
        f = open('yaozhi_input.txt', 'r')
        keys = f.readlines()
        f.close()
        f = open('input.txt', 'wb')
        f.close()
        for key in keys:
            print key
            time.sleep(self.delayTime)
            url = 'http://db.yaozh.com/Search?content=' + key
            yield scrapy.Request(url, callback=self.parseAllUrl)

    def parseAllUrl(self, response):
        dbName = [u'药品注册与受理数据库', u'国产药品数据库', u'进口药品数据库', u'国外新药及新剂型数据库']
        urls = []
        for name in dbName:
            try:
                url = response.xpath('//a[span[text()="%s"]]/@href' %(name)).extract()
                ct = response.xpath('//a[span[text()="%s"]]//span//em/text()' %(name)).extract()
            except IndexError as e:
                self.logger.info(self.name + '解析错误,关闭爬虫')
                print self.name + '解析错误,关闭爬虫'
            if url!=[]:
                urls.append(['http://db.yaozh.com' + url[0], ct[0]])
        for url in urls:
            pageCt = int(url[1])/30 + 1
            pageCt = 10 if pageCt > 10 else pageCt
            self.needCt += int(url[1])
            for i in range(1, pageCt + 1):
                time.sleep(self.delayTime)
                href = url[0] + '&p=' + str(i) + '&pageSize=30'
                #print href
                yield scrapy.Request(href, callback=self.parseCompanyName)

    def parseCompanyName(self, response):
        print response.url
        f = open('input.txt', 'a+')
        urlSplit = response.url.split('/')
        for i in range(1, 31):
            try:
                crawlTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                if u'zhuce' in urlSplit[len(urlSplit)-1]:
                    companyName = response.xpath('//tbody//tr[%s]//td[6]//a/text()' %(str(i))).extract()
                    companyName = '' if companyName == [] else companyName[0].strip(u'\n\t- ')
                elif u'pijian' in urlSplit[len(urlSplit)-1]:
                    companyName = response.xpath('//tbody//tr[%s]//td[3]/text()' %(str(i))).extract()
                    companyName = '' if companyName == [] else companyName[0].strip(u'\n\t- ')
                else:
                    companyName = ''
                if companyName != '':
                    f.write(companyName.encode('utf-8'))
                    f.write('\n')
                    cursor = self.connector.cursor()
                    try:
                        para = {
                            'time':  crawlTime,
                            'content':  companyName
                        }
                        cursor.execute(
                            'select count(*) from jobqueue where job_content =%(content)s;',
                            para
                        )
                        result = cursor.fetchall()
                        if int(result[0][0]) == 0:
                            cursor.execute(
                                'INSERT INTO jobqueue(job_push_time, job_content)'
                                'VALUES(%(time)s,%(content)s);',
                                para
                            )
                            self.connector.commit()
                            self.realGetCt += 1
                            print 'add a job to database successfully!'
                            self.logger.info('add a job to database successfully!')
                    except psycopg2.errorcodes as e:
                        self.logger.info(format(errorcodes.lookup(e.pgcode)))
                        self.connector.commit()
                        self.logger.info('failed to add a job to database ')
            except IndexError as e:
                self.logger.info(self.name + '解析错误,关闭爬虫')
                print self.name + '解析错误,关闭爬虫'
        f.close()
        print self.needCt, self.realGetCt