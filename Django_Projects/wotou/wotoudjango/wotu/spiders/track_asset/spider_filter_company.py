from selenium import webdriver
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import DesiredCapabilities
import pandas as pd
import urllib.parse
from selenium.common.exceptions import TimeoutException
import time
import pymongo
import datetime
from spider_tianyancha import search_detail

from bson.dbref import DBRef
def search_mainpage(query, times=0):

    baseurl = 'http://www.tianyancha.com/search?'
    params = {
        'key': query,
        'checkForm': 'searchBox'
    }
    url = baseurl + urllib.parse.urlencode(params)
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    try:
        href = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ng-view"]/div[2]/div/div/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/a'))).get_attribute('href')
        print (href)
    except TimeoutException:
        driver.save_screenshot('screenshot.png')
        print('crawl again')
        if times < 5:
            times += 1
            return search_mainpage(query, times)
        else:
            return '', '名称未找到', ''
    try:
        name = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ng-view"]/div[2]/div/div/div[1]/div[3]/div[1]/div[2]/div[1]/div[1]/a/span'))).text
        name = name.replace('<em>', '')
        name = name.replace('</em>', '')
        print (name)
        if name == query:
            return name, '名称正确', href
        else:
            try:
                bname = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="ng-view"]/div[2]/div/div/div[1]/div[3]/div[1]/div[2]/div[3]/div/div[4]/div/span[3]'))).text
                print (bname)
                bname = bname.replace('<em>', '')
                bname = bname.replace('</em>', '')
                type = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="ng-view"]/div[2]/div/div/div[1]/div[3]/div[1]/div[2]/div[3]/div/div[4]/div/span[1]'))).text
                if bname==query:
                    return name,type,href
                else:
                    return name,'名称需修改',href
            except:
                return '', '名称未找到', href
    except:
        return '', '名称未找到', href


def get_company_detail_from_db(company_name):
    '''
    输入：公司名称
    若公司存在于数据库，输出条目
    不存在输出None
    '''
    db = CONN['company']
    collection = db['raw_company']
    ret = collection.find_one({'公司名称': company_name})
    if not ret:
        return None
    return ret

def write_raw_company_to_db(item):
    db = CONN['company']
    collection = db['raw_company']
    item['爬取时间'] = datetime.datetime.now()
    _id = collection.insert(item)
    print (_id)
    return _id

if __name__ == '__main__':
    CONN = pymongo.MongoClient('106.75.65.56', 27017)
    db = CONN['company']
    caps = DesiredCapabilities.PHANTOMJS
    caps["phantomjs.page.settings.userAgent"] = \
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36"

    #driver = webdriver.PhantomJS(desired_capabilities=caps)
    driver = webdriver.Chrome('/usr/local/Cellar/chrome/chromedriver',desired_capabilities=caps)

    df = pd.read_excel('企业名称.xlsx',index_col=0)
    #print (df.head(10))

    company_list = df['企业名称'].values.tolist()
    company_name_new = []
    company_type=[]



    for company in ['北京臻迪智能科技有限公司']:

        name,type,href = search_mainpage(company)
        print (name)
        detail = get_company_detail_from_db(name.strip())
        print (detail)

        company_name_new.append(name)
        company_type.append(type)
        print (company,name,type)
        if href!='':
            if not detail:
                detail = search_detail(href)
                print (detail)
                _id = write_raw_company_to_db(detail)
            else:
                _id = detail['_id']
            item=dict()
            item['引用'] = DBRef("raw_company", _id)
            item['来源'] = 'origin'
            ret = db.filtered_company.find_one({'引用': item['引用']})
            if not ret:
                db.filtered_company.insert(item)

            time.sleep(3)

    dicts = {
        '原名称':company_list[0:50],
        '新名称':company_name_new,
        '类型':company_type
    }

    #df = pd.DataFrame(dicts)
    #df.to_csv('result.csv',encoding='gbk')

    driver.close()