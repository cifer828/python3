#-*-coding:utf-8-*-#
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import pandas as pd
import pymongo
def textrank():
    f=open('test_result.txt','wb+')
    CONN = pymongo.MongoClient('106.75.65.56', 27017)
    db=CONN['news']
    collection=db['bioon']
    result=[item['content'] for item in collection.find()][:100]
    for one_text in result:
        try:
            #text = codecs.open('./text/01.txt', 'r', 'utf-8').read()
            text=one_text[0]
            tr4w = TextRank4Keyword()  # 导入停止词
            f.write('原文：\n')

            f.write(text+'\n\n\n')
    
            #使用词性过滤，文本小写，窗口为2
            tr4w.analyze(text=text, lower=True, window=2)

            print('关键词：')
            # 20个关键词且每个的长度最小为1
            print('/'.join(pd.DataFrame(tr4w.get_keywords(20, word_min_len=1))['word'].values.tolist()))
            f.write('/'.join(pd.DataFrame(tr4w.get_keywords(20, word_min_len=1))['word'].values.tolist())+'\n\n\n\n')

            print('关键短语：')
            # 20个关键词去构造短语，短语在原文本中出现次数最少为2
            print('/'.join(tr4w.get_keyphrases(keywords_num=20, min_occur_num= 2)))
            f.write('/'.join(tr4w.get_keyphrases(keywords_num=20, min_occur_num= 2))+'\n\n\n')
        except:
            pass