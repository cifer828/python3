import requests
import urllib
from lxml import html
import re
from selenium import webdriver
import time
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait


download_url = "http://tjedu.tjjy.com.cn/api/front/localres/first?flagIp=false"

upload_headers = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
    'Connection':'keep-alive',
    'Cache-Control':'max-age=0',
    'Upgrade-Insecure-Requests':'1',
    'Host':'i.tj.mypep.cn',
    'Cookie':'SERVERID=B; sso_access_token=eyJpdiI6IkI2ZjZRZDUwUkUxNTZ1VTdwRjFIUEE9PSIsInZhbHVlIjoiQ29iS0VUUG9aMTg2Z25YRFpjaXVKZ0FXaU1uam81YXc1Ylg2RWJpdWtnXC9LTjlPRmFcL3QzanhJaXhcL2FDN3VUdGUyOHRHc0E4eXNvWDBNN2Y2STlhenc9PSIsIm1hYyI6IjE0NzAyYzg5YWQxM2EwY2Q1ZjEyYTc5ZDE1MGRlY2Y3MDQ0NGE0OTVlNmIzODM1OTU3NDI4MWMyOTEyMzI1N2MifQ%3D%3D; _ga=GA1.2.320935002.1515811917; _gid=GA1.2.1495905171.1515811917; Hm_lvt_e2f18d091bbea6debd06a167ddec6778=1515811917,1515818121,1515818171,1515820114; Hm_lpvt_e2f18d091bbea6debd06a167ddec6778=1515823322; mypep_session=eyJpdiI6ImNGWU1xWnpQQnVKRXRFQVVXa1lCOGc9PSIsInZhbHVlIjoiR2Z4VDE4dVhvOFFOTzk5STI3Z2pYOXBOd3lYb0VSS3FnVktWa3YxWFwvNVdXOW9XUE9VQStFY1pcLytjaUhkbDA1SmZiYkw4cUZKcDB4d20rSE40MlVBZz09IiwibWFjIjoiZDkzZGI3NDkwNDEyNmFkNTY4MGQ1OTYzZWMxODJjODBkMmI0ODM2NzVmMDQzNDliMTBlNzA0ZWVmOGY1ZDQ4OCJ9',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
}

data = {
    'keyword':'',
    'gradeId':'26',
    'courseId':'4744',
    'resType':'8',
    'originId':'',
    'areaCode':'',
    'sortFlag':'4',
    'curPage':'1',
    'totalPage':'',
}

def retrieve_url(url, data):
    url1 = url  + urllib.parse.urlencode(data)
    r = requests.get(url1)
    return r.content.decode('utf8')

def download():
    file_id = []
    root = html.fromstring(retrieve_url(download_url, data))
    last_page_xpath= '//div[@class="pagination"]/a[2]/@onclick'
    page_num = root.xpath(last_page_xpath)[0]
    pattern = re.compile(",'(\d+)'")
    page_num = int(re.findall(pattern, page_num)[0])
    for i in range(1, page_num):
        print('retrieving page %d' % i)
        data['curPage'] = str(i)
        root = html.fromstring(retrieve_url(download_url, data))
        download_btn_xpath= '//div[@class="btn2"]/a/@onclick'
        download_id_list = root.xpath(download_btn_xpath)
        file_id += download_id_list

    for i in range(len(file_id)):
        id_pattern = re.compile("down\('(.+)',")
        id= re.findall(id_pattern, file_id[i])[0]
        file_url = 'http://tjedu.tjjy.com.cn/api/front/appLocalrs/appLocalrsDown?id=' + id
        r = requests.get(file_url)
        print(i, id)
        with open("C:/Users/zhqch/Desktop/高中英语练习/%d.doc" % (110 + i), "wb") as code:
             code.write(r.content)

def upload():
    cookie_dict = {
        'SERVERID':'B',
        'sso_access_token':'eyJpdiI6InBmVFNCc2M0czNwbmh1c0JpYWU5WVE9PSIsInZhbHVlIjoiWjhkNlpSa0FuemZKeGduNW5TVldjd0hPRUhVMDlteFRKTGhFcHpvM2ZQeXNjSk9GTGxoNlN1UnNHMVwvbnlkdWtqSFl2Q3l0NVdTcE1IMmtzSklBU1lnPT0iLCJtYWMiOiI5YWQyNjU3M2Y0MDkxODg5N2E2MTgzN2ViY2FlYzM0NTkzNTcyOTI1YjM2NjcwMTNjMzU1Njc3ZTdiNGUxZGJhIn0%3D',
        '_ga':'GA1.2.320935002.1515811917',
        '_gid':'GA1.2.1495905171.1515811917',
        'Hm_lvt_e2f18d091bbea6debd06a167ddec6778':'1515811917,1515818121,1515818171',
        'Hm_lpvt_e2f18d091bbea6debd06a167ddec6778':'1515818779',
        '_gat':'1',
        'mypep_session':'eyJpdiI6Im55czEzYkx2b2w0QTkwalJHUzhwMGc9PSIsInZhbHVlIjoiMmFqS2liNzUwS0w4MDRYaW9FTVNmWXd0XC9oM21kS0g3VU0xRWVOTWE4a3N2UmNyVzExODJSNW5cL3U4N1dZbXRrRit1dUlHNFdGWCtMejhXT0ZqeTg5Zz09IiwibWFjIjoiNmQ3YTE4ZDJiMzMzZjYwNzQxNzljNGRmNzhiYzkzYWEwM2RlYmVhMjI5YjRiYzI2MDVhOTczYzQwYTliZWUzOCJ9'
    }
    cookie_dict2 = {
        # 'acw_tc':'AQAAALOZyyjxdgIAgiKgtGksQK8lpcF7',
	    'sso_access_token':'eyJpdiI6InBmVFNCc2M0czNwbmh1c0JpYWU5WVE9PSIsInZhbHVlIjoiWjhkNlpSa0FuemZKeGduNW5TVldjd0hPRUhVMDlteFRKTGhFcHpvM2ZQeXNjSk9GTGxoNlN1UnNHMVwvbnlkdWtqSFl2Q3l0NVdTcE1IMmtzSklBU1lnPT0iLCJtYWMiOiI5YWQyNjU3M2Y0MDkxODg5N2E2MTgzN2ViY2FlYzM0NTkzNTcyOTI1YjM2NjcwMTNjMzU1Njc3ZTdiNGUxZGJhIn0%3D',
	    # '_ga':'GA1.2.320935002.1515811917',
	    # '_gid':'GA1.2.1495905171.1515811917',
	    # 'Hm_lvt_e2f18d091bbea6debd06a167ddec6778':'1515811917,1515818121,1515818171,1515820114',
	    # 'Hm_lpvt_e2f18d091bbea6debd06a167ddec6778':'1515824881'
    }
    upload_url = 'http://i.tj.mypep.cn/teacher/upload'
    # r = requests.get(upload_url, headers = upload_headers)
    # print(r.content.decode('utf8'))
    caps = DesiredCapabilities.PHANTOMJS
    caps["phantomjs.page.settings.userAgent"] = \
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36"
    # driver = webdriver.PhantomJS(executable_path='C:/Software/Python27/phantomjs',  desired_capabilities=caps)
    driver = webdriver.Chrome(executable_path='C:/Software/Python27/chromedriver.exe')
    # driver.implicitly_wait(8)
    # driver.get(upload_url)
    # driver.delete_all_cookies()
    # for key, value in cookie_dict2.items():
    #     print(1)
    #     driver.add_cookie({'domain': 'tj.mypep.cn',
    #                        'name': key,
    #                        'value': value,
    #                        'path':'/',
    #                        'httponly':'True',
    #                        'secure':'False'})
    # # time.sleep(2)
    # driver.refresh()
    driver.get(upload_url)
    driver.find_element_by_id("username").send_keys('flguojinhong')
    driver.find_element_by_id("password").send_keys('123456')
    time.sleep(5)
    driver.find_element_by_xpath('//div[@class="submit"]/input').click()
    driver.find_element_by_name("title").send_keys('习题')
    degree_slt = driver.find_element_by_name("degree_id")
    degree_slt.find_element_by_xpath('//option[@value="3"]').click()
    course_slt = driver.find_element_by_name("course_id")
    course_slt.find_element_by_xpath('//option[@value="3"]').click()

    # print(driver.get_cookies())

upload()

