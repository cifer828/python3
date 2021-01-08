"""
从数据库中读入rawcompany 数据
按企业初评表格式整理，写入excel中
"""
import pymongo
from wotu.config.config import MONGO_SERVER
from wotu.config.config import MONGO_PORT
import xlwt
import xlrd
CONN = pymongo.MongoClient(MONGO_SERVER, MONGO_PORT)
db = CONN['company']
collection = db['raw_company']
#创建工作表
def write_excel(keys,rawcompany):
    f = xlwt.Workbook(encoding='utf-8')  # 创建工作xls表
    sheet = f.add_sheet(u'sheet1', cell_overwrite_ok=True)  # 生成第一个工作表
    for i in range(len(keys)):
        sheet.write(0,i,keys[i])
    for i in range(1,len(rawcompany)+1):
        for j in range(len(keys)):
            sheet.write(i,j,str(rawcompany[i-1][keys[j]]))
    f.save('企业初评表.xls')
if __name__ == '__main__':
    rawcompany=[]
    keys = list(collection.find()[1].keys())
    for item in collection.find()[1:10]:
        rawcompany.append(item)
    write_excel(keys,rawcompany)