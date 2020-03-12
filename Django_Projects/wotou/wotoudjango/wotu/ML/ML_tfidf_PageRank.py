# coding:utf-8
"""
作者：石晓文
内容：使用每个词的tfidf值，这个值作为pagerank的初始值计算词的重要性
版本：python2.7
"""
import numpy as np
import jieba
import os
import sys
import pymysql
import jieba.posseg as pseg
from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd


"""生成词列表和词典"""
def generate_word_list(text):
    word_list = list(jieba.cut(text,cut_all=False))

    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    f = open(os.path.join(dirname, 'stopword.txt'))
    stopwords = [single_word.strip() for single_word in f.read().split('\n')]
    add_stop_list = ['', ' ', '\r\n']
    word_list = [x for x in word_list if x not in stopwords]
    word_list = [x for x in word_list if x not in add_stop_list]

    distinct_word_list = list(set(word_list))

    # print len(word_list)
    # print len(distinct_word_list)
    # print len(word_list)
    # print len(distinct_word_list)
    distinct_word_dict = dict()

    for i in range(len(distinct_word_list)):
        #print type(distinct_word_list[i])
        distinct_word_dict[distinct_word_list[i]]=i

    return word_list,distinct_word_list,distinct_word_dict

"""生成转移矩阵"""
def generate_graph_matrix(text):
    word_list, distinct_word_list, distinct_word_dict = generate_word_list(text)
    graph = np.zeros((len(distinct_word_list), len(distinct_word_list)))
    for i in range(len(word_list) - 1):
        index1 = distinct_word_dict[word_list[i]]
        index2 = distinct_word_dict[word_list[i + 1]]
        graph[index1][index2] += 1
        graph[index2][index1] += 1

    b = np.transpose(graph)  # b为graph的转置矩阵
    c = np.zeros((graph.shape), dtype=float)
    for i in range(graph.shape[0]):
        for j in range(graph.shape[1]):
            c[i][j] = graph[i][j] / (b[j].sum())  # 完成初始化分配
    # print c,"\n===================================================="
    return c,distinct_word_list,distinct_word_dict


"""根据tfidf计算结果进行权威值初始化"""
def firstPr(c,init_value,word_dict):   #pr值得初始化
    pr = np.zeros((c.shape[0],1),dtype = float)  #构造一个存放pr值得矩阵
    for key, value in list(init_value.items()):
        if key in list(word_dict.keys()):
            index = word_dict[key]
            pr[index] = value
    #print pr,"\n==================================================="
    return pr



"""迭代计算权威值"""
def pageRank(p, m, v):  # 计算pageRank值
    t=0
    while ((v == p * np.dot(m, v) + (1 - p) * v).all() == False) and t<100:  # 判断pr矩阵是否收敛,(v == p*dot(m,v) + (1-p)*v).all()判断前后的pr矩阵是否相等，若相等则停止循环
        t+=1
        v = p * np.dot(m, v) + (1 - p) * v
        # print (v == p*dot(m,v) + (1-p)*v).all()
    return v


"""计算tfidf值"""
def tf_idf_cal():
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    print(dirname)
    f = open(os.path.join(dirname,'stopword.txt'))
    stopwords = [single_word.strip() for single_word in f.read().split('\n')]
    train_set=[]
    print (stopwords)
    conn=pymysql.Connect(host='106.75.65.56',user='root',passwd='wotou',charset='utf8',db='news')
    #end_time = datetime.datetime.now()
    #end_day = modify_time('-'.join([str(end_time.year), str(end_time.month), str(end_time.day)]))
    #df=pd.read_sql('select * from bioon where spidertime="'+end_day+'"',conn)
    df = pd.read_sql('select * from bioon',conn)
    add_stop_list=['',' ','\r\n']
    #rint df.head(10)

    content_list=df['content'].values.tolist()
    for t in content_list:
        # words = pseg.cut(t)
        # word_list=[]
        # for w in words:
        #     if w.flag=='n':
        #         word_list.append(w.word)
        #print word_list
        word_list = list([x for x in list(jieba.cut(t,cut_all=False))])
        word_list = [x for x in word_list if x not in stopwords]

        word_list = [x for x in word_list if x not in add_stop_list]
        train_set.append(' '.join(word_list))
    vectorizer = CountVectorizer()
    # 该类会将文本中的词语转换为词频矩阵，矩阵元素a[i][j] 表示j词在i类文本下的词频

    transformer = TfidfTransformer()  # 该类会统计每个词语的tf-idf权值

    tfidf = transformer.fit_transform(vectorizer.fit_transform(train_set))  # 第一个fit_transform是计算tf-idf，第二个fit_transform是将文本转为词频矩阵

    word = vectorizer.get_feature_names()  # 获取词袋模型中的所有词语

    weight = tfidf.toarray()  # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重

    f=open('tf_idf.txt','wb')
    tfidf_list=[]
    for i in range(50):  # 打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
        one_tfidf_dict = dict()
        print("-------这里输出第", i, "类文本的词语tf-idf权重------")
        for j in range(len(word)):
            #print word[j], weight[i][j]
            # if weight[i][j] > 0 :

            one_tfidf_dict[word[j]]=weight[i][j]
        tfidf_list.append([content_list[i],one_tfidf_dict])

    return tfidf_list




if __name__ == '__main__':

    tfidf_list = tf_idf_cal()
    f = open('tfidf_pagerank.txt', 'wb')
    #word_list, distinct_word_list, distinct_word_dict=generate_word_list(str)
    for t in range(len(tfidf_list)):
        if t == 9:
            continue
        c,word_list,word_dict = generate_graph_matrix(tfidf_list[t][0])
        pr = firstPr(c,tfidf_list[t][1],word_dict)
        p = 0.8  # 引入浏览当前网页的概率为p,假设p=0.8
        v = pageRank(p, c, pr)
        print(t)

        f.write('原文' + str(t) + ':\n')
        f.write(tfidf_list[t][0] + '\n\n\n')
        f.write('关键词' + str(t) + ':\n')

        #v_list = list(np.concatenate((word_list,v),axis=1))
        v_list = list(zip(word_list,list(np.array(v).reshape(-1))))
        #v_list = [list(x) for x in v_list]
        #print v_list
        v_list.sort(key=lambda x: x[1], reverse=True)
        for i in range(10):
            f.write(v_list[i][0]+'/')
        f.write('\n\n')
    f.close()




