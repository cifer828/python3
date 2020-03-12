#-*-coding:utf-8-*-#
import requests
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import time
try:
    browser = webdriver.Chrome('/usr/local/Cellar/chrome/chromedriver')
    browser.get('http://www.qichacha.com/')
    input = browser.find_element_by_css_selector('body > header > div > div.pull-right.hidden-xs > a:nth-child(3)')
    input.click()
    wait = WebDriverWait(browser,10)
    wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="user_login_normal"]/div[8]/div[2]/a')))
    qq_click = browser.find_element_by_xpath('//*[@id="user_login_normal"]/div[8]/div[2]/a')
    qq_click.click()
    browser.switch_to.frame('ptlogin_iframe')
    wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="switcher_plogin"]')))
    login_button=browser.find_element_by_xpath('//*[@id="switcher_plogin"]')
    login_button.click()
    #browser.execute_script('javascript:void(0);')
    wait.until(EC.presence_of_element_located((By.ID,'u')))
    wait.until(EC.presence_of_element_located((By.ID,'p')))
    wait.until(EC.element_to_be_clickable((By.ID,'login_button')))
    username = browser.find_element_by_id('u')
    password = browser.find_element_by_id('p')
    button = browser.find_element_by_id('login_button')
    username.clear()
    password.clear()
    username.send_keys('xxxx')
    password.send_keys('xxxx')
    button.click()
    # wait.until(EC.presence_of_element_located((By.ID,'searchkey')))
    # wait.until(EC.element_to_be_clickable((By.ID,'V3_Search_bt')))
    # input = browser.find_element_by_id("searchkey")
    # button = browser.find_element_by_id('V3_Search_bt')
    # input.send_keys(u'腾讯')
    # button.click()

    time.sleep(3)

    print(browser.get_cookie('_umdata'))
    cookie_dict={
            'UM_distinctid': browser.get_cookie('UM_distinctid')['value'] ,
            'gr_user_id': browser.get_cookie('gr_user_id')['value'],
            '_uab_collina': browser.get_cookie('_uab_collina')['value'],
            'acw_tc': browser.get_cookie('acw_tc')['value'],
            #'_umdata': '70CF403AFFD707DF01F447BEB8F98B0A64DE1388E1FB72C22705EF3B0690146152B13D1F2132E739CD43AD3E795C914C3E56FC42EB4918121BE0F971D1CB2D53',
            'PHPSESSID': browser.get_cookie('PHPSESSID')['value'],
            'gr_session_id_9c1eb7420511f8b2': browser.get_cookie('gr_session_id_9c1eb7420511f8b2')['value'],
            'CNZZDATA1254842228': browser.get_cookie('CNZZDATA1254842228')['value']
    }

    print(cookie_dict)
finally:
    browser.close()





