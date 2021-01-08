import codecs
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import MySQLdb
import pandas as pd
import pymongo


f=open('test_result.txt','wb+')
CONN = pymongo.MongoClient('106.75.65.56', 27017)
db=CONN['searchreport']
con = pymysql.connect(host='localhost', user='root', passwd='0845', db='searchreport', port=3306, charset='utf8')
cur = con.cursor()  # 获取一个游标
cur.execute('select content from sina where id<10')
result=cur.fetchall()
for one_text in result:
#text = codecs.open('./text/01.txt', 'r', 'utf-8').read()
    text=one_text[0]
    tr4w = TextRank4Keyword()  # 导入停止词
    f.write('原文：\n')
    print text
    f.write(text+'\n\n\n')

    #使用词性过滤，文本小写，窗口为2
    tr4w.analyze(text=text, lower=True, window=2)

    print '关键词：'
    # 20个关键词且每个的长度最小为1
    print '/'.join(pd.DataFrame(tr4w.get_keywords(20, word_min_len=1))['word'].values.tolist())

    print '关键短语：'
    # 20个关键词去构造短语，短语在原文本中出现次数最少为2
    print '/'.join(tr4w.get_keyphrases(keywords_num=20, min_occur_num= 2))

    tr4s = TextRank4Sentence()

    # 使用词性过滤，文本小写，使用words_all_filters生成句子之间的相似性
    tr4s.analyze(text=text,  lower=True, source = 'all_filters')

    print '摘要：'
    print '\n'.join(pd.DataFrame(tr4s.get_key_sentences(num=3))['sentence'].values.tolist()) # 重要性最高的三个句子
    f.write('摘要：\n')
    f.write('\n'.join(pd.DataFrame(tr4s.get_key_sentences(num=3))['sentence'].values.tolist())+'\n\n\n\n')