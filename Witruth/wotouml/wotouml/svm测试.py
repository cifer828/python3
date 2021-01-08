from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.model_selection import KFold
import numpy as np
import pandas as pd

import math


df = pd.read_csv('train.csv',encoding = 'GBK')
df.fillna(0)
# 619*19
x_label=['经营范围lda','专利标题lda','专利内容lda','经营范围cos','专利标题cos',
         '专利内容cos','所属行业']
y_label=['sim']
raw_x=df[x_label]
raw_y=df[y_label]['sim']
# print(raw_y)
# onehot_y=[]
# for i in range(len(raw_y)):
#     onerow=[0,0,0,0]
#     # print (int(raw_y[i]))
#     onerow[int(raw_y[i])-1]=1
#     onehot_y.append(onerow)

# sim_1 = df[df.sim==1]
# feature_1 = sim_1[x_label]
# label_1 = sim_1[y_label]['sim']
#
# sim_2 = df[df.sim==2]
# feature_2 = sim_2[x_label]
# label_2 = sim_2[y_label]['sim']
#
# sim_3 = df[df.sim==3]
# feature_3 = sim_3[x_label]
# label_3 = sim_3[y_label]['sim']
#
# sim_4 = df[df.sim==4]
# feature_4 = sim_4[x_label]
# label_4 = sim_4[y_label]['sim']

# 将多分类问题先转换成二分类问题
for i in range(len(df['sim'])):
    # print(df['sim'][i])
    if df['sim'][i]!=4:
        df['sim'][i] = 1

# print(df['sim'].value_counts())
# 类别4:398，占比64.3%
# 类别1:221
onehot_y = df[y_label]['sim']

k = 100
# max_item第一项为参数c的值，第二项为平均准确率，第三项为循环100遍中的最低准确率
max_item = [0, 0, 0]
# 更改mici即可改变参数C的寻优list
mici = [math.pow(5,i) for i in range(6)]
result = []
for xunhuan in range(3):
    for c in mici:
        sum_acc = 0
        min_acc = 1
        for i in range(k):
            x_train, x_test, y_train, y_test = train_test_split(raw_x, onehot_y, test_size=0.25)

            # clf = LinearSVC(C=c)
            clf = SVC(C=c)

            clf.fit(X=x_train,y=y_train)
            # print('真实标签：',y_test)
            # print('预测标签',clf.predict(X=x_test))
            temp = clf.score(X=x_test,y=y_test)
            # print(temp)
            sum_acc += temp
            min_acc = min(min_acc,temp)
        print('c=',c,'时，平均准确率为：',str(sum_acc/k))
        if sum_acc/k>max_item[1]:
            max_item[0] = c
            max_item[1] = sum_acc/k
            max_item[2] = min_acc
    print(max_item)
    result.append(max_item)
    max_item = [0, 0, 0]
print(result)