# -*- coding: utf-8 -*-
import pymysql
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class Spider36KrPipeline(object):
    def __init__(self):
        # MYSQL configuration
        self.connect = pymysql.connect(
            host='106.75.65.56',
            db='news',
            user='root',
            passwd='wotou',
            charset='utf8',
            use_unicode=True)
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        try:
            print item["link"]
            self.cursor.execute("""select * from 36kr where url = %s""", item["link"])
            ret = self.cursor.fetchone()
            if ret:
                self.cursor.execute(
                    """update 36kr set title = %s,url = %s,content = %s, news_date = %s
                        where url = %s""",
                    (item['title'],
                     item['link'],
                     item['content'],
                     item['time'],
                     item['link']))
            else:
                print 222222222222222222222222
                self.cursor.execute(
                    """insert into 36kr(id, title, url, content, news_date) value (%s, %s, %s, %s, %s)""",
                    (item['id'],
                     item['title'],
                     item['link'],
                     item['content'],
                     item['time']))
            self.connect.commit()
        except:
            print 44444444444444444444444
        return item
