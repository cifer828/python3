# -*- encoding=utf8 -*-
# from gensim.models.doc2vec import Doc2Vec,LabeledSentence,TaggedDocument
from 相似度计算.gen_vector import remove_stopwords
from pymongo import MongoClient
from gensim import corpora
from gensim.similarities import Similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import LSHForest
import jieba
import numpy as np


'''
目前的问题：fit_transform(all_doc)中
若传入的all_doc类型是list[list1[],list2[],···]则报错，list没有lower属性
若传入的all_doc类型是list[字符串1，字符串2，···],则可以运行，但结果明显错误
'''
# 数据库连接，baiteng中有公司的专利信息
conn = MongoClient('106.75.65.56', 27017)
db = conn['CFDA']
baiteng = db['baiteng']
companylist = ['北京旷视科技有限公司', '杭州安恒信息技术有限公司', '上海红神信息技术有限公司', '南京中储新能源有限公司', '成都恩普生医疗科技有限公司',
               '武汉众宇动力系统科技有限公司', '深圳市医诺智能科技发展有限公司', '深圳市清友能源技术有限公司', '上海魅丽纬叶医疗科技有限公司',
               '重庆中科云丛科技有限公司', '北京江南天安科技有限公司', '宁波美晶医疗技术有限公司', '识益生物科技（北京）有限公司', '上海通用药业股份有限公司',
               '北京北科天绘科技有限公司', '福州友宝电子科技有限公司', '宁波韦尔德斯凯勒智能科技有限公司', '心诺普医疗技术（北京）有限公司', '宁波薄言信息技术有限公司',
               '光景生物科技（苏州）有限公司', '科技谷（厦门）信息技术有限公司', '北京明略软件系统有限公司', '浙江莱达信息技术有限公司', '金普诺安蛋白质工程技术（北京）有限公司',
               '广州卫视博生物科技有限公司', '上海君众信息科技有限公司', '杭州华恩教育科技有限公司', '北京奥科美技术服务有限公司', '成都术有科技有限公司',
               '杭州华恩教育科技有限公司', '长春赛诺迈德医学技术有限责任公司', '北京畅想天行医疗技术有限公司', '上海黄海制药有限责任公司', '辽宁天龙药业有限公司']

def LSH_test():
    company_zhuanli_title_list=[]
    company_zhuanli_content_list=[]

    # for循环分别提取每个公司的专利信息
    for i in range(len(companylist)):
        # baiteng数据库
        baiteng_item=baiteng.find_one({'公司名称':companylist[i]})
        # print(i)

    # 专利名称处理
        zhuanli_title=''.join(list(baiteng_item['专利'].keys()))
        zhuanli_title_list=jieba.cut(zhuanli_title,cut_all=False)
        zhuanli_title_list=remove_stopwords(zhuanli_title_list)
        zhuanli_title=''.join(zhuanli_title_list)
        # zhuanli_title = zhuanli_title_list
        # 上述四行将一个公司的所有专利名称连接、分词、移除停用词后再连接，生成一个全新的字符串

        # 将该字符串append入专利名称list中
        company_zhuanli_title_list.append(zhuanli_title)


    # 专利内容处理
        zhuanli_content=''.join([value['summary'] for value in baiteng_item['专利'].values()])
        zhuanli_content_list=jieba.cut(zhuanli_content,cut_all=False)
        zhuanli_content_list=remove_stopwords(zhuanli_content_list)
        zhuanli_content=''.join(zhuanli_content_list)
        # zhuanli_content = zhuanli_content_list
        # 上述四行将一个公司的所有专利内容连接、分词、移除停用词后再连接，生成一个全新的字符串
        # 将该字符串append入专利名称list中

        company_zhuanli_content_list.append(zhuanli_content)

    # for i in range(len(companylist)):
    #     print('公司名称：',companylist[i])
    #     print('专利名汇总：',company_zhuanli_title_list[i])
    #     print('专利内容汇总',company_zhuanli_content_list[i])
    #     print('')
    tfidf_vectorizer = TfidfVectorizer()
    title_train = tfidf_vectorizer.fit_transform(company_zhuanli_title_list)

    print('生成的字典',tfidf_vectorizer.vocabulary_)
    print('company_zhuanli_title_list',len(company_zhuanli_title_list))
    print('title_train',type(title_train))
    print(np.shape(title_train),title_train)

    test_title = '处理设备所述信息处理获取原始网页解析所述原始网页确定候选图像集检测所述候选图像集中每个候选图像包含人脸检测人脸确定目标人脸目标人脸对应候选图像确定目标图像所述目标人脸进'
    test_cut_title_list = list(jieba.cut(test_title, cut_all=False))
    test_cut_title_list = ''.join(test_cut_title_list)

    x_test = tfidf_vectorizer.transform([test_cut_title_list])
    print('x_test', x_test)

    lshf = LSHForest(random_state=42)
    lshf.fit(title_train.toarray())

    distances, indices = lshf.kneighbors(x_test.toarray(), n_neighbors=5)
    print('distances',distances)
    print('indices',indices)

if __name__=='__main__':
    LSH_test