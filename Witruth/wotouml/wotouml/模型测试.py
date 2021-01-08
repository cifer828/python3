from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from xgboost import XGBClassifier
from functions import *
import numpy as np

filename = 'data/train.csv'
x_label = ['经营范围lda', '专利标题lda', '专利内容lda', '经营范围cos', '专利标题cos',
               '专利内容cos', '所属行业']
y_label = ['sim']
feature,label = load_data(filename=filename,x_label=x_label,y_label=y_label)
# 类别4:398，占比64.3%
# 类别1:221
feature,label = balance_sample(feature=feature,label=label)
# 类别4:221
# 类别1:221

split_count = 5
n_estimators = 100
learning_rate = 0.1

def rf_test():
    rf = RandomForestClassifier(n_estimators=n_estimators,
                                criterion='gini',
                                min_samples_leaf=5,
                                min_samples_split=12,
                                max_features='auto',
                                oob_score=True,
                                random_state=1,
                                n_jobs=-1
                                )
    use_model(rf, 'RF', feature=feature, label=label)
def gbdt_test():
    gbdt = GradientBoostingClassifier(loss='deviance',
                                      learning_rate=learning_rate,
                                      n_estimators=n_estimators,
                                      max_depth=3,
                                      min_samples_split=2,
                                      min_samples_leaf=1,
                                      max_features='auto',
                                      random_state=1,
                                      )
    use_model(gbdt, 'gbdt', feature=feature, label=label)
def xgboost_test():
    xgboost = XGBClassifier(max_depth=3, # 交叉验证调参
                            learning_rate=learning_rate,
                            n_estimators=n_estimators,
                            silent=True,
                            objective='binary:logistic',
                            # nthread=-1
                            gamma=0,    # 需要调参
                            # gamma:Minimum loss reduction required to make a further partition on a leaf node of the tree
                            min_child_weight=1, # 调大该参数可以控制过拟合
                            # Minimum sum of instance weight(hessian) needed in a child

                            # max_delta_step=0
                            # Maximum delta step we allow each tree’s weight estimation to be
                            subsample=1,
                            # 用于训练模型的子样本占整个样本集合的比例
                            colsample_bytree=1,
                            # 建立树时对特征随机采样的比例
                            colsample_bylevel=1,
                            # 节点分裂时对特征随机采样的比例

                            # reg_alpha=0,
                            # reg_lambda=1,
                            # reg_ 是线性模型的参数

                            scale_pos_weight=1,
                            # scale_pos_weight:大于0的取值可以处理类别不平衡的情况。帮助模型更快收敛
                            base_score=0.5,
                            # base_score:the initial prediction score of all instances, global bias
                            seed=0,
                            # seed:Random number seed.
                            # missing=None
                            )
    use_model(xgboost, 'xgboost', feature=feature, label=label)
def svm_test():
    svc = SVC(C=1,
              kernel='rbf',
              gamma='auto',
              random_state=3)
    use_model(svc,'svc',feature=feature,label=label)

if __name__ =='__main__':
    rf_test()
    gbdt_test()
    xgboost_test()
    svm_test()
