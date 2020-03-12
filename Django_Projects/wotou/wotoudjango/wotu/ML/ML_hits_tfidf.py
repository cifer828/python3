#coding:utf-8
"""hits算法和tfidf相结合"""

from math import sqrt
import os
import sys
import digraph
import pymysql
import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import jieba


class HITSIterator:
    __doc__ = '''计算一张图中的hub,authority值'''

    def __init__(self, dg,tfidf):
        self.max_iterations = 100  # 最大迭代次数
        self.min_delta = 0.0001  # 确定迭代是否结束的参数
        self.graph = dg

        self.hub = {}
        self.authority = {}
        #print tfidf.keys()
        for node in self.graph.nodes():
            """根据tfidf值初始化authority和hub"""
            self.hub[node] = tfidf[node]
            self.authority[node] = tfidf[node]

    def hits(self):
        """
        计算每个页面的hub,authority值
        :return:
        """
        if not self.graph:
            return

        flag = False
        for i in range(self.max_iterations):
            change = 0.0  # 记录每轮的变化值
            norm = 0  # 标准化系数
            tmp = {}
            # 计算每个页面的authority值
            tmp = self.authority.copy()
            for node in self.graph.nodes():
                self.authority[node] = 0
                for incident_page in self.graph.incidents(node):  # 遍历所有“入射”的页面
                    self.authority[node] += self.hub[incident_page]
                norm += pow(self.authority[node], 2)
            # 标准化
            norm = sqrt(norm)
            for node in self.graph.nodes():
                self.authority[node] /= norm
                change += abs(tmp[node] - self.authority[node])

            # 计算每个页面的hub值
            norm = 0
            tmp = self.hub.copy()
            for node in self.graph.nodes():
                self.hub[node] = 0
                for neighbor_page in self.graph.neighbors(node):  # 遍历所有“出射”的页面
                    self.hub[node] += self.authority[neighbor_page]
                norm += pow(self.hub[node], 2)
            # 标准化
            norm = sqrt(norm)
            for node in self.graph.nodes():
                self.hub[node] /= norm
                change += abs(tmp[node] - self.hub[node])

            print(("This is NO.%s iteration" % (i + 1)))
            #print("authority", self.authority)
            #print("hub", self.hub)

            if change < self.min_delta:
                flag = True
                break
        if flag:
            print(("finished in %s iterations!" % (i + 1)))
        else:
            print("finished out of 100 iterations!")

        return list(self.authority.items())
        #print("The best authority page: ", max(self.authority.items(), key=lambda x: x[1]))
        #print("The best hub page: ", max(self.hub.items(), key=lambda x: x[1]))

def tf_idf_cal():
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
    print(dirname)
    f = open(os.path.join(dirname,'stopword.txt'))
    stopwords = [single_word.strip() for single_word in f.read().split('\n')]
    train_set=[]
    nojoin_train_set = []
    print (stopwords)
    conn=pymysql.Connect(host='106.75.65.56',user='root',passwd='wotou',charset='utf8',db='news')
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
        nojoin_train_set.append(word_list)
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
        tfidf_list.append([content_list[i],nojoin_train_set[i],one_tfidf_dict])

    return tfidf_list

def create_graph(seq_list,tfidf):
    seq_list = [x.lower() for x in seq_list]
    nodes = list(set(tfidf.keys()))
    dg = digraph()
    edges= []
    dg.add_nodes(nodes)
    for i in range(len(seq_list)-1):
        if (seq_list[i] in nodes) and (seq_list[i+1] in nodes):
            if (seq_list[i],seq_list[i+1]) in edges:
                continue
            else:
                edges.append((seq_list[i],seq_list[i+1]))
                dg.add_edge((seq_list[i],seq_list[i+1]))

    return dg

def start():
    tfidf_list = tf_idf_cal()
    f = open('tfidf_hits.txt', 'wb')
    for i in range(len(tfidf_list)):
        content = tfidf_list[i][1]
        tfidf = tfidf_list[i][2]
        dg = create_graph(content,tfidf)
        hits = HITSIterator(dg,tfidf)
        authority = hits.hits()
        #print authority

        authority.sort(key=lambda x:x[1],reverse=True)
        print(authority[:10])
        f.write('原文' + str(i) + ':\n')
        f.write(tfidf_list[i][0] + '\n\n\n')
        f.write('关键词' + str(i) + ':\n')
        for t in range(10):
            f.write(authority[t][0]+'/')
        f.write('\n\n\n')
    f.close()





#if __name__ == '__main__':
    # dg = digraph()
    #
    # dg.add_nodes(["A", "B", "C", "D", "E"])
    #
    # dg.add_edge(("A", "C"))
    # dg.add_edge(("A", "D"))
    # dg.add_edge(("B", "D"))
    # dg.add_edge(("C", "E"))
    # dg.add_edge(("D", "E"))
    # dg.add_edge(("B", "E"))
    # dg.add_edge(("E", "A"))
    #start()
