#coding:utf-8
"""
使用TF-IDF爬取关键词
使用每篇文章的关键词进行两两组合，判断是否在佰腾网中有相应的专利

返回

"""
import jieba
import jieba.posseg as pseg

import os
import sys
import pandas as pd
import numpy as np
import urllib.request, urllib.parse, urllib.error
import requests
import lxml.html
import re
import time
import xlwt
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from lib.db_connection import *
from spiders.baiteng.baiteng import baiteng_search

db = mongodb_connection('news')

def write_to_excel(info_dict):
    f = xlwt.Workbook()
    for index,value in list(info_dict.items()):
        sheet1 = f.add_sheet('sheet'+str(index), cell_overwrite_ok=True)
        sheet1.write(0,0,'原文')
        sheet1.write(0,1,value['content'])
        sheet1.write(1,0,'关键词')
        sheet1.write(1,1,value['keyword'])
        sheet1.write(2, 0, '词组:')
        row=3

        for item in value['company']:
            col = 2
            sheet1.write(row,0,item[0])
            sheet1.write(row,1,str(item[1]))
            for company in item[2]:
                sheet1.write(row,col,company[1]+' : '+company[0])
                col+=1
            row+=1
    f.save('过滤后.xls')

def get_stopwords():
    """得到停用词表"""
    return [item['stopword'] for item in db.stopwords.find()]

def get_article():
    """得到文章信息"""
    return [item for item in db.shengwugu.find()]

def get_train_set(df):
    """得到训练集，训练集中的一条记录是经过分词之后再合并的字符串
    返回四个list:
    content_list：文章正文列表
    title_list：文章标题列表
    train_set: 训练集，用于计算tfidf
    title_train_set：标题分词列表，用于对标题词增加权重
    """
    train_set = []
    title_train_set = []
    stopwords = get_stopwords()
    pattern = re.compile(r'^[a-zA-Z]+$')
    # 过滤掉原文中原文出处及后面的部分
    pattern1 = re.compile(r'原文出处')
    content_list = [item['content'] for item in db.shengwugu.find()]
    title_list = [item['name'] for item in db.shengwugu.find()]
    """分词并保存其中的名词或者英文单词"""
    for t in content_list:
        match = pattern1.search(t)
        if match:
            t = t[:match.start()]
        words = pseg.cut(t)
        word_list = []
        for w in words:
            if w.flag == 'n':
                word_list.append(w.word)
            elif pattern.match(w.word):
                word_list.append(w.word)
        word_list = [x for x in word_list if x not in stopwords]
        train_set.append(' '.join(word_list))

    """分词并保存其中的名词或者英文单词"""
    for t in title_list:
        words = pseg.cut(t)
        title_word_list = []
        for w in words:
            if w.flag == 'n':
                title_word_list.append(w.word)
            elif pattern.match(w.word):
                title_word_list.append(w.word)
        word_list = [x for x in title_word_list if x not in stopwords]
        title_train_set.append(title_word_list)

    return title_list,title_train_set,content_list,train_set


def tf_idf_cal(content_train_set):
    """计算tfidf值
    返回词典以及每篇文章的tfidf值列表
    """
    vectorizer = CountVectorizer()  # 该类会将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频
    transformer = TfidfTransformer()  # 该类会统计每个词语的tf-idf权值
    tfidf = transformer.fit_transform(vectorizer.fit_transform(content_train_set))  # 第一个fit_transform是计算tf-idf，第二个fit_transform是将文本转为词频矩阵
    word = vectorizer.get_feature_names()  # 获取词袋模型中的所有词语
    weight = tfidf.toarray() # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重
    return word,weight

def main(limit=1000):

    df = pd.DataFrame(get_article())
    title_list,content_list,title_train_set,content_train_set  = get_train_set(df)
    pattern = re.compile(r'^[a-zA-Z]+$')

    word,weight = tf_idf_cal(content_train_set)

    insert_time = str(time.strftime('%Y-%m-%d'))
    info_dict = dict()

    for i in range(len(df.index)):  # 打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重

        info_dict[i] = dict()
        info_dict[i]['content'] = content_list[i]
        tfidf_list = []

        """对标题词以及英文词的权重进行扩大"""
        for j in range(len(word)):
            # print word[j], weight[i][j]
            weight1 = weight[i][j]
            if word[j] in title_train_set[i]:
                weight1 *= 2
            if pattern.match(word[j]):
                weight1 *= 1.5
            tfidf_list.append((word[j], weight1))

        """进行权重排序"""
        tfidf_list.sort(key=lambda x: x[1], reverse=True)


        keywords = []
        for t in range(10):
            # f.write(tfidf_list[t][0]+'/')
            keywords.append(tfidf_list[t][0])

        """关键词更新，插入mongodb"""
        id = df.ix[i, '_id']
        db.shengwugu.update({"_id": id}, {"$set": {"keyword": ' '.join(keywords)}})

        info_dict[i]['keyword'] = ' '.join(keywords)

        """俩俩组合搜索佰腾"""
        info_dict[i]['company'] = baiteng_search(keywords)
        print(info_dict[i]['company'])
        # write_to_excel(info_dict)


if __name__ == '__main__':
    for p in os.sys.path:
        print(p)
    main(300)

