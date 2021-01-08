#-*- coding:utf-8-*-#
import gensim
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import pandas as pd
import gensim.models.word2vec as w2v
from goose import Goose
from goose.text import StopWordsChinese
import sys
import jieba

from spiders.baidu_new_spider import baidu_news_search,search_one_new

"""得到需要搜索的企业列表"""
def get_company():
    company_list=[('信宇科技',1),('天智航',2),('冠新软件',3),('振威展览',4),('怡文环境',5)]
    #company_df = pd.read_csv('100企业&官网.csv',encoding='gbk',index_col=None)
    #print company_df.info()
    company_df =pd.DataFrame(company_list,columns=['name','url'])
    return company_df

"""对语料进行分句"""
def get_sentence(content):
    tr4s = TextRank4Sentence()
    print(len(content))

    # 使用词性过滤，文本小写，使用words_all_filters生成句子之间的相似性
    tr4s.analyze(text=content, lower=True, source='all_filters')
    #返回的是list，list中每一项是一个字典，包含index，weight和sentence三个字段
    #sen_list = tr4s.get_key_sentences()
    return tr4s.sentences
    # for item in sen_list:
    #     if word in item['sentence']:
    #         item['weight'] *= 2
    # sen_list.sort(key=lambda x:x['weight'],reverse=True)
    # print sen_list




"""计算word2vec相似词"""
def get_word2vec_result(sentences,word):
    try:
        sentences = w2v.LineSentence(sentences)
        model = w2v.Word2Vec(sentences, size=100, window=5, min_count=5, workers=4)
        print('相似词')
        print(model.similar_by_word(word))
    except Exception as e:
        print(e.args)
        return

def main():
    f=open('abstarct.txt','wb')
    searchlist=['融资','投资','并购','上市']
    company_df = get_company()
    #for i in range(5):
    for i in range(len(company_df)):

        company_name = company_df.iloc[i,0]
        f.write(company_name+'\n')
        urls=[]
        company_url = company_df.iloc[i,1]
        for word in searchlist:
            f.write(word+'\n')
            print(company_name+' '+word)
            query = company_name+' '+word
            totalcontent = ''
            news_list = baidu_news_search(query,news_cnt=10)
            for single_new in news_list:
                title = single_new[1]
                #print title
                time = single_new[0]
                href=single_new[3]
                if href not in urls:
                    urls.append(href)
                    #content = search_one_new(href)
                    #print content
                    #f.write(content)
                    f.write('\n\n')
                    #使用goose得到新闻文本
                    g=Goose({'stopwords_class': StopWordsChinese})
                    content = g.extract(url=href)

                    totalcontent+=content.cleaned_text+'\n'
            sentences=get_sentence(totalcontent)

            sentences_cut = '\n'.join([ ])
            #print sentences_cut
           # print type(sentences_cut)
           # print type(word.decode('utf-8'))
            print(word.decode('utf-8') in sentences_cut)
            with open('test.txt','w') as f1:
                for sentence in sentences:
                    f1.write(' '.join(list(jieba.cut(sentence, cut_all=False))))
                    f1.write('\n')

            get_word2vec_result('test.txt',word.decode('utf-8'))
            #f.write(abstract+'\n')

            f.write(sentences_cut)
            f.write('\n')
#
        f.write('\n')
    f.write('\n\n')




        #print company_name,company_url





if __name__ == '__main__':
    main()