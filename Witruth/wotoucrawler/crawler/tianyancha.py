# -*- coding: utf-8 -*-
from selenium import webdriver
import sys, urllib
from lxml import html
import time, psycopg2, json
from psycopg2 import errorcodes
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException

user = 'ubuntu'
password = 'wotou123'
database = 'wotou'
host = 'localhost'

delayTime = 3
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap={
    "phantomjs.page.settings.userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0",
    "phantomjs.page.settings.preferer":  "http://www.tianyancha.com",
    "phantomjs.page.settings.loadImages": False,
    "phantomjs.page.settings.resourceTimeout": 5000
}
verifyUrl = 'http://antirobot.tianyancha.com/captcha/verify'


def getHtmlByKeys(key, ipList):#抓取网页html
    url = 'http://www.tianyancha.com/search/' + urllib.quote_plus(key)
    driver = webdriver.PhantomJS(desired_capabilities=dcap)
    try:
        driver.get(url)
        time.sleep(delayTime)
        if verifyUrl in driver.current_url:
            print '-------------'
            print 'start trying proxy'
            pageSource = getHtmlByProxy(url, ipList)
        else:
            pageSource = driver.page_source
        return pageSource
    except TimeoutException:
        driver.quit()
        return ''

def getHtmlByProxy(url, ipList):
    t = time.time()
    pageSource = ''
    for i in range(0, len(ipList)):
        print ipList[i]
        proxy = [
            '--proxy=%s' % (ipList[i][1]),
            '--proxy-type=%s' % (ipList[i][2])
        ]
        driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=proxy)
        try:
            driver.get(url)
            time.sleep(delayTime)
            if verifyUrl in driver.current_url or driver.title == '':
                print 'trying cross validate'
                pass
            else:
                print 'cross successfully!', driver.title
                print 'time consuming', time.time()-t
                print '-------------'
                pageSource = driver.page_source
                break
        except TimeoutException:
            pass
    if pageSource == '':
        print 'all proxy ip have been used, no one can access target, plz update ip pool!'
    return pageSource

def getHtmlByUrl(url):
    driver = webdriver.PhantomJS(desired_capabilities=dcap)
    try:
        driver.get(url)
        time.sleep(delayTime)
        if verifyUrl in driver.current_url:
            print '-------------'
            print 'start trying proxy'
            pageSource = getHtmlByProxy(url)
        else:
            pageSource = driver.page_source
        return pageSource
    except TimeoutException:
        driver.quit()
        return ''

def parseCompany(html):#提取链接
    try:
        url = html.xpath('//a[@class="query_name"]/@href')[0]
        url = 'http://www.tianyancha.com' + url
        return url
    except IndexError:
        print 'can not find url!'
        return ''

def parseCompanyInfor(pageSource):#解析页面信息
    inforDict = {}
    open('logs/1.html', 'w').write(pageSource.encode('utf-8'))
    try:
        pageSource = html.fromstring(pageSource)
        companyName = pageSource.xpath('//div[@class="company_info_text"]//p/text()')
        inforDict['companyName'] = '' if companyName == [] else companyName[0]
        n = u'电话:'
        phoneNumber = pageSource.xpath('//span[span[text()="%s"]]/text()' %(n))
        inforDict['phoneNumber'] = '' if phoneNumber == [] else phoneNumber[2]
        y = u'邮箱:'
        emailAddress = pageSource.xpath('//span[span[text()="%s"]]/text()' %(y))
        inforDict['emailAddress'] = '' if emailAddress == [] else emailAddress[2]
        webLinks = pageSource.xpath('//a[@ng-if="company.baseInfo.websiteList[0]"]/text()')
        inforDict['webLinks']= '' if webLinks == [] else webLinks[0]
        d = u'地址:'
        locate = pageSource.xpath('//span[span[text()="%s"]]/text()' %(d))
        inforDict['locate'] = '' if locate == [] else locate[2]
        opreateCondition = pageSource.xpath('//td[@class="td-regStatus-value"]//p/text()')
        inforDict['opreateCondition'] = '' if opreateCondition == [] else opreateCondition[0]
        registerTime = pageSource.xpath('//td[@class="td-regTime-value"]//p/text()')
        inforDict['registerTime'] = '' if registerTime == [] else registerTime[0]
        legalPersonName = pageSource.xpath('//a[@ng-if="company.baseInfo.legalPersonName"]/text()')
        inforDict['legalPersonName'] = '' if legalPersonName== [] else legalPersonName[0]
        registerMoney = pageSource.xpath('//td[@class="td-regCapital-value"]//p/text()')
        inforDict['registerMoney'] = '' if registerMoney == [] else registerMoney[0]
        infor = pageSource.xpath('//div[@class="c8"]//span[@class="ng-binding"]/text()')
        inforDict['companyType'] = infor[2]
        inforDict['businessType'] = infor[0]
        inforDict['businessScope'] = infor[len(infor)-1]
        inforDict['registerId'] = infor[1]
        holderCt = pageSource.xpath('//div[@id = "nav-main-investment"]//span/text()')
        investCt = pageSource.xpath('//div[@id = "nav-main-outInvestment"]//span/text()')
        print holderCt, investCt
        inforDict['shareHolderInfo'] = ''
        if holderCt != []:
            holderCt = int(holderCt[0])
            for i in range(1, holderCt+1):
                holderName = pageSource.xpath('//div[@ng-repeat="investor in company.investorList track by $index"][' + str(i) + ']//p//a/text()')[0]
                holderMoney = pageSource.xpath('//div[@ng-repeat="investor in company.investorList track by $index"][' + str(i) + ']//p[@class="ng-binding"]/text()')[0]
                holderType = pageSource.xpath('//div[@ng-repeat="investor in company.investorList track by $index"][' + str(i) + ']//p//span/text()')[0]
                inforDict['shareHolderInfo'] += holderName.strip(u'\t\n ') + holderType.strip(u'\t\n ') + holderMoney.strip(u'\t\n ')
                if i != holderCt:
                    inforDict['shareHolderInfo'] += u'、'
        inforDict['investment'] = ''
        if investCt != []:
            investCt = int(investCt[0])
            for i in range(1, investCt+1):
                investName = pageSource.xpath('//div[@ng-repeat="invest in company.investList track by $index"][' + str(i) + ']//p//a/text()')[0]
                investMoney = pageSource.xpath('//div[@ng-repeat="invest in company.investList track by $index"][' + str(i) + ']//p[2]//text()')[0]
                inforDict['investment'] += investName.strip(u'\t\n ') + investMoney.strip(u'\t\n ')
                if i != investCt:
                    inforDict['investment'] += u'、'
        inforDict['crawlTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        for key in inforDict.keys():
            inforDict[key] = inforDict[key].strip(u'\t\n ').encode('utf-8')
        line = json.dumps(inforDict, ensure_ascii=False) + '\n'
    except IndexError:
        print '解析错误'

def connectPostgersql():#连接数据库
    connector = psycopg2.connect(user=user, password=password, database=database, host=host)
    print 'connect database successfully!'
    return connector

def closeDatabaseConnect(connector, cursor):#关闭数据库连接
    print 'close database connect!'
    cursor.close()
    connector.close()

def getJobFromDb(connector, cursor):
    cursor.execute('select * from jobqueue order by job_id desc limit 1;')
    result = cursor.fetchall()
    if result != []:
        job_id = result[0][0]
        job_content = result[0][1]
        cursor.execute('delete from jobqueue where job_id =' + str(job_id) + ';')
        sys.stdout.write('crawler get a job success!| %s | %s\n' % (job_id, job_content))
    else:
        job_id = ''
    connector.commit()
    return job_id, job_content

def getProxy(connector, cursor):
    cursor.execute('select * from ip_pool;')
    result = cursor.fetchall()
    return result

if __name__ == '__main__':
    #path = os.path.abspath('.')
    #path = os.path.split(path)
    connector = connectPostgersql()
    cursor = connector.cursor()
    job_id = 1 #进入循环，启动任务
    while job_id > 0:
        try:
            job_id, job_content = getJobFromDb(connector, cursor)
            ipList = getProxy(connector, cursor)
            if job_id == '':
                print 'jobqueue is null!'
                break
            job_id -= 1
            time.sleep(delayTime)
            sourceHtml = getHtmlByKeys(job_content, ipList)
            if sourceHtml != '':
                newUrl = parseCompany(html.fromstring(sourceHtml))
                if newUrl != '':
                    sourceHtml = getHtmlByUrl(newUrl)
                    parseCompanyInfor(sourceHtml)
        except psycopg2.errorcodes as e:
            print 'database operate error：', e
            connector.commit()
        break
    closeDatabaseConnect(connector, cursor)
