#-*- coding:utf-8 -*-#
import pandas as pd
import jieba
import pymysql
import sys
#from gensim import corpora, models
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
import lda
import numpy as np
from gensim.corpora import Dictionary
from gensim.models import LdaModel
import os
import datetime
import json
import jieba.posseg as pseg


# reload(sys)
# sys.setdefaultencoding('utf8')


def modify_time(og_time):
    time_list = og_time.split('-')
    new_time = time_list[0] + '-'
    if len(time_list[1]) == 1:
        new_time += ('0' + time_list[1] + '-')
    else:
        new_time += (time_list[1] + '-')
    if len(time_list[2]) == 1:
        new_time += ('0' + time_list[2])
    else:
        new_time += (time_list[2])
    return new_time

def lda1(num_topics=10):
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    print(dirname)
    f = open(os.path.join(dirname,'stopword.txt'))
    stopwords = [single_word.strip() for single_word in f.read().split('\n')]
    train_set=[]
    print (stopwords)
    conn=pymysql.Connect(host='106.75.65.56',user='root',passwd='wotou',charset='utf8',db='news')
    end_time = datetime.datetime.now()
    end_day = modify_time('-'.join([str(end_time.year), str(end_time.month), str(end_time.day)]))
    #df=pd.read_sql('select * from bioon where spidertime="'+end_day+'"',conn)
    df = pd.read_sql('select * from bioon limit 10',conn)
    add_stop_list=['',' ','\r\n']
    #rint df.head(10)

    content_list=df['content'].values.tolist()
    for t in content_list:
        word_list = list([x for x in list(jieba.cut(t,cut_all=True))])
        word_list = [x for x in word_list if x not in stopwords]

        word_list = [x for x in word_list if x not in add_stop_list]
        train_set.append(word_list)

        #train_set.append([x for x in list(jieba.cut(t, cut_all=False)) if x not in stopwords])

    print((train_set[0]))
    count = len(train_set)
    # count_Vector = CountVectorizer()
    #
    # X = count_Vector.fit_transform(train_set).toarray()
    # vocab = count_Vector.vocabulary_
    # print vocab
    #
    # model = lda.LDA(n_topics=10, n_iter=100, random_state=1)
    # model.fit(X)
    dictionary = Dictionary(train_set)
    corpus = [dictionary.doc2bow(text) for text in train_set]

    # lda模型训练
    lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics,iterations=10000)
    topic_word=dict()
    for i in range(10):
        topic_word[i]=[]
        topic_word_tuple = lda.show_topic(i)
        for t in range(len(topic_word_tuple)):
            topic_word[i].append(topic_word_tuple[t][0])
    f = open('LDA.txt', 'w+')
    json.dump(topic_word, f, ensure_ascii=False, indent=4)
    return count,topic_word

#进行词性过滤
def lda2(num_topics=10):
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    print(dirname)
    f = open(os.path.join(dirname,'stopword.txt'))
    stopwords = [single_word.strip() for single_word in f.read().split('\n')]
    train_set=[]
    print (stopwords)
    conn=pymysql.Connect(host='106.75.65.56',user='root',passwd='wotou',charset='utf8',db='news')
    end_time = datetime.datetime.now()
    end_day = modify_time('-'.join([str(end_time.year), str(end_time.month), str(end_time.day)]))
    #df=pd.read_sql('select * from bioon where spidertime="'+end_day+'"',conn)
    df = pd.read_sql('select * from bioon limit 100',conn)
    add_stop_list=['',' ','\r\n']
    #rint df.head(10)

    content_list=df['content'].values.tolist()
    for t in content_list:
        words = pseg.cut(t)
        word_list=[]
        for w in words:
            if w.flag=='n':
                word_list.append(w.word)
        #print word_list
        #word_list = list([x for x in list(jieba.cut(t,cut_all=True))])
        word_list = [x for x in word_list if x not in stopwords]

        word_list = [x for x in word_list if x not in add_stop_list]
        train_set.append(word_list)

        #train_set.append([x for x in list(jieba.cut(t, cut_all=False)) if x not in stopwords])

    #print (train_set[0])
    count = len(train_set)
    # count_Vector = CountVectorizer()
    #
    # X = count_Vector.fit_transform(train_set).toarray()
    # vocab = count_Vector.vocabulary_
    # print vocab
    #
    # model = lda.LDA(n_topics=10, n_iter=100, random_state=1)
    # model.fit(X)
    dictionary = Dictionary(train_set)
    print(dictionary)
    corpus = [dictionary.doc2bow(text) for text in train_set]

    # lda模型训练
    lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics,iterations=10000)
    topic_word=dict()
    for i in range(10):
        topic_word[i]=[]
        topic_word_tuple = lda.show_topic(i)
        for t in range(len(topic_word_tuple)):
            topic_word[i].append(topic_word_tuple[t][0])
    f = open('LDA.txt', 'w+')
    json.dump(topic_word, f, ensure_ascii=False, indent=4)
    return count,topic_word


#count,topic_word = lda2()






