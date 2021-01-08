#! -*- coding:utf-8 -*-
from selenium import webdriver
from scrapy.http import HtmlResponse
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class PhantomjsMiddleware(object):
    def process_request(self, request, spider):
        if spider.name =="simu":
            print "PhantomJS is starting..."
            # dcap = dict(DesiredCapabilities.PHANTOMJS)
            # dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0" )
            # driver = webdriver.PhantomJS(executable_path='C:\Software\Python27\phantomjs.exe', desired_capabilities=dcap) #指定使用的浏览器
            driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\Application\chrome.exe')
            driver.get(request.url)
            time.sleep(1)
            # next_page = driver.find_element_by_class_name('paginate_button next')
            # print next_page
            # js = """document.getElementsByClass('paginate_button next').click();
            #         function click(el){
            #             var ev = document.createEvent("MouseEvent");
            #             ev.initMouseEvent(
            #                 "click",
            #                 true /* bubble */, true /* cancelable */,
            #                 window, null,
            #                  0, 0, 0, 0, /* coordinates */
            #                 false, false, false, false, /* modifier keys */
            #                  0 /*left*/, null
            #                 );
            #             el.dispatchEvent(ev);
            #         }
            #         """
            # driver.execute_script(js) #执行js
            body = driver.page_source
            print "retrieving: " + request.url
            return  HtmlResponse(driver.current_url, body=body, encoding='utf-8', request=request)
        else:
            print "Failed to retrieve: " + request.url
            return