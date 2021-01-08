#-*- coding:utf-8-*-#
import pymysql
import pymongo
from wotu.config.config import *


def mysql_connection(db):
    conn = pymysql.Connect(host=MYSQL_SERVER,port=MYSQL_PORT,user=MYSQL_USER,passwd=MYSQL_PASSWD,db=db,charset='utf8',)
    cur = conn.cursor()
    return conn,cur


def mongodb_connection(db):
    conn = pymongo.MongoClient(MONGO_SERVER, MONGO_PORT)
    database = conn[db]
    return database


def mysql_close_connection(conn):
    conn.close()


if __name__ == '__main__':
    mysql_connection()