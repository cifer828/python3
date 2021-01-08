"""
使用selenium爬取天眼查六个板块的信息
地区  行业  规模  股东类型 专利数  成立时间
"""
from selenium import webdriver
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import urllib.parse
from selenium.common import exceptions
import re
import datetime
import pymongo
from selenium.webdriver import DesiredCapabilities
from wotu.config.config import FILTER_COMPANY_MONEY_UPPER_LIMIT
from wotu.config.config import FILTER_COMPANY_MONEY_LOWER_LIMIT
from wotu.config.config import FILTER_COMPANY_YEAR
from wotu.config.config import MONGO_SERVER
from wotu.config.config import MONGO_PORT
from wotu.spiders.track_asset import spider_qichacha
import requests
caps = DesiredCapabilities.PHANTOMJS
caps["phantomjs.page.settings.userAgent"] = \
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36"

driver = webdriver.PhantomJS(desired_capabilities=caps)
# driver = webdriver.Chrome('/usr/local/Cellar/chrome/chromedriver',desired_capabilities=caps)
driver.implicitly_wait(8)
driver.set_page_load_timeout(20)
CONN = pymongo.MongoClient(MONGO_SERVER, MONGO_PORT)

"""搜索起始页，得到详情页的网址"""


def search_mainpage(query, times=0):
    global driver
    try:
        baseurl = 'http://www.tianyancha.com/search?'
        params = {
            'key': query,
            'checkForm': 'searchBox'
        }
        url = baseurl + urllib.parse.urlencode(params)
        driver.get(url)
        href=''
        full_name=''
        history_name=''
        wait = WebDriverWait(driver, 10)
        temp_driver = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="ng-view"]/div[2]/div/div/div[1]/div[3]')))
        company_num=driver.find_element_by_xpath('//body/div[1]/div[2]/div/div/div[1]/div[2]/div[1]/span[1]').text
        company_num=int(company_num)
        if company_num>=5:
            company_num=5
        for i in range(1,company_num+1):
            temp_href=temp_driver .find_element_by_xpath('./div[%d]/div[2]/div[1]/div[1]/a' % i).get_attribute('href')
            temp_full_name=temp_driver .find_element_by_xpath('./div[%d]/div[2]/div[1]/div[1]/a/span' % i).text
            temp_history_name=''
            try:
                if temp_driver.find_element_by_xpath('./div[%d]/div[2]/div[3]/div/div[4]/div/span[1]' % i).text=='历史名称':
                    temp_history_name=temp_driver .find_element_by_xpath('./div[%d]/div[2]/div[3]/div/div[4]/div/span[3]' % i).text
            except Exception as e:
                temp_history_name=''
            if temp_full_name==query:
                href=temp_href
                full_name=temp_full_name
                history_name=temp_history_name
            else:
                if temp_history_name == query:
                    href = temp_href
                    full_name = temp_full_name
                    history_name = temp_history_name
        return href,full_name,history_name
    except exceptions.TimeoutException:
        driver.save_screenshot('screenshot.png')
        try:
            status = requests.get(url).status_code#返回状态码
        except requests.exceptions.ConnectionError:
            status=404
        if status==404:
            if times < 5:
                times += 1
                print('网络中断，重试中'+str(status))
                return search_mainpage(query, times)
            else:
                print('网络中断'+str(status))
                return None
        else:
            print("访问连接受到限制,状态码"+str(status))
            return None
    # except exceptions.InvalidSwitchToTargetException:
    #     print('页面跳转失败，网址不存在')
    # except exceptions.InvalidCookieDomainException:
    #     print('试图在不同的domain而不是目前的URL中添加一个cookie')
    # except exceptions.RemoteDriverServerException:
    #     print('远程服务器数据库异常')
    # except exceptions.UnableToSetCookieException:
    #     print('无法设置cookie')
    except Exception as e:
        print(e)
        return None


def search_by_holder(query):
    result = search_one_page_by_holder(query, 1)
    href_list = result[0]
    total_pages = result[1]
    if total_pages > 1:
        try:
            for page in range(2, total_pages):
                href_list += search_one_page_by_holder(query, page)[0]
        except Exception as e:
            print(e)
    return href_list


def search_one_page_by_holder(query, page_num, times=0):
    """
    搜索条件：股东/高管
    输出：一页公司链接,总页数
    """
    global driver
    try:
        baseurl = 'http://www.tianyancha.com/search?'
        params = {
            'key': query,
            'p%dsearchType' % page_num: 'human'
        }
        url = baseurl + urllib.parse.urlencode(params)
        print(url)
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        href_list = []
        total_pages = 0
        try:
            row = 0
            str_pages = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="ng-view"]/div[2]/div/div/div[1]/div[4]/div'))).text
            total_pages = int(re.findall('\d', str_pages)[0])
            print(total_pages)
            while (True):
                href_list.append(wait.until(EC.element_to_be_clickable((By.XPATH,
                                                                        '//*[@id="ng-view"]/div[2]/div/div/div[1]/div[3]/div[%d]/div[2]/div[1]/div[1]/a' % row))).get_attribute(
                    'href'))
                name = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                              '//*[@id="ng-view"]/div[2]/div/div/div[1]/div[3]/div[%d]/div[2]/div[1]/div[1]/a/span' % row))).text
                print(name, href_list[-1])
                if '有限合伙' in name:
                    print('----DIVING----')
                    href_list += search_by_holder(query)
        except Exception as e:
            print('error:', e)
        return href_list, total_pages

    except exceptions.TimeoutException:
        driver.save_screenshot('screenshot.png')
        try:
            status = requests.get(url).status_code#返回状态码
        except requests.exceptions.ConnectionError:
            status=404
        print(status)
        print('crawl again')
        if times < 5:
            times += 1
            return search_mainpage(query, times)
        else:
            return ''


"""对money字符串进行处理
输入：页面中的字符串，如(人民币)6500万元
输出：[类型，金额，单位] ，如['人民币', '6500.0000', '万']
"""


def parse_money(money):
    pattern1 = re.compile(r'(\(人民币|美元\))([\d.]+)(.*?)')
    pattern2 = re.compile(r'([\d.]+)(.*?)(人民币|美元)')
    match1 = pattern1.search(money)
    match2 = pattern2.search(money)
    if match1:
        return [match1.group(1)[1:-1], match1.group(2), match1.group(3)]
    elif match2:
        return [match2.group(3), match2.group(1), match2.group(2)]
    else:
        return [0, 0, 0]


"""搜索详情页
输入：公司详细内容的网址
输出：公司地区  行业  规模  股东类型 专利数  成立时间的信息
"""


def search_detail(href, history_name,times=0):
    global driver
    adjust_num = 2  # 调整上市与非上市公司标签抓取位置
    try:
        driver.get(href)
        wait = WebDriverWait(driver, 10)

        contain_element = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="ng-view"]/div[2]/div/div/div')))

        # 公司名称
        try:
            company_name = contain_element.find_element_by_xpath('./div[1]/div[1]/div[2]/div/span').text
        except Exception as e:
            company_name = ''
        # 是否上市
        try:

            stock_num = contain_element.find_element_by_xpath('./div[2]/div/div[1]/div/div/div/div/div[1]/div[1]').text
            if stock_num=='上市信息':
                on_list = True
                adjust_num = 3
            else:
                on_list = False
            print(on_list)

        except Exception as e:
            on_list = False
        # 公司地址
        try:
            location = contain_element.find_element_by_xpath('./div[1]/div[1]/div[2]/div/div[3]/div[2]/span[2]').text
        except Exception as e:
            location = ''
        if ((location == '')or('@' in location)or('暂无' in location)):
            try:
                location = contain_element.find_element_by_xpath(
                    './div[1]/div[1]/div[2]/div/div[4]/div[2]/span[2]').text
            except Exception as e:
                location = ''
        #网站
        try:
            web_site = contain_element.find_element_by_xpath('./div[1]/div[1]/div[2]/div/div[3]/div[1]/a').text
        except Exception as e:
            web_site = ''
        #电话
        try:
            contact_phone = contain_element.find_element_by_xpath('./div[1]/div[1]/div[2]/div/div[2]/div[1]/span[2]').text
        except Exception as e:
            contact_phone = ''
        if contact_phone == '':
            try:
                contact_phone = contain_element.find_element_by_xpath('./div[1]/div[1]/div[2]/div/div[3]/div[1]/span[2]').text
            except Exception as e:
                contact_phone = ''
        #邮箱
        try:
            contact_mail = contain_element.find_element_by_xpath('./div[1]/div[1]/div[2]/div/div[2]/div[2]/span[2]').text
        except Exception as e:
            contact_mail = ''
        if contact_mail == '':
            try:
                contact_mail = contain_element.find_element_by_xpath('./div[1]/div[1]/div[2]/div/div[3]/div[2]/span[2]').text
            except Exception as e:
                contact_mail = ''
        # 公司行业
        try:
            industry = contain_element.find_element_by_xpath(
                "./div[2]/div/div[2]/div[%d]/div[3]/table/tbody/tr[3]/td[1]/div/span" % adjust_num).text
        except Exception as e:
            industry = ''
        # 公司注册资本
        try:
            money = contain_element.find_element_by_xpath(
                './div[2]/div/div[2]/div[%d]/div[2]/table/tbody/tr/td[2]/div' % adjust_num).text
        except Exception as e:
            # money = ['','','']
            money = ''
        # 股东列表
        try:
            holders_element = contain_element.find_element_by_xpath(
                './div[2]/div/div[%d]/div[5]/div[2]/table/tbody' % adjust_num)
            holders_num=contain_element.find_element_by_xpath('./div[2]/div/div[%d]/div[5]/div[1]/span'% adjust_num).text
            holders_num=int(holders_num[1:-1])+1
            holders = []
            holders_invest_par=[]
            for i in range(1,holders_num):
                holder = holders_element.find_element_by_xpath('./tr[%d]/td[1]/a'%i ).text
                try:
                    holder_invest_par = holders_element.find_element_by_xpath('./tr[%d]/td[2]/div/div/span' % i).text
                except:
                    holder_invest_par=None
                holders.append(holder)
                holders_invest_par.append(holder_invest_par)
        except Exception as e:
            holders = []
            holders_invest_par = []
        # 成立时间
        try:
            founded_time = contain_element.find_element_by_xpath(
                'div[2]/div/div[2]/div[%d]/div[2]/table/tbody/tr/td[3]/div' % adjust_num).text
        except Exception as e:
            founded_time = ''
        # 专利数量
        try:
            patent_count = driver.find_element_by_id('nav-main-patentCount').find_element_by_xpath(
                './span').text.strip()[1:-1]
        except Exception as e:
            patent_count = 0
        # 著作权
        try:
            copyright_count = driver.find_element_by_id('nav-main-cpoyRCount').find_element_by_xpath(
                './span').text.strip()[1:-1]
        except Exception as e:
            copyright_count = 0
        #地区
        try:
            city = re.findall('([^省]+市)', location)[0]
        except Exception as e:
            city = ''
        #省份
        if city in ['上海市','北京市','天津市','重庆市']:
            province=city
        else:
            try:
                province = re.findall('(.+省)', location)[0]
            except Exception as e:
                province = ''
        #主要负责人
        try:
            principal = contain_element.find_element_by_xpath(
                './div[2]/div/div[2]/div[2]/div[2]/table/tbody/tr/td[1]/a').text
        except Exception as e:
            principal = ''
        try:
            money=re.findall('(\d+)',money)[0]
            money = float(money)
        except Exception as e:
            money = 0.0
        patent_count=int(patent_count)
        copyright_count=int(copyright_count)
        contact_way={"电话":contact_phone,"邮箱":contact_mail}
        qualification={"专利数":patent_count,"著作权数":copyright_count}
        holders_info={"股东":holders,"出资比例":holders_invest_par}
        search_link=href
        return {"企业全称": company_name,"曾用名":history_name,"成立日期": founded_time,"地区": city,"省份": province,
                "注册资本": money,"联系方式":contact_way ,"网站":web_site,"主要负责人": principal,"股东状况":holders_info,
                "企业资质":qualification,"链接":search_link,"公司地址": location, "行业": industry,"是否上市": on_list}
    except exceptions.TimeoutException as e:
        print(e.args)
        try:
            status = requests.get(href).status_code#返回状态码
        except requests.exceptions.ConnectionError:
            status=404
        if status==404:
            if times < 5:
                print('crawl again')
                times += 1
                return search_detail(href, times)
            else:
                return {}
        else:
            print("访问连接受到限制,状态码"+str(status))
            return{}


def read_whitelist(col_name, key_name):
    db = CONN['company']
    collection = db[col_name]
    return [item[key_name] for item in collection.find()]


def write_raw_company_to_db(item):
    db = CONN['company']
    collection = db['raw_company']
    item['爬取时间'] = datetime.datetime.now()
    collection.insert(item)
    return item


def write_filtered_company_to_db(item):
    db = CONN['company']
    collection = db['raw_company']
    item['爬取时间'] = datetime.datetime.now()
    collection.insert(item)

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

def search_company(company_name):
    """
    查找公司详细消息：
    先从数据库查找公司名字，数据库没有的话就去天眼查找，查找后输入到数据库中
    返回公司详细信息
    """
    try:
        target=1#判断合格情况
        detail = get_company_detail_from_db(company_name)
        detail = None
        if not detail:
            href,full_name,history_name = search_mainpage(company_name)
            print(href)
            if href == '':
                print("天眼查找不到公司相关链接："+company_name)
                detail=spider_qichacha.search_detail(company_name)
            #raise Exception
            else:
                detail = search_detail(href, history_name)
                if ((company_name != detail["企业全称"]) and (company_name !=history_name)):  # 避免错误搜索
                    print("天眼查的企业全称与曾用名均找不到公司：" + company_name)
                    detail = spider_qichacha.search_detail(company_name)
                    # raise Exception
            target=filter_company(detail)
            detail=write_raw_company_to_db(detail)
        return detail,target
    except Exception as e:
         target=-1#运行出错
         detail={}
         return detail,target

    detail = get_company_detail_from_db(company_name)
    if not detail:
        href,full_name,history_name = search_mainpage(company_name)
        print(href)
        if href == '':
            print("找不到公司："+company_name)
            return None
            # raise Exception

        detail = search_detail(href,history_name)
        if (company_name != detail["企业全称"]) and (company_name !=history_name):  # 避免错误搜索
            print("找不到公司：" + company_name)
            # raise Exception
            return None
        detail=write_raw_company_to_db(detail)
    return detail



def filter_company(detail):
    flag_dict = {'district': False, 'money': False, 'industry': False, 'build_date': False, 'holders': True}
    # 地点
    address_list = read_whitelist('whitelist_district', 'city')
    location = detail['公司地址']
    for ad in address_list:
        if ad in location:
            flag_dict['district'] = True
            break
    # 行业
    industry_list = read_whitelist('whitelist_industry', 'industry')
    industry = detail['行业']
    for ind in industry_list:
        if ind[0] in industry:
            flag_dict['industry'] = True
            break
    # 资金
    if FILTER_COMPANY_MONEY_LOWER_LIMIT <= detail['注册资本'] <= FILTER_COMPANY_MONEY_UPPER_LIMIT:
        flag_dict['money'] = True
    # 注册时间
    build_date = detail['成立日期']
    try:
        date = datetime.datetime.strptime(build_date, '%Y-%m-%d')
        diff = datetime.datetime.now() - date
        flag_dict['build_date'] = diff.days <= FILTER_COMPANY_YEAR * 365
    except:
        flag_dict['build_date'] = False

    # 是否有机构股东
    # for s in detail['股东']:
    #     if '有限' in s or '公司' in s:
    #         flag_dict['holders'] = True
    # 企业资质[专利数，著作权数]

    flag_dict['patent'] = detail['企业资质']['专利数']+ detail['企业资质']['著作权数'] > 0
    for key,value in flag_dict.items():
        print(key,value)

    flag_dict['patent'] = sum(detail['企业资质'].values()) > 0
    # for key,value in flag_dict.items():
    #     print(key,value)

    for flag in flag_dict.values():
        if not flag:
            return 0
    # write_filtered_company_to_db(detail)
    return 1


if __name__ == '__main__':
    # company_list=[
    #     '西安中科晶像光电科技有限公司',
    #     '国家电网公司',
    #     '山东锦华电力设备有限公司',
    #     '华中电网有限公司',
    #     '皇家飞利浦电子股份有限公司',
    #     '苏州思创源博电子科技有限公司',
    #     '无锡新大力电机有限公司',
    #     '尤米科尔公司'
    #     '宁波微行航空科技有限公司'
    #     '北京臻迪智能科技有限公司'
    #     '杭州阿里创业投资有限公司'
    # ]
    # for i in company_list:
    company_detail,target = search_company('杭州阿里创业投资有限公司')

    company_detail = search_company('杭州阿里创业投资有限公司')
    company_detail = search_company('上海百胜软件股份有限公司')
    #search_iteration_investment_company('北京百度网讯科技有限公司')
    print(search_company('国家电网公司'))

    #     print(i)
    #     print(filter_company(detail))
    # seleium_test()
    # print(search_by_holder('杭州维思投资合伙企业（有限合伙）'))
    driver.quit()
