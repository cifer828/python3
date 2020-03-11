#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/4/17 13:38
# @Author  : Cifer
# @File    : lda_ped.py

import pandas as pd
import matplotlib.pyplot as plt
import os
from sklearn.cluster import KMeans
from gensim.models.ldamodel import LdaModel
from gensim import corpora
import numpy as np
from sklearn.decomposition import PCA
from gensim.test.utils import datapath
from sklearn.metrics import silhouette_score
import math
import operator
import re
import datetime

class Lda_ped:
    def __init__(self):
        self.documents = []
        self.dictionary = {}
        self.corpus = []
        self.path_dir = 'C:\\Users\\zhqch\\Documents\\code\\Python3Projects\\visual_detection\\lda\\'
        self.conflict_df = []
        self.corpus = []
        self.documents = []
        self.lda = []
        self.doc_list = []
        self.topic_num = 1

    def load_data(self):
        self.conflict_df = pd.read_csv(self.path_dir + 'filter_conflicts.csv')

    def load_lda(self):
        # Load a potentially pretrained model from disk.
        self.load_data()
        self.create_corpus()
        self.lda = LdaModel.load(self.path_dir + "model")

    def create_data(self, filename):
        conflict_df = pd.read_csv(filename)
        # os.getcwd()
        # conflict_df.head()
        conflict_df = conflict_df.loc[conflict_df['PET'] > 0,:].loc[conflict_df['PET'] < 10,:]  # 去除异常值
        conflict_df['PET_level'] = pd.cut(conflict_df['PET'],[0,1,2,3,4,5,6,7,8,9,10], labels=[1,2,3,4,5,6,7,8,9,10])   # pet离散化
        # plt.plot(conflict_df['PET'])
        # 编码单词
        conflict_df['Word'] = conflict_df.apply(lambda x: str(x['Conflict_user'])+'_'+str(x['Vel_level']) +'_'+ str(x['Angle_level']) + '_'+str(x['PET_level']), axis =1)
        conflict_df['Conflict_code'] = conflict_df.apply(lambda x: str(x['Conflict_user']) + '_' + str(x['Ped_id']) + '_' + str(x['Conflict_id']), axis=1)
        self.conflict_df = conflict_df
        conflict_df.to_csv(self.path_dir + 'filter_conflicts.csv.csv', index=False)

    def create_corpus(self):
        s = self.conflict_df.groupby('Conflict_code')['Word'].apply(list)
        self.doc_list = s.index
        self.documents = [s[doc] for doc in self.doc_list]
        # corpus
        # 创建语料的词语词典，每个单独的词语都会被赋予一个索引
        self.dictionary = corpora.Dictionary(self.documents)
        # 使用上面的词典，将转换文档列表（语料）变成 DT 矩阵
        self.corpus = [self.dictionary.doc2bow(doc) for doc in self.documents]

    def train_lda(self, i):
        self.create_corpus()
        self.topic_num = i
        doc_num = len(self.doc_list)
        print('共训练%d篇文档，%d个主题' % (doc_num, self.topic_num))
        self.lda = LdaModel(corpus=self.corpus, id2word=self.dictionary, num_topics=self.topic_num, iterations=10000, alpha=0.01, eta=0.01,
                       minimum_probability=0.001,
                       update_every=1, chunksize=100, passes=1)
        # Save model to disk.
        temp_file = datapath(self.path_dir + "model")
        self.lda.save(temp_file)

    def perplexity(self):
        """calculate the perplexity of a lda-model"""
        testset = self.corpus[:40]
        print ('the info of this ldamodel: \n')
        print ('num of testset: %s; size_dictionary: %s; num of topics: %s'%(len(testset), len(self.dictionary), self.topic_num))

        prob_doc_sum = 0.0
        topic_word_list = [] # store the probablity of topic-word:[(u'business', 0.010020942661849608),(u'family', 0.0088027946271537413)...]
        for topic_id in range(self.topic_num):
            topic_word = self.lda.show_topic(topic_id, len(self.dictionary))
            dic = {}
            for word, probability in topic_word:
                dic[word] = probability
            topic_word_list.append(dic)
        doc_topics_ist = [] #store the doc-topic tuples:[(0, 0.0006211180124223594),(1, 0.0006211180124223594),...]
        for doc in testset:
            doc_topics_ist.append(self.lda.get_document_topics(doc, minimum_probability=0))
        testset_word_num = 0
        for i in range(len(testset)):
            prob_doc = 0.0 # the probablity of the doc
            doc = testset[i]
            doc_word_num = 0 # the num of words in the doc
            for word_id, num in doc:
                prob_word = 0.0 # the probablity of the word
                doc_word_num += num
                word = self.dictionary[word_id]
                for topic_id in range(self.topic_num):
                    # cal p(w) : p(w) = sumz(p(z)*p(w|z))
                    prob_topic = doc_topics_ist[i][topic_id][1]
                    prob_topic_word = topic_word_list[topic_id][word]
                    prob_word += prob_topic*prob_topic_word
                prob_doc += math.log(prob_word) # p(d) = sum(log(p(w)))
            prob_doc_sum += prob_doc
            testset_word_num += doc_word_num
        prep = math.exp(-prob_doc_sum/testset_word_num) # perplexity = exp(-sum(p(d)/sum(Nd))
        print ("the perplexity of this ldamodel is : %s"%prep)
        return prep

    def perplexity_curve(self, num):
        # 寻找最优主题数
        ppl = []
        for i in range(1, num):
            self.train_lda(i)
            ppl.append(self.perplexity())
        plt.plot(range(1,num), ppl)

    def topic_distribute(self):
        # 主题分布
        # print('***************************所有文档主题分布***************************')
        doc_topics = self.lda.get_document_topics(self.corpus)
        doc2topic_file = 'visual_detection//lda//doc2topic.csv'
        # with open(doc2topic_file, 'w') as f:
        #     f.write('***************************Topic distribution for each document***************************\n')

        topic_list = []
        # 输出每个文档的主题分布
        for doc_num, topic in enumerate(doc_topics):
            one_doc_topic = [0 for _ in range(self.topic_num)]
            for topic_no, topic_probability in topic:
                one_doc_topic[topic_no] = topic_probability
            topic_list.append(one_doc_topic)
        topic_df = pd.DataFrame(topic_list, index=self.doc_list)
        topic_df.columns = ['Topic %d' % num for num in topic_df.columns]

        cluster_model = KMeans(n_clusters = 2, n_jobs = 1, max_iter = 1000)
        cluster_model.fit(topic_list)
        topic_df['cluster'] = cluster_model.labels_
        topic_df.to_csv(doc2topic_file, index_label='Conflict')

    def predict_doc(self, text_idx):
        """预测新doc的topic"""
        new_text = self.documents[text_idx]
        result = np.zeros((4, len(new_text)))
        for i in range(len(new_text)):
            text_piece = new_text[:i+1]
            new_doc = self.dictionary.doc2bow(text_piece)
            vector = self.lda[new_doc]
            if new_text[0][0] == '1':
                mat = np.array([[-0.23,0,-0.32,0.76,0,-0.24,0,0.42,0,-0.24,0,-0.22],
                                [-0.41,0,-0.87,-0.02,0,-0.23,0,-0.05,0,-0.25,0,0.21],
                                [-0.04,0,0.7,0.01,0,-0.06,0,-0.37,0,0.85,0,0.03],
                                [0.16,0,0.03,0.1,0,-0.84,0,-0.46,0,-0.22,0,0.2]])
            else:
                mat = np.array([[0, -0.1, 0, -0.21, 0.31, 0, 0.81, 0, -0.13, 0, 0.36, 0],
                                 [0, 0.03, 0, 0.09, 0.08, 0, 0.91, 0, 0.03, 0, 0.47, 0],
                                 [0, 0.82, 0, -0.38, -0.07, 0, -0.22, 0, 0.1, 0, 0.29, 0],
                                 [0, 0.55, 0, 0.74, 0.11, 0, 0.15, 0, -0.1, 0, -0.28, 0]])
            new_topic = np.zeros((12,1))
            for tp_idx, tp_prob in vector:
                new_topic[tp_idx] = tp_prob
            result[:,i] = np.dot(mat, new_topic)[:,0]
        return new_text, result

    def predict_batch(self, num):
        conflict_list = []
        feature_list = []
        for i in range(0, num):
            print('Predict %d conflict' % i)
            conflict, feature = lda_model.predict_doc(i)
            conflict_list.append(conflict)
            feature_list += feature.tolist()
        conflict_df = pd.DataFrame(conflict_list)
        feature_df = pd.DataFrame(feature_list)
        conflict_df.to_csv(self.path_dir + 'conflict_list.csv', index=False, header=None)
        feature_df.to_csv(self.path_dir + 'feature_list.csv', index=False, header=None)

    def word_distribute(self):
        doc_topics = self.lda.get_document_topics(self.corpus)
        doc2topic_file = self.path_dir + 'doc2topic.csv'
        topic_list = []
        # 输出每个文档的主题分布
        for doc_num, topic in enumerate(doc_topics):
            one_doc_topic = [0 for _ in range(self.topic_num)]
            for topic_no, topic_probability in topic:
                one_doc_topic[topic_no] = topic_probability
            topic_list.append(one_doc_topic)
        topic_df = pd.DataFrame(topic_list, index=self.doc_list)
        topic_df.columns = ['Topic %d' % num for num in topic_df.columns]
        topic_df.to_csv(doc2topic_file, index_label='Conflict')

def pca_doc():
    doc2topic_df = pd.read_csv('doc2topic.csv')
    conflict = doc2topic_df['Conflict']
    doc2topic_df.drop(['cluster'], axis=1,inplace=True)
    doc2topic_df['Conflict'] = doc2topic_df['Conflict'].apply(lambda x: int(x[0]))
    # # 交换列
    # mid = doc2topic_df['Topic 10']
    # doc2topic_df.drop(labels=['Topic 10'], axis=1, inplace=True)
    # doc2topic_df.insert(0, 'Topic 10', mid)
    df_v = doc2topic_df.loc[doc2topic_df['Conflict']==2].iloc[:, [1,3,4,5,6,8,11]]
    df_b = doc2topic_df.loc[doc2topic_df['Conflict']==1].iloc[:,[2,4,7,9,10,12]]

    pca_v = pca_train(4, df_v)
    pca_b = pca_train(4, df_b)
    pca_all = pca_train(7, doc2topic_df)

    kmeans_model_v = KMeans(n_clusters=2).fit(pca_v)  # 训练模型
    print(kmeans_model_v.cluster_centers_)

    kmeans_model_b = KMeans(n_clusters=2).fit(pca_b)  # 训练模型
    print(kmeans_model_b.cluster_centers_)

    # 轮廓系数法确定聚类k值
    # sc_scores=[]
    # for t in range(2,10):
    #     kmeans_model = KMeans(n_clusters=t).fit(pca_b)  # 训练模型
    #     sc_score = silhouette_score(pca_b, kmeans_model.labels_, metric='euclidean')
    #     sc_scores.append(round(sc_score,2))
    # plt.figure()
    # plt.plot(range(2,10), sc_scores, '*-')
    # plt.xlabel('Number of Clusters')
    # plt.ylabel('Silhouette Coefficient Score')
    # plt.show()
    # print(sc_scores)


def pca_train(pca_n, df):
    """
    :param pca_n: 目标维度
    :param df: 原数据
    :return: 降维后数据.values==True
    """
    print(df.shape)
    pca = PCA(pca_n)
    pca.fit(df)
    cov = pca.get_covariance()  # 协方差矩阵
    eig_val, eig_vect = np.linalg.eig(cov)
    np.set_printoptions(suppress=True, precision=2) # 取消科学计数，保留两位小数
    print('特征值：\n', eig_val.real)
    print('特征向量：\n', eig_vect[:pca_n].real)
    print('累计方差贡献：\n', pca.explained_variance_ratio_.cumsum())
    print(pca.explained_variance_ratio_)
    return pca.fit_transform(df)




if __name__ == "__main__":
    # pca_doc()
    lda_model = Lda_ped()
    # lda_model.create_data('all_conflicts.csv')
    # lda_model.load_data()
    # lda_model.train_lda(12)
    # lda_model.word_distribute()
    # lda_model.topic_distribte()
    # lda_model.perplexity_curve

    lda_model.load_lda()
    lda_model.predict_batch(4700)

