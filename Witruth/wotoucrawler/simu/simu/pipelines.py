# -*- coding: utf-8 -*-
import pymysql
import settings
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class SimuPipeline(object):
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
            self.cursor.execute("""select * from simu where id = %s""", item["id"])
            ret = self.cursor.fetchone()
            if ret:
                self.cursor.execute(
                    """update simu set id = %s,fundName = %s,fundNo = %s, managerName = %s, managerType = %s, workingState = %s, putOnRecordDate = %s,
                       lastQuarterUpdate = %s, isDeputeManage = %s, url = %s, managerUrl = %s, establishDate = %s
                        where id = %s""",
                    (item['id'],
                    item['fundName'],
                    item['fundNo'],
                    item['managerName'],
                    item['managerType'],
                    item['workingState'],
                    item['putOnRecordDate'],
                    item['lastQuarterUpdate'],
                    item['isDeputeManage'],
                    item['url'],
                    item['managerUrl'],
                    item['establishDate'],
                    item['id']))
            else:
                print 222222222222222222222222
                # print  "insert into simu(id, fundName, fundNo, managerName, managerType, workingState, putOnRecordDate,lastQuarterUpdate, isDeputeManage, url, managerUrl, establishDate) value (%s, %s, %s, %s, %s, %s, %s, %d, %s, %s, %s, %s)" % (item['id'], item['fundName'], item['fundNo'], item['managerName'], item['managerType'], item['workingState'],item['putOnRecordDate'],item['lastQuarterUpdate'],item['isDeputeManage'],item['url'],item['managerUrl'],item['establishDate'])
                # print 3333333333333333333333333
                self.cursor.execute(
                    """insert into simu(id, fundName, fundNo, managerName,  managerType, workingState, putOnRecordDate,
                      lastQuarterUpdate, isDeputeManage, url, managerUrl, establishDate) value (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (item['id'],
                    item['fundName'],
                    item['fundNo'],
                    item['managerName'],
                    item['managerType'],
                    item['workingState'],
                    item['putOnRecordDate'],
                    item['lastQuarterUpdate'],
                    item['isDeputeManage'],
                    item['url'],
                    item['managerUrl'],
                    item['establishDate']))
            self.connect.commit()
        except:
            print 44444444444444444444444
        return item

