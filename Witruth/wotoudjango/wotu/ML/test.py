import pymongo
import pandas as pd
conn = pymongo.MongoClient('106.75.65.56',27017)
database = conn['news']
items = pd.DataFrame([item for item in database.shengwugu.find()])
print (items.head(10))