# -*- coding:utf-8-*-#
import pymysql
import nltk
import re
import jieba
import json
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import pandas as pd
# 创建连接
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='0845', db='searchreport', charset='utf8')
# 创建游标
cur = conn.cursor()

# 执行SQL，并返回收影响行数
effect_row = cur.execute('select content from sina where type="生物医药行业"')
results=cur.fetchall()
pattern=re.compile(r'\s+')
print (effect_row)
f=open(u'sougou/sougou_生物医药.json')
words=json.load(f)
print (words)
f1=open('structrue_word.txt')

weight0=f1.read().split(',')
weight1=[u'生物医药']
weight2=[]
weight3=[]
for key,value in words[u'生物医药'].items():
    weight2.extend(value)

for word in weight2:
    for key,value in words[word].items():
        weight3.extend(value)

print (weight0)
print (weight1)
print (weight2)
print (weight3)

f=open('result.txt','w+')

for one in results:
    content=one[0]
    content=re.sub(pattern,'.',content)
    tr4s = TextRank4Sentence()

    # 使用词性过滤，文本小写，使用words_all_filters生成句子之间的相似性
    tr4s.analyze(text=content, lower=True, source='all_filters')
    score=[]
    cixu=[]
    i=1
    for sentence in tr4s.sentences:
        cixu.append(i)
        i+=1
        seg_list = jieba.cut(sentence, cut_all=True)
        onescore=0
        for oneword in seg_list:
            if oneword in weight1:
                onescore+=1
            elif oneword in weight2:
                onescore+=0.8
            elif oneword in weight3:
                onescore+=0.6
        score.append(onescore)

    sen_score=list(zip(tr4s.sentences,score,cixu))

    sen_score=sorted(sen_score,key=lambda item:item[1],reverse=True)

    top3=sen_score[:3]
    top3=sorted(top3,key=lambda item:item[2])
    f.write(u'摘要-textrank:\n')
    f.write('\n'.join(pd.DataFrame(tr4s.get_key_sentences(num=3))['sentence'].values.tolist()) + '\n\n\n\n')
    output=[]
    f.write(u'原文\n\n\n')
    f.write(content+'\n\n\n')
    f.write(u'摘要-使用词谱\n\n')


    for x,y,z in top3:
        output.append(x)
        f.write(x+'\n')
    f.write('\n')
    print (output)

f.close()




    #print (content)


