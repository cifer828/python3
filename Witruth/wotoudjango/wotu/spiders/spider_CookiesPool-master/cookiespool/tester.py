#-*-coding:utf-8-*-#
import json
from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError
from cookiespool.db import *
from cookiespool.generator import WeiboCookiesGenerator

class ValidTester(object):
    def __init__(self,name='default'):
        self.name=name
        self.account_db = AccountRedisClient(name=self.name)
        self.cookies_db = CookiesRedisClient(name=self.name)

    def test(self, account, cookies):
        raise NotImplementedError


    def run(self):
        accounts = self.cookies_db.all()
        for account in accounts:
            username = account.get('username')
            cookies = self.cookies_db.get(username)
            self.test(account, cookies)

class WeiboValidTester(ValidTester):
    def __init__(self,name='weibo'):
        ValidTester.__init__(self,name)

    def test(self,account,cookies):
        print(('Testing Account', account.get('username')))
        try:
            cookies = json.loads(cookies)
        except TypeError:
            # Cookie 格式不正确
            print(('Invalid Cookies Value', account.get('username')))
            self.cookies_db.delete(account.get('username'))
            print(('Deleted User', account.get('username')))
            return None
        try:
            response = requests.get('http://weibo.cn', cookies=cookies)
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'lxml')
                title = soup.title.string
                if title == '我的首页':
                    print(('Valid Cookies', account.get('username')))
                else:
                    print(('Title is', title))
                    # Cookie已失效
                    print(('Invalid Cookies', account.get('username')))
                    self.cookies_db.delete(account.get('username'))
                    print(('Deleted User', account.get('username')))
        except ConnectionError as e:
            print(('Error', e.args))
            print(('Invalid Cookies', account.get('username')))


class QCCValidTester(ValidTester):
    def __init__(self,name='qcc'):
        ValidTester.__init__(self,name)

    def test(self,account,cookies):
        print(('Testing Account', account.get('username')))
        try:
            cookies = json.loads(cookies)
        except TypeError:
            # Cookie 格式不正确
            print(('Invalid Cookies Value', account.get('username')))
            self.cookies_db.delete(account.get('username'))
            print(('Deleted User', account.get('username')))
            return None
        try:
            response = requests.get('http://www.qichacha.com/search?key=%E6%B1%9F%E8%8B%8F%E5%87%8C%E7%89%B9%E7%B2%BE%E5%AF%86%E6%9C%BA%E6%A2%B0%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8', cookies=cookies)
            if response.status_code == 200:
                html = response.text

                if not response.text.startswith('<script>'):
                    #print response.text
                    if not ('user_login' in response.url):
                        print(response.url)
                        print(('Valid Cookies', account.get('username')))
                    else:
                        print(('Invalid Cookies', account.get('username')))
                        self.cookies_db.delete(account.get('username'))
                        print(('Deleted User', account.get('username')))

                else:
                    # Cookie已失效
                    print(('Invalid Cookies', account.get('username')))
                    self.cookies_db.delete(account.get('username'))
                    print(('Deleted User', account.get('username')))
            else:
                print(('Invalid Cookies', account.get('username')))
                self.cookies_db.delete(account.get('username'))
                print(('Deleted User', account.get('username')))
        except ConnectionError as e:
            print(('Invalid Cookies', account.get('username')))
            self.cookies_db.delete(account.get('username'))
            print(('Deleted User', account.get('username')))


if __name__ == '__main__':
    tester = WeiboValidTester()
    tester.run()

