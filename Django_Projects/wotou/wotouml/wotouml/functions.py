import pandas as pd
import random
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split

def load_data(filename,x_label,y_label):
    df = pd.read_csv(filename, encoding='GBK')
    df.fillna(0)
    # 619*19
    raw_x = df[x_label]
    for i in range(len(df['sim'])):
        if df['sim'][i] != 4:
            df['sim'][i] = 1
    # print(df['sim'].value_counts())
    # 类别4:398，占比64.3%
    # 类别1:221
    raw_y = df[y_label][y_label]
    return raw_x,raw_y

def balance_sample(feature,label):
    # 本函数用于解决样本分别不均匀的问题
    # print('feature',type(feature),feature.shape,feature.index)
    # print('label',type(label),label.shape,label.index)
    index_1 = []
    index_4 = []
    for i in range(len(label)):
        # print(label['sim'][i])
        if label['sim'][i]==1:
            index_1.append(i)
        else:
            index_4.append(i)
    min_count = min(len(index_1),len(index_4))
    index_1 = random.sample(index_1,min_count)
    index_4 = random.sample(index_4,min_count)
    index_1.extend(index_4)
    select_index = index_1
    select_index.sort()

    # random.shuffle(select_index)
    # print(select_index,len(select_index))

    for i in range(len(label)):
        if i not in select_index:
            feature.drop(i,inplace=True,axis=0)
            label.drop(i,inplace=True,axis=0)

    return feature,label

def get_quality(test_labels,predict_labels):
    # print (test_labels)
    # print type(test_labels)
    # print (predict_labels)
    # print type(predict_labels)
    num = len(test_labels)
    right_num = 0
    true_p = 0
    true_n = 0
    false_p = 0
    false_n = 0
    test_labels_list = []
    for i in test_labels['sim']:
        # print(i)
        test_labels_list.append(i)

    for i in range(len(predict_labels)):
        if test_labels_list[i] == 1 and predict_labels[i] == 1:
            right_num += 1
            true_p += 1
        elif test_labels_list[i] == 1 and predict_labels[i] == 4:
            false_n += 1
        elif test_labels_list[i] == 4 and predict_labels[i] == 1:
            false_p += 1
        elif test_labels_list[i] == 4 and predict_labels[i] == 4:
            right_num += 1
            true_n += 1
    # print ('num',num)
    # print ('right_num',right_num)
    # print ('true_p',true_p)
    # print ('false_p',false_p)

    accuracy = right_num / float(num)

    precision = true_p / float(true_p + false_p)
    sensitivity = true_p / float(true_p + false_n)
    specificity = true_n / float(true_n + false_p)
    return sensitivity,precision
    # return accuracy,true_p,true_n,false_p,false_n

def use_model(model,modelname,feature,label):
    sum_acc = 0
    sum_sensitivity = 0
    sum_precison = 0
    split_count=5
    for j in range(split_count):
        x_train, x_test, y_train, y_test = train_test_split(feature, label, test_size=0.25)
        model.fit(X=x_train, y=y_train)
        single_acc = model.score(X=x_test, y=y_test)
        predict_labels = model.predict(X=x_test)
        sensitivity, precision = get_quality(test_labels=y_test, predict_labels=predict_labels)
        # print('单次准确率：',single_acc,'类别1查全率：',sensitivity,'类别1查准率',precision)
        sum_acc += single_acc
        sum_precison += precision
        sum_sensitivity += sensitivity
    mean_acc = sum_acc / split_count
    mean_sensitivity = sum_sensitivity / split_count
    mean_precision = sum_precison / split_count
    print(modelname,'的平均准确率', mean_acc, '平均查全率', mean_sensitivity, '平均查准率', mean_precision)


if __name__ =='__main__':
    filename = 'train.csv'
    x_label = ['经营范围lda', '专利标题lda', '专利内容lda', '经营范围cos', '专利标题cos',
               '专利内容cos', '所属行业']
    y_label = ['sim']
    feature,label = load_data(filename = filename,x_label=x_label,y_label=y_label)
    feature,label = balance_sample(feature=feature,label=label)
    # print(feature,label)
    print(np.shape(feature),np.shape(label))