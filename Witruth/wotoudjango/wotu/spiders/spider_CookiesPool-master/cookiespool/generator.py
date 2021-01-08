#-*-coding:utf-8-*-#
import json

import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from cookiespool.config import *
from cookiespool.db import CookiesRedisClient, AccountRedisClient
from cookiespool.verify import Yundama

import time


class CookiesGenerator(object):
    """
    父类, 初始化一些对象
    :param name: 名称
    :param browser: 浏览器, 若不使用浏览器则可设置为 None
    """
    def __init__(self,name='default',browser_type=DEFAULT_BROWSER):
        self.name=name
        self.cookies_db = CookiesRedisClient(name=self.name)
        self.account_db = AccountRedisClient(name=self.name)
        self.browser_type = browser_type

    def _init_browser(self, browser_type):
        """
        通过browser参数初始化全局浏览器供模拟登录使用
        :param browser: 浏览器 PhantomJS/ Chrome
        :return:
        """
        if browser_type=='PhantomJs':
            caps = DesiredCapabilities.PHANTOMJS
            caps["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
            self.browser = webdriver.PhantomJS(desired_capabilities=caps)
        else:
            self.browser = webdriver.Chrome('/usr/local/Cellar/chrome/chromedriver')

    def new_cookies(self, username, password):
        raise NotImplementedError

    def set_cookies(self, account):
        """
        根据账户设置新的Cookies
        :param account:
        :return:
        """
        results = self.new_cookies(account.get('username'), account.get('password'))
        if results:
            username, cookies = results
            print(('Saving Cookies to Redis', username, cookies))
            self.cookies_db.set(username, cookies)


    def run(self):
        """
        运行, 得到所有账户, 然后顺次模拟登录
        :return:
        """
        accounts = self.account_db.all()
        cookies = self.cookies_db.all()
        # Account 中对应的用户
        accounts = list(accounts)
        # Cookies中对应的用户
        valid_users = [cookie.get('username') for cookie in cookies]
        print(('Getting', len(accounts), 'accounts from Redis'))
        if len(accounts):
            self._init_browser(browser_type=self.browser_type)
        for account in accounts:
            if not account.get('username') in valid_users:
                print(('Getting Cookies of ', self.name, account.get('username'), account.get('password')))
                self.set_cookies(account)
        print('Generator Run Finished')


    def close(self):
        try:
            print('Closing Browser')
            self.browser.close()
            del self.browser
        except TypeError:
            print('Browser not opened')


class WeiboCookiesGenerator(CookiesGenerator):
    """
    初始化操作, 微博需要声明一个云打码引用
    :param name: 名称微博
    :param browser: 使用的浏览器
    """
    def __init__(self, name='weibo', browser_type=DEFAULT_BROWSER):
        CookiesGenerator.__init__(self,name,browser_type)
        self.name = name
        self.ydm=Yundama(YUNDAMA_USERNAME, YUNDAMA_PASSWORD, YUNDAMA_APP_ID, YUNDAMA_APP_KEY)


    def _success(self,username):
        wait = WebDriverWait(self.browser,5)
        success = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'me_portrait_w')))
        if success:
            print('登录成功')
            self.browser.get('http://weibo.cn/')

            if "我的首页" in self.browser.title:
                print((self.browser.get_cookies()))
                cookies = {}
                for cookie in self.browser.get_cookies():
                    cookies[cookie["name"]] = cookie["value"]
                print(cookies)
                print('成功获取到Cookies')
                return (username, json.dumps(cookies))

    def new_cookies(self, username, password):
        """
        生成Cookies
        :param username: 用户名
        :param password: 密码
        :return: 用户名和Cookies
        """
        print(('Generatinng cookies of',username))
        self.browser.delete_all_cookies()
        self.browser.get('http://my.sina.com.cn/profile/unlogin')
        wait = WebDriverWait(self.browser, 20)

        try:
            login = wait.until(EC.element_to_be_clickable((By.ID,'hd_login')))
            login.click()
            user = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.loginformlist input[name="loginname"]')))
            user.send_keys(username)
            psd = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.loginformlist input[name="password"]')))
            psd.send_keys(password)
            submit = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.login_btn')))
            submit.click()
            try:
                result = self._success(username)
                if result:
                    return result
            except TimeoutException:
                print ('出现验证码，开始识别验证码')
                yzm = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.loginform_yzm .yzm')))
                url = yzm.get_attribute('src')
                cookies = self.browser.get_cookies()
                cookie_dict = {}
                for cookie in cookies:
                    cookie_dict[cookie['name']]=cookie['value']
                response = requests.get(url,cookies=cookie_dict)
                #云打码识别结果
                result = self.ydm.identify(stream=response.content)
                if not result:
                    print('验证码识别失败, 跳过识别')
                    return
                door = wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, '.loginform_yzm input[name="door"]')))
                door.send_keys(result)
                submit.click()
                result = self._success(username)
                print(result)
                if result:
                    return result
        except WebDriverException as e:
            print((e.args))


class QCCCookiesGenerator(CookiesGenerator):
    """
    :param name: 名称企查查
    :param browser: 使用的浏览器
    """
    def __init__(self, name='qcc', browser_type=DEFAULT_BROWSER):
        CookiesGenerator.__init__(self,name,browser_type)
        self.name = name
        #self.ydm=Yundama(YUNDAMA_USERNAME, YUNDAMA_PASSWORD, YUNDAMA_APP_ID, YUNDAMA_APP_KEY)


    def _success(self,username):
        wait = WebDriverWait(self.browser,5)
        print('登录成功')
        self.browser.get('http://www.qichacha.com/')

        time.sleep(5)


    def new_cookies(self, username, password):
        """
        生成Cookies
        :param username: 用户名
        :param password: 密码
        :return: 用户名和Cookies
        """
        print(username)
        print(password)
        try:
            #browser = webdriver.Chrome('/usr/local/Cellar/chrome/chromedriver')
            self.browser.get('http://www.qichacha.com/')
            input = self.browser.find_element_by_css_selector('body > header > div > div.pull-right.hidden-xs > a:nth-child(3)')
            input.click()
            wait = WebDriverWait(self.browser, 10)
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="user_login_normal"]/div[8]/div[2]/a')))
            qq_click = self.browser.find_element_by_xpath('//*[@id="user_login_normal"]/div[8]/div[2]/a')
            qq_click.click()
            self.browser.switch_to.frame('ptlogin_iframe')
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="switcher_plogin"]')))
            login_button = self.browser.find_element_by_xpath('//*[@id="switcher_plogin"]')
            login_button.click()
            # browser.execute_script('javascript:void(0);')

            wait.until(EC.presence_of_element_located((By.ID, 'u')))
            wait.until(EC.presence_of_element_located((By.ID, 'p')))
            wait.until(EC.element_to_be_clickable((By.ID, 'login_button')))
            user = self.browser.find_element_by_id('u')
            passwd = self.browser.find_element_by_id('p')
            button = self.browser.find_element_by_id('login_button')
            user.clear()
            passwd.clear()

            user.send_keys(username)
            passwd.send_keys(password)
            button.click()
            # wait.until(EC.presence_of_element_located((By.ID,'searchkey')))
            # wait.until(EC.element_to_be_clickable((By.ID,'V3_Search_bt')))
            # input = browser.find_element_by_id("searchkey")
            # button = browser.find_element_by_id('V3_Search_bt')
            # input.send_keys(u'腾讯')
            # button.click()
            time.sleep(5)
            wait.until(EC.presence_of_element_located((By.ID,'searchkey')))
            cookie_dict = {
                'UM_distinctid': self.browser.get_cookie('UM_distinctid')['value'],
                'gr_user_id': self.browser.get_cookie('gr_user_id')['value'],
                '_uab_collina': self.browser.get_cookie('_uab_collina')['value'],
                'acw_tc': self.browser.get_cookie('acw_tc')['value'],
                # '_umdata': browser.get_cookie('_umdata')['value'],
                'PHPSESSID': self.browser.get_cookie('PHPSESSID')['value'],
                'gr_session_id_9c1eb7420511f8b2': self.browser.get_cookie('gr_session_id_9c1eb7420511f8b2')['value'],
                'CNZZDATA1254842228': self.browser.get_cookie('CNZZDATA1254842228')['value']
            }
            print(cookie_dict)
            print('成功获取到Cookies')
            return (username, json.dumps(cookie_dict))
            # result = self._success(username)
            # if result:
            #     return result

        except WebDriverException as e:
            print((e.args))


