from wotu.config.config import MONGO_SERVER
from wotu.config.config import MONGO_PORT
import pymongo
from wotu.spiders.track_asset.spider_tianyancha import search_company
from bson.dbref import DBRef

if __name__ == '__main__':

    CONN = pymongo.MongoClient(MONGO_SERVER, MONGO_PORT)
    wrong_company_file=open('./wrong_company','w')
    company_name=''
    with open('./whitelist_industry.txt', 'r') as f:
        for l in f.readlines():
            if l.find("name") > -1:
                try:
                    company_name = l.replace('"name" : "', "").replace('",', "").strip()
                    detail = search_company(company_name)
                    db = CONN['company']
                    collection = db['filtered_company']
                    result = {}
                    result['from'] = "origin"
                    result['company'] = DBRef("raw_company", detail['_id'])
                    collection.insert(result)
                except Exception as e:
                    wrong_company_file.write(company_name)
                    wrong_company_file.write(";")
