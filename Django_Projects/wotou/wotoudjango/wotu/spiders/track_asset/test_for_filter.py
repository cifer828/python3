from wotu.spiders.track_asset.spider_tianyancha import search_company
from wotu.spiders.track_asset.spider_tianyancha import filter_company
from wotu.config.config import MONGO_SERVER
from wotu.config.config import MONGO_PORT
import pymongo

if __name__ == '__main__':

    CONN = pymongo.MongoClient(MONGO_SERVER, MONGO_PORT)
    db = CONN['company']
    collection = db['investment_company']

    company_id_list=[]

    raw_company_list = collection.find({}, {'公司列表': 1})
    for i in raw_company_list:
        for j in i['公司列表']:
            company_id_list.append(j.id)


    black_list = []
    with open('./wrong_company', 'r') as f:
        for l in f.readlines():
            black_list.append(l.strip())
    collection = db['raw_company']
    for i in company_id_list:
        detail = collection.find_one({"_id":i})
        if detail['公司名称'] in black_list:
            continue
        # print(i,filter_company(detail))
        if filter_company(detail) == 1:
            print(detail['公司名称'])
