# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
from wotu.lib.db_connection import *
from lib.db_connection import *


class ShengwuguCrawlPipeline(object):
    def __init__(self):
        self.db = mongodb_connection('news')


    '''
    The default pipeline invoke function
    '''

    def process_item(self, item, spider):
        # url = item['art_url']
        # count = self.cursor.execute('select url from bioon where url="' + url + '"')
        # if count == 0:
        #     self.cursor.execute('insert into bioon(title,url,type,content,time,spidertime) values(%s,%s,%s,%s,%s,%s)',
        #                  (item['art_name'], item['art_url'],
        #                   item['art_type'], item['art_content'], item['art_time'], item['spidertime']))
        #
        # self.connect.commit()
        self.db.shengwugu.insert(item)
        return item

