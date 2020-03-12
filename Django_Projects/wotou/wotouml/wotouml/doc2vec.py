import multiprocessing
from gensim.models.doc2vec import Doc2Vec,LabeledSentence,TaggedDocument
from 相似度计算.gen_vector import remove_stopwords
from gensim.models import Doc2Vec
import gensim.models.doc2vec
import jieba

'''
目前的问题：同样的数据下，每次运行都得到不同的结果
'''

raw_documents = [
    '0人脸关键特征点检测模型的训练、检测方法及系统',
    '1一种融合多种人脸识别算法的识别方法及系统',
    '2一种实现远程监测与控制的终端配送柜、配送柜系统及通信方法',
    '3电子配送系统、电子配送专用网系统及电子配送计费系统',
    '4一种胶囊内窥镜运动的控制系统和控制方法',
    '5一种人体微型探测器以及激活控制器',
    '6一种指静脉识别模块及具有其的装置',
    '7一种具有指静脉识别装置的移动终端及指静脉识别方法',
    '8预测域名是否恶意的方法、系统及其模型训练方法、系统',
    '9恶意URL检测干预方法、系统及装置',
]

# 使用doc2vec来判断
cores = multiprocessing.cpu_count()
print('cores',cores)

corpora_documents = []
for i, item_text in enumerate(raw_documents):
    words_list = list(jieba.cut(item_text,cut_all=False))
    words_list = remove_stopwords(words_list)
    document = TaggedDocument(words=words_list, tags=[i])
    print('document',document)
    corpora_documents.append(document)

print('corpora_documents',type(corpora_documents),corpora_documents)

model = Doc2Vec(size=89, min_count=1, iter=10)
model.build_vocab(corpora_documents)
# Build vocabulary from a sequence of sentences (can be a once-only generator stream).
# Each sentence must be a list of unicode strings.

model.train(corpora_documents,total_examples=len(corpora_documents),epochs=100)
# either total_examples (count of sentences) or total_words (count of raw words in sentences) MUST be provided
print('#########', model.vector_size)

test_data_1 = '一种复杂场景下基于人脸识别的视频人像跟踪方法'
test_cut_raw_1 = list(jieba.cut(test_data_1,cut_all=False))
remove_stopwords(test_cut_raw_1)
print(test_cut_raw_1)
inferred_vector = model.infer_vector(test_cut_raw_1)
print('inferred_vector',inferred_vector)
sims = model.docvecs.most_similar([inferred_vector], topn=1)
print('sims',sims)