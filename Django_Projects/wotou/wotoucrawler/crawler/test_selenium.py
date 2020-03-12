# -*- coding: utf-8 -*-
from selenium import webdriver
from time import sleep
import sys
import time
import urllib
# import urllib, selenium.webdriver.support.ui as ui, time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0"
)
dcap["phantomjs.page.settings.preferer"] = ( "http://www.tianyancha.com" )
dcap["phantomjs.page.settings.loadImages"] = False

def yaozhByPhantom():
    by = webdriver.PhantomJS()
    for i in range(1, 6):
        url = 'http://db.yaozh.com/zhuce?p=' + str(i)
        print url
        by.get(url)
        f = open('logs/phantom_yaozh'+str(i)+'.html', 'w')
        f.write(by.page_source.encode('utf-8'))
        f.close()
    by.quit()


# company
def tianyanchaCompany(driver, companyids):
    for companyid in companyids:
        url = 'http://www.tianyancha.com/company/'+companyid
        sys.stdout.write("Fetching %s ..." % (companyid))
        driver.get(url)
        f = open('logs/tianyancha-company-' + companyid + '-' + driver.name + '.html', 'w')
        page = driver.page_source.encode('utf-8')
        f.write(page)
        f.close()
        sys.stdout.write("\t Got %dK\n" % (len(page)/1024))
        sleep(2)


def tianyanchaCompanyByChrome(companyids):
    by = webdriver.Chrome('/usr/local/bin/chromedriver')
    tianyanchaCompany(by, companyids)
    by.quit()


def tianyanchaCompanyByPhantom(companyids):
    by = webdriver.PhantomJS()
    tianyanchaCompany(by, companyids)

def phantomTianyanchaSearch(name):
    t = time.time()
    by = webdriver.PhantomJS()
    service_args = [
    '--proxy=222.163.236.133:8118',
    '--proxy-type=http'
    ]
    by = webdriver.PhantomJS(service_args=service_args)
    url = 'http://www.tianyancha.com/search/' + urllib.quote_plus(name)
    by.get(url)
    sleep(5)
    f = open('logs/phantom_tianyancha'+name+'.html', 'w')
    page = by.page_source.encode('utf-8')
    f.write(page)
    f.close()
    print url, '\tgot', len(page)
    print by.current_url
    by.quit()


# search
def tianyanchaSearch(driverName, names):
    proxy = "120.27.142.209:82"
    if driverName.lower().startswith('chrome'):
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument('--proxy-server=%s' %(proxy))
        driver = webdriver.Chrome(chrome_options=chromeOptions)
    else:
        service_args = [
            '--proxy=%s' % (proxy),
            '--proxy-type=http'
        ]
        driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=service_args)
    for name in names:
        '''
        url = 'http://www.tianyancha.com/search/' + \
            urllib.quote_plus(name) + '?checkFrom=searchBox'
        '''
        url = "http://www.tianyancha.com/company/638562997"
        sys.stdout.write("%s|%s searching %s|" % \
                         (time.strftime('%a %H:%M:%S'), driverName, name))
        driver.get(url)
        sleep(3)
        print driver.title
        f = open('logs/tianyancha-search-'+name+'-'+driverName+'.html', 'w')
        page = driver.page_source.encode('utf-8')
        f.write(page)
        f.close()
        sys.stdout.write("Got %dK\n" % (len(page)/1024))
        # sleep(9)
    driver.quit()


if __name__ == '__main__':
    # phantomYaozh()
    # chromeTianyancha('1218773262')
    companyids = ['1218773262', '719792175', '2347856627', '2342953041']
    # phantomTianyanchas(companyids)
    companynames = ['汕头金石制药总厂',\
                    '江南电镀厂',\
                    '蘑菇街',\
                    '腾讯科技',\
                    '百度公司',\
                    '美丽说',\
                    '天眼查',\
                    '浙商银行', \
                    '泰隆银行', \
                    '阿里巴巴', \
                    '魅族科技', \
                    '小米']
    print('==================')
    #tianyanchaSearch('chrome', companynames)
    print('------------------')
    tianyanchaSearch('phantomjs', companynames)
