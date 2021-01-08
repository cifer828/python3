# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.conf import settings
import sys, psycopg2, logging, json,jieba,string, math
from psycopg2 import errorcodes
import random, xlrd
from xlutils.copy import copy


class EasystagingPipeline(object):
    def __init__(self, settings):
        self.username = settings.get('POSTGRESQL_USERNAME')
        self.password = settings.get('POSTGRESQL_PASSWORD')
        self.host = settings.get('POSTGRESQL_HOST')
        self.database = settings.get('POSTGRESQL_DATABASE')
        self.table_name_dict = settings.get('TABLE_NAME_DICT')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            settings=crawler.settings
        )

    def open_spider(self, spider):
        # 连接到数据库
        try:
            self.connector = psycopg2.connect(
                user=self.username,
                password=self.password,
                host=self.host,
                database=self.database
            )
            print "postgresql database successfully connected!!!"
            self.cursor = self.connector.cursor()
            spider.connector = self.connector
            #jieba.load_userdict('biomedical_dic.txt')
            '''
            #region get key from database
            result = self.cursor.execute('select * from fundcompany;')
            result = self.cursor.fetchall()
            keyDict = []
            for i in range(0, len(result)):
                keyDict.append(eval(result[i][2])['managerName'])
            spider.key = keyDict[random.randint(0, len(keyDict)-1)]
            #endregion
            '''
            self.logger.info('Connecting to database successfully!')
        except psycopg2.Error as e:
            sys.exit('Failed to connect database. Returned: {0:s}'.format(errorcodes.lookup(e.pgcode)))
    def colse_spider(self, spider):
        #关闭数据库连接
        print "close postgresql database connect!"
        print "爬虫" + spider.name + "需要抓取的数据量：" + self.needCt
        print "爬虫" + spider.name + "实际抓取的数据量：" + self.realGetCt
        self.cursor.close()
        self.connector.close()

    def process_item(self, item, spider):
        print "---pipeline processing item ---"
        line = json.dumps(dict(item), ensure_ascii=False) + '\n'
        #print line
        if spider.name == 'crawlfund':
            para = {'id': item['fundId'],
                    'time': item['crawlTime'],
                    'content': line,
                    'database': 'fundcompany'
                    }
            self.databaseOperate(para)
        if spider.name == 'qiduowei':
            #region 写入excel
            file = xlrd.open_workbook(spider.name + '.xls')
            sheet = file.sheets()[0]
            nrows = sheet.nrows
            fileWrite = copy(file)
            writeSheet = fileWrite.get_sheet(0)
            writeSheet.write(nrows, 0, item['companyName'])
            writeSheet.write(nrows, 1, item['phoneNumber'])
            writeSheet.write(nrows, 2, item['registerId'])
            writeSheet.write(nrows, 3, item['emailAddress'])
            writeSheet.write(nrows, 4, item['webLinks'])
            writeSheet.write(nrows, 5, item['locate'])
            writeSheet.write(nrows, 6, item['opreateCondition'])
            writeSheet.write(nrows, 7, item['companyType'])
            writeSheet.write(nrows, 8, item['registerTime'])
            writeSheet.write(nrows, 9, item['legalPersonName'])
            writeSheet.write(nrows, 10, item['registerMoney'])
            writeSheet.write(nrows, 11, item['businessType'])
            writeSheet.write(nrows, 12, item['businessScope'])
            writeSheet.write(nrows, 13, item['shareHolderInfo'])
            writeSheet.write(nrows, 14, item['investment'])
            writeSheet.write(nrows, 15, item['key'])
            fileWrite.save(spider.name + '.xls')
            print spider.name + 'write into excel successfully!'
            #endregion
            para = {
                'id': item['registerId'],
                'time': item['crawlTime'],
                'content': line,
                'keys': item['key'],
                'database': 'qiduowei'
            }
            self.databaseOperateWithKeys(para)
        if spider.name == 'baiteng' and item['state'] != u'失效专利':
            #region 写入excel
            file = xlrd.open_workbook(spider.name + '.xls')
            sheet = file.sheets()[0]
            nrows = sheet.nrows
            fileWrite = copy(file)
            writeSheet = fileWrite.get_sheet(0)
            writeSheet.write(nrows, 0, item['patentName'])
            writeSheet.write(nrows, 1, item['applyPerson'])
            writeSheet.write(nrows, 2, item['patentTime'])
            writeSheet.write(nrows, 3, item['applyId'])
            writeSheet.write(nrows, 4, item['state'])
            writeSheet.write(nrows, 5, item['abstract'])
            fileWrite.save(spider.name + '.xls')
            self.logger.info(spider.name + ' write into excel successfully!')
            #endregion
        if spider.name == 'qichacha':
            #region 写入excel
            file = xlrd.open_workbook(spider.name + '.xls')
            sheet = file.sheets()[0]
            nrows = sheet.nrows
            fileWrite = copy(file)
            writeSheet = fileWrite.get_sheet(0)
            writeSheet.write(nrows, 0, item['companyName'])
            writeSheet.write(nrows, 1, item['phoneNumber'])
            writeSheet.write(nrows, 2, item['registerId'])
            writeSheet.write(nrows, 3, item['emailAddress'])
            writeSheet.write(nrows, 4, item['webLinks'])
            writeSheet.write(nrows, 5, item['locate'])
            writeSheet.write(nrows, 6, item['opreateCondition'])
            writeSheet.write(nrows, 7, item['companyType'])
            writeSheet.write(nrows, 8, item['registerTime'])
            writeSheet.write(nrows, 9, item['legalPersonName'])
            writeSheet.write(nrows, 10, item['registerMoney'])
            writeSheet.write(nrows, 11, item['businessType'])
            writeSheet.write(nrows, 12, item['businessScope'])
            writeSheet.write(nrows, 13, item['shareHolderInfo'])
            writeSheet.write(nrows, 14, item['investment'])
            fileWrite.save(spider.name + '.xls')
            print spider.name + 'write into excel successfully!'
            #endregion
            para = {
                'id': item['registerId'],
                'time': item['crawlTime'],
                'content': line,
                'keys': item['key'],
                'database': 'qichacha'}
            self.databaseOperateWithKeys(para)
        if spider.name == 'xizhi':
            #region 写入excel
            file = xlrd.open_workbook(spider.name + '.xls')
            sheet = file.sheets()[0]
            nrows = sheet.nrows
            fileWrite = copy(file)
            writeSheet = fileWrite.get_sheet(0)
            writeSheet.write(nrows, 0, item['companyName'])
            writeSheet.write(nrows, 1, item['phoneNumber'])
            writeSheet.write(nrows, 2, item['registerId'])
            writeSheet.write(nrows, 3, item['emailAddress'])
            writeSheet.write(nrows, 4, item['webLinks'])
            writeSheet.write(nrows, 5, item['locate'])
            writeSheet.write(nrows, 6, item['opreateCondition'])
            writeSheet.write(nrows, 7, item['companyType'])
            writeSheet.write(nrows, 8, item['registerTime'])
            writeSheet.write(nrows, 9, item['legalPersonName'])
            writeSheet.write(nrows, 10, item['registerMoney'])
            writeSheet.write(nrows, 11, item['businessType'])
            writeSheet.write(nrows, 12, item['businessScope'])
            writeSheet.write(nrows, 13, item['shareHolderInfo'])
            writeSheet.write(nrows, 14, item['investment'])
            fileWrite.save(spider.name + '.xls')
            print spider.name + 'write into excel successfully!'
            #endregion
            para = {
                'id': item['registerId'],
                'time': item['crawlTime'],
                'content': line,
                'keys': item['key'],
                'database': 'xizhi'}
            self.databaseOperateWithKeys(para)
        if spider.name == 'yaozhi':
            para = {
                 'id': item['id'],
                 'time': item['crawlTime'],
                 'content': line,
                 'database': 'yaozhi'
            }
            self.databaseOperate(para)
            if item['databaseType'] == 1:
                #region 写入excel
                file = xlrd.open_workbook(spider.name + '-国产药品.xls')
                sheet = file.sheets()[0]
                nrows = sheet.nrows
                fileWrite = copy(file)
                writeSheet = fileWrite.get_sheet(0)
                writeSheet.write(nrows, 0, item['medicineName'])
                writeSheet.write(nrows, 1, item['englishName'])
                writeSheet.write(nrows, 2, item['medicineSpecification'])
                writeSheet.write(nrows, 3, item['produceIndustry'])
                writeSheet.write(nrows, 4, item['approvalNumber'])
                writeSheet.write(nrows, 5, item['approvalDate'])
                writeSheet.write(nrows, 6, item['medicineType'])
                writeSheet.write(nrows, 7, item['dosageForms'])
                fileWrite.save(spider.name + '-国产药品.xls')
                print spider.name + 'write into excel successfully!'
                #endregion
            elif item['databaseType'] == 2:
                #region 写入excel
                file = xlrd.open_workbook(spider.name + '-进口药品.xls')
                sheet = file.sheets()[0]
                nrows = sheet.nrows
                fileWrite = copy(file)
                writeSheet = fileWrite.get_sheet(0)
                writeSheet.write(nrows, 0, item['medicineName'])
                writeSheet.write(nrows, 1, item['companyName'])
                writeSheet.write(nrows, 2, item['date'])
                fileWrite.save(spider.name + '-进口药品.xls')
                print spider.name + 'write into excel successfully!'
                #endregion
            elif item['databaseType'] == 4:
                #region 写入excel
                file = xlrd.open_workbook(spider.name + '-临床试验.xls')
                sheet = file.sheets()[0]
                nrows = sheet.nrows
                fileWrite = copy(file)
                writeSheet = fileWrite.get_sheet(0)
                writeSheet.write(nrows, 0, item['expName'])
                writeSheet.write(nrows, 1, item['indication'])
                writeSheet.write(nrows, 2, item['expState'])
                writeSheet.write(nrows, 3, item['expStage'])
                writeSheet.write(nrows, 4, item['registerDate'])
                fileWrite.save(spider.name + '-临床试验.xls')
                print spider.name + 'write into excel successfully!'
                #endregion
            elif item['databaseType'] == 5:
                #region 写入excel
                file = xlrd.open_workbook(spider.name + '-国外新药.xls')
                sheet = file.sheets()[0]
                nrows = sheet.nrows
                fileWrite = copy(file)
                writeSheet = fileWrite.get_sheet(0)
                writeSheet.write(nrows, 0, item['medicineName'])
                writeSheet.write(nrows, 1, item['type'])
                writeSheet.write(nrows, 2, item['companyName'])
                writeSheet.write(nrows, 3, item['approvalCountry'])
                writeSheet.write(nrows, 4, item['approvalDate'])
                writeSheet.write(nrows, 5, item['effects'])
                writeSheet.write(nrows, 6, item['introduction'])
                fileWrite.save(spider.name + '-国外新药.xls')
                print spider.name + 'write into excel successfully!'
                #endregion
            elif item['databaseType'] == 3:
                #region 写入excel
                file = xlrd.open_workbook(spider.name + '-药品注册.xls')
                sheet = file.sheets()[0]
                nrows = sheet.nrows
                fileWrite = copy(file)
                writeSheet = fileWrite.get_sheet(0)
                writeSheet.write(nrows, 0, item['medicineName'])
                writeSheet.write(nrows, 1, item['registerType'])
                writeSheet.write(nrows, 2, item['applyType'])
                writeSheet.write(nrows, 3, item['companyName'])
                writeSheet.write(nrows, 4, item['processState'])
                writeSheet.write(nrows, 5, item['stateStartDate'])
                writeSheet.write(nrows, 6, item['valueResult'])
                fileWrite.save(spider.name + '-药品注册.xls')
                print spider.name + 'write into excel successfully!'
                #endregion
        return item

    def databaseOperate(self, para):
        try:
            self.cursor.execute(
                'INSERT INTO ' + para['database'] + '(id, scrapy_time, scrapy_content)'
                'VALUES(%(id)s,%(time)s,%(content)s);',
                para
            )
            self.connector.commit()
            print para['database'] + 'database insert operation success!'
            self.logger.info(para['database'] + ' insert successfully!')
        except psycopg2.Error as e:
            self.connector.commit()
            if format(errorcodes.lookup(e.pgcode)) == 'UNIQUE_VIOLATION':
                try:

                    self.cursor.execute(
                        'update ' + para['database'] + ' set scrapy_time = %(time)s, scrapy_content=%(content)s where id =%(id)s;',
                        para)
                    self.connector.commit()
                    print para['database'] + 'database update operation success!'
                    self.logger.info(para['database'] + ' update successfully!')
                except psycopg2.Error as e:
                    self.logger.info(format(errorcodes.lookup(e.pgcode)))
                    self.connector.commit()
                    self.logger.info('failed to update ' + para['database'])

    def databaseOperateWithKeys(self, para):
        try:
            self.cursor.execute(
                'INSERT INTO ' + para['database'] + '(id, scrapy_time, scrapy_keys, scrapy_content)'
                'VALUES(%(id)s,%(time)s,%(keys)s,%(content)s);',
                para
            )
            self.connector.commit()
            print para['database'] + ' database insert operation success!'
            self.logger.info(para['database'] + ' insert successfully!')
        except psycopg2.Error as e:
            self.connector.commit()
            if format(errorcodes.lookup(e.pgcode)) == 'UNIQUE_VIOLATION':
                try:

                    self.cursor.execute(
                        'update ' + para['database'] + ' set scrapy_time = %(time)s, scrapy_content=%(content)s,scrapy_keys=%(keys)s'
                        'where id =%(id)s;',
                        para)
                    self.connector.commit()
                    print para['database'] + 'database update operation success!'
                    self.logger.info(para['database'] + ' update successfully!')
                except psycopg2.Error as e:
                    self.logger.info(format(errorcodes.lookup(e.pgcode)))
                    self.connector.commit()
                    self.logger.info('failed to update ' + para['database'])