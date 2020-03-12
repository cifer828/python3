import jieba
from gensim.corpora import Dictionary
from gensim.models import LdaModel, TfidfModel, word2vec
import numpy as np
import operator
import re
import datetime

def weibo_seg():
    # 清洗微博并分词
    raw_weibo = [line for line in open('result.csv')][1: ]
    result = []
    f = open('cleaned.txt', 'w')
    idx = 0
    for weibo in raw_weibo:
        tag_pattern = re.compile('^[\d]+,|<[^>]+>|,[^,]+$')
        # 去起始数字编号| <tag> | 结尾时间
        cleaned_weibo = re.sub(tag_pattern, '', weibo)
        f.write(str(idx) + '.')
        f.write(cleaned_weibo + '\n')
        idx += 1
        stopwords = [line for line in open('stopword.txt', encoding='utf8').read().split()]
        words = jieba.cut(cleaned_weibo, cut_all=False)   # 精准分词
        result.append([word.encode('utf8') for word in words if word not in stopwords and word.strip() != '' and not word.isdigit()])
    with open('segment.txt', 'w') as f:
        line = 0
        for sentence in result:
            if sentence == []:
                line += 1
                continue
            f.write(str(line) + '.')
            for word in sentence:
                f.write(word.decode('utf8') + ' ')
            f.write('\n')
            line += 1
    return result

def seg(num):
    # 结巴分词
    result = []
    for idx in range(num):
        stopwords = [line for line in open('stopword.txt', encoding='utf8').read().split()]
        content = open("C000008/%d.txt" % (idx + 10,) , "r").read()
        # print(content)
        words = jieba.cut(content, cut_all=False)   # 精准分词
        result.append([word.encode('utf8') for word in words if word not in stopwords and word.strip() != '' and not word.isdigit()])
    return result

def lda(train_set, topic_num):
    # print(len(train_set))
    # train_set = [[tr.encode('utf8') for tr in train_set]]
    # print([i.decode('utf8') for i in train_set])

    # 语料准备
    dictionary = Dictionary(train_set)
    doc_num = len(train_set)
    corpus = [dictionary.doc2bow(text) for text in train_set]
    corpus_tfidf = TfidfModel(corpus)[corpus]

    # lda训练
    lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=topic_num, iterations=10000,  alpha=0.01, eta=0.01, minimum_probability=0.001,
                            update_every = 1, chunksize = 100, passes = 1)
    print('共训练%d篇文档，%d个主题' % (doc_num, topic_num))

    # 主题分布
    # print('***************************每个主题排名前十篇微博的主题分布***************************')
    doc_topics = lda.get_document_topics(corpus)
    topic_nums = np.arange(topic_num)
    time_now = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    with open('lda_results/%s.txt' % time_now , 'w') as f:
        f.write('***************************随机十篇微博的主题分布***************************\n')
    # 输出每个主题排名前十的文档的主题分布
    for topic_idx in topic_nums:
        docs_in_topic = []  # 拥有该主题的所有doc
        for doc_idx in range(doc_num):
            for topic in doc_topics[doc_idx]:
                if topic[0] == topic_idx:
                    docs_in_topic.append([doc_idx, topic[1]])   # [文档id， 主题在该文档的占比]
        docs_sorted = sorted(docs_in_topic, key = operator.itemgetter(1), reverse = True)
        with open('lda_results/%s.txt' % time_now , 'a') as f:
            temp_writing = '第%d个主题的排名前20个文档：\n' % topic_idx
            for d in docs_sorted[:21]:
                topic_in_d = doc_topics[d[0]]
                topic_sorted = sorted(topic_in_d, key = operator.itemgetter(1), reverse = True)
                temp_writing += '第%d个文档的主题分布：' % (d[0], ) + '\n'
                for item in topic_sorted:
                    temp_writing += '{:>8d}'.format(item[0])
                temp_writing += '\n'
                for item in topic_sorted[:10]:
                   temp_writing += '{:>8.4f}'.format(item[1])
                temp_writing += '\n'
            f.write(temp_writing)
        # print('第%d个文档的前%d个主题：' % (doc_id, 10), [item[0] for item in topic_sorted[:10]])
        # print( [item[1] for item in topic_sorted[:10]])

    # 单词分布
    print('***************************所有主题的单词分布***************************')
    with open('lda_results/%s.txt' % time_now , 'a') as f:
        f.write('***************************所有主题的单词分布***************************\n')
    for topic_id in range(topic_num):
        term_distribute_all = lda.get_topic_terms(topicid=topic_id)
        term_distribute = term_distribute_all
        term_distribute = np.array(term_distribute)
        term_id = term_distribute[:, 0].astype(np.int)
        with open('lda_results/%s.txt' % time_now , 'a') as f:
            temp_writing = ''
            temp_writing += '\n主题#%d：\t' % topic_id + '\n'
            temp_writing += '词：\t'
            for t in term_id:
                temp_writing += dictionary.id2token[t] + '\t'
            temp_writing += '\n概率：\t'
            for td in term_distribute:
                temp_writing += '{:>8.4f}'.format(td[1])
            f.write(temp_writing)
        # print('主题#%d：\t' % topic_id)
        # print('词：\t',end = ' ')
        # for t in term_id:
        #     print(dictionary.id2token[t],end = ' ')
        # print('\n概率：\t', term_distribute[:, 1])

def weibo_word2vec(train_set):
    sentences = []
    for sent in train_set:
        sentences.append([word.decode('utf8') for word in sent])
    model = word2vec.Word2Vec(sentences, size=200, min_count=1)  #训练skip-gram模型，默认window=5

    # 计算两个词的相似度/相关程度
    y1 = model.similarity("百度", "小米")
    print("【百度】和【小米】的相似度为：", y1)

    # 计算某个词的相关词列表
    y2 = model.most_similar("事故", topn=20)  # 20个最相关的
    print("和【事故】最相关的词有：\n")
    for item in y2:
        print(item[0], item[1])

    # # 寻找对应关系
    # print("书-不错，质量-")
    # y3 =model.most_similar(['质量', '不错'], ['书'], topn=3)
    # for item in y3:
    #     print(item[0], item[1])
    #
    # # 寻找不合群的词
    # y4 =model.doesnt_match("书 书籍 教材 很".split())
    # print("不合群的词：", y4)

    # 保存模型，以便重用
    # model.save(u"书评.model")
    # 对应的加载方式
    # model_2 =word2vec.Word2Vec.load("text8.model")

# weibo_word2vec(weibo_seg())
lda(weibo_seg(), topic_num= 10)
# weibo_seg()
# print('{:>8d}'.format(12))


