#-*-coding:utf-8-*-#
import datetime
import time
import os
import sys
import pandas as pd
from lib.db_connection import *

def add_stopcompany(word):
    db = mongodb_connection('news')
    count = db.stopcompanys.find({'name':word}).count()
    if count == 0:
        insert_time = time.strftime('%Y-%m-%d %H:%M:%S')
        db.stopcompanys.insert({'name':word,'time':insert_time})


if __name__ == '__main__':
    df = pd.read_excel('企业名称.xlsx')
    print(df.head(10))
    list1 = df['企业名称'].values.tolist()
    print(list1)
    for word in list1:
        add_stopcompany(word)


