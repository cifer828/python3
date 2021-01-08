#-*-coding:utf-8-*-#
import datetime
import time
import os
import sys
import pymongo

from lib.db_connection import *

def add_stopword(word):
    db = mongodb_connection('news')
    count = db.stopwords.find({'stopword':word}).count()
    print(count)
    if count == 0:
        db.stopwords.insert({'stopword':word})





