import cv2
import numpy as np
import os

class Detector:
    """
    hov提取特征 + svm训练
    """
    def __init__(self, Data_PATH = 'D:\TrainData\Pedestrians64x128'):
        self.__DATA_PATH = Data_PATH + '\\'
        self.__detect = cv2.xfeatures2d.SIFT_create()  # 提取关键点
        self.__extract = cv2.xfeatures2d.SIFT_create() # 提取特征
        self.__matcher = self.__get_flann_matcher()    # flann匹配器
        self.extract_bow = self.__get_bow_extractor()
        self.svm = self.__init_svm()  # 初始化svm

    def __get_bow_extractor(self):
        return cv2.BOWImgDescriptorExtractor(self.__extract,self.__matcher)

    def __get_flann_matcher(self):
        self.__flann_params = dict(algorithm = 1, trees = 5)
        return cv2.FlannBasedMatcher(self.__flann_params, {})

    def __init_svm(self, Gamma = 1, C = 35):
        svm = cv2.ml.SVM_create()
        svm.setGamma(Gamma)
        svm.setC(C) # 大精度越差，小容易过拟合
        svm.setKernel(cv2.ml.SVM_RBF)
        return svm

    def __pos_pic(self, num):
        # 返回指定数目的正样本文件名
        chdir = os.listdir(self.__DATA_PATH + 'Positive')
        return [self.__DATA_PATH + 'Positive\\' + picName for picName in chdir[: num]]

    def __neg_pic(self, num):
        # 返回指定数目的负样本文件名
        chdir = os.listdir(self.__DATA_PATH + 'Negative')
        return [self.__DATA_PATH + 'Negative\\' + picName for picName in chdir[: num]]

    def __bow_kmeans_trainer(self, num):
        """
        添加训练图像
        """
        trainer = cv2.BOWKMeansTrainer(40)
        pos = self.__pos_pic(num)
        neg = self.__neg_pic(num)
        for i in range(num):
            trainer.add(self.__extract_sift(pos[i]))
            trainer.add(self.__extract_sift(neg[i]))
        return trainer

    def __extract_sift(self, fn):
        """
        返回描述符
        """
        im = cv2.imread(fn, 0)         # 灰度格式读取
        return self.__extract.compute(im, self.__detect.detect(im))[1]

    def bow_features(self, fn, extractor_bow, detector):
        """
        返回基于BOW的描述符
        """
        im = cv2.imread(fn, 0)
        return extractor_bow.compute(im, detector.detect(im))

    def svm_training(self, train_num=500):
        """
        trainer_size : 训练器数量，用于特征提取的聚类
        train_num: 训练样本数量
        """
        # 聚类并设置视觉词汇
        print("adding features to trainer")
        bow_kmeans_trainer = self.__bow_kmeans_trainer(train_num)
        voc = bow_kmeans_trainer.cluster()
        self.extract_bow.setVocabulary(voc)
        traindata, trainlabels = [],[]

        # 添加训练集
        pos_path = self.__pos_pic(train_num)
        neg_path = self.__neg_pic(train_num)
        print("adding to lda_results data")
        for i in range(train_num):
            traindata.extend(self.bow_features(pos_path[i], self.extract_bow, self.__detect))
            trainlabels.append(1)
            traindata.extend(self.bow_features(neg_path[i], self.extract_bow, self.__detect))
            trainlabels.append(-1)
        # svm训练
        print("training svm")
        self.svm.train(np.array(traindata), cv2.ml.ROW_SAMPLE, np.array(trainlabels))


    def predict_one(self, fn):
        f = self.bow_features(fn, self.extract_bow, self.__detect)
        p = self.svm.predict(f)
        print(fn, "\t", p[1][0][0])
        return p

    def save_svm(self, path):
        self.svm.save(path)

    def show_prediction(self, pos_name="per00924.ppm", neg_name="002120.jpg"):
        """
        展示预测集结果
        """
        pos, neg = self.__DATA_PATH + 'Positive\\' + pos_name, self.__DATA_PATH + 'Negative\\' + neg_name
        pos_img = cv2.imread(pos)
        neg_img = cv2.imread(neg)
        pos_predict = self.predict_one(pos)
        neg_predict = self.predict_one(neg)
        font = cv2.FONT_HERSHEY_SIMPLEX
        if (pos_predict[1][0][0] == 1.0):
            cv2.putText(pos_img,'Positive',(5,10), font, 0.5,(0,255,0),1,cv2.LINE_AA)
        if (neg_predict[1][0][0] == -1.0):
            cv2.putText(neg_img,'Negative',(5,10), font, 0.5,(0,0, 255),1,cv2.LINE_AA)
        cv2.namedWindow('BOW + SVM Success', 0)
        cv2.imshow('BOW + SVM Success', pos_img)
        cv2.namedWindow('BOW + SVM Failure', 0)
        cv2.imshow('BOW + SVM Failure', neg_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    hov_obj = Detector('D:\TrainData\Pedestrians64x128')
    hov_obj.svm_training()
    # hov_obj.show_prediction()

    test_path = 'D:\TrainData\Pedestrians64x128\Positive\\per00855.ppm'
    test_path = 'C:\\Users\\zhqch\\Documents\\code\\Python3Projects\\visual_detection\\input\\test4.png'
    hov_obj.predict_one(test_path)

