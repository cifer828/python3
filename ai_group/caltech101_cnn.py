#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/23 11:21
# @Author  : Cifer
# @File    : caltech101_cnn.py

import os
import cv2
from PIL import Image
import numpy as np
import tensorflow as tf

TRAIN_TXT = 'training_set.txt'
VALIDATION_TXT = 'validation_set.txt'

def separate_data(root_path, ratio = 0.6):
    """
    :param dir_path: 训练集根目录
    :param ratio: training_set和validation set比例
    划分training set, validation set
    :return: 标签字典
    """
    with open(TRAIN_TXT, 'w') as f:
        f.write('')
    with open(VALIDATION_TXT, 'w') as f:
        f.write('')
    label_dict = {}
    for label, (dir, x, files) in enumerate(os.walk(root_path)):
        if label == 0: continue
        # 标签数值化
        category = dir.split('\\')[-1]
        label_dict[label] = category
        # 随机抽样，默认60% training set, 40% validation set
        file_num = len(files)
        rand_files = np.array(files)
        np.random.shuffle(rand_files)
        for file in rand_files[: int(file_num * ratio)]:
            with open(TRAIN_TXT, 'a') as f:
                f.write(os.path.join(dir, file) + '\t' + str(label) + '\n')
        for file in rand_files[int(file_num * ratio): ]:
            with open(VALIDATION_TXT, 'a') as f:
                f.write(os.path.join(dir, file) + '\t' + str(label) + '\n')
    return label_dict

def read_data(categories, training = True):
    """
    :param categories:  用到的类别
    :param training:  True for training, False for validation
    :return:
    """
    txt = TRAIN_TXT if training else VALIDATION_TXT
    file_path = []
    image_data = []
    labels = []
    with open(txt) as f:
        txt_data = f.read().strip().split('\n')
        for line in txt_data:
            image_path, cate = line.split('\t')
            label = int(cate)
            if label in categories:
                image = cv2.imread(image_path)
                im = cv2.resize(image, (32, 32), interpolation=cv2.INTER_CUBIC)
                # cv2.imshow('img', im)
                # if cv2.waitKey(0) == '27':
                #     continue
                # image = Image.open(image_path)
                # im = image.resize((32, 32), Image.ANTIALIAS).convert('L')
                data = np.array(im) / 255.0
                file_path.append(image_path)
                image_data.append(data)
                labels.append(label)
    image_data = np.array(image_data)
    labels = np.array(labels)
    return file_path, image_data, labels

def run_by_layer(file_path, data, label, label_dict, iter_num = 100, train=True):
    """
    :param file_path, data, label : 样本路径，像素矩阵，标签
    :param label_dict: 标签对应的物体名称
    :param iter_num: 训练次数
    :param train: True for training, False for validation
    """
    tf.reset_default_graph()
    data_placeholder = tf.placeholder(tf.float32, [None, 32, 32, 3])
    label_placeholder = tf.placeholder(tf.int32, [None])
    # dropout防止过拟合，0.25 for train，0 for test
    dropout_placeholder = tf.placeholder(tf.float32)

    # 卷积层，20核，5x5，Relu激活
    conv0 = tf.layers.conv2d(data_placeholder, 20, 5, activation=tf.nn.relu)
    # max-pooling, 窗口2x2，步长2x2
    pool0 = tf.layers.max_pooling2d(conv0, [2, 2], [2, 2])
    # 卷积层，40核，4x4，Relu激活
    conv1 = tf.layers.conv2d(pool0, 40, 4, activation=tf.nn.relu)
    # max-pooling, 窗口2x2，步长2x2
    pool1 = tf.layers.max_pooling2d(conv1, [2, 2], [2, 2])

    # 转一维
    flatten = tf.contrib.layers.flatten(pool1)
    # 全连接层
    fc = tf.layers.dense(flatten, 400, activation=tf.nn.relu)
    dropout_dc = tf.layers.dropout(fc, dropout_placeholder)
    # 输出层
    class_num = len(set(label))
    logits = tf.layers.dense(dropout_dc, class_num)
    predicted_labels = tf.argmax(logits, 1)

    # 交叉熵定义损失
    losses = tf.nn.softmax_cross_entropy_with_logits(
        labels = tf.one_hot(label_placeholder, class_num),
        logits = logits
    )
    # 平均损失
    mean_loss = tf.reduce_mean(losses)
    # 定义优化器，指定要优化的损失函数
    optimizer = tf.train.AdamOptimizer(learning_rate=1e-2).minimize(losses)

    correct_prediction = tf.equal(predicted_labels, tf.argmax(tf.one_hot(label_placeholder, class_num), 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    # 保存模型
    saver = tf.train.Saver(max_to_keep = 1)

    with tf.Session() as sess:
        if train:
            print('--------------Train-------------')
            sess.run(tf.global_variables_initializer())
            train_feed_dict = {
                data_placeholder: data,
                label_placeholder: label,
                dropout_placeholder: 0
            }
            for step in range(1, iter_num + 1):
                # _, mean_loss_val, _ = sess.run([optimizer, mean_loss, tf.Print(logits,[logits], summarize=100)], feed_dict=train_feed_dict)
                _, mean_loss_val, iterate_accuracy = sess.run([optimizer, mean_loss, accuracy], feed_dict=train_feed_dict)
                # iterate_accuracy = accuracy.eval(feed_dict=train_feed_dict)
                if step % 10 == 0:
                    print("step = %d\tmean loss = %f\ttraining accuracy = %4.2f%%" % (step, mean_loss_val, iterate_accuracy * 100.0))
            saver.save(sess, os.path.join(os.getcwd(), 'layer_model/layer_model'))
            print("训练结束,保存模型")
        else:
            print('--------------Test-------------')
            f =os.path.join(os.getcwd(), '.\\layer_model\\layer_model')
            saver.restore(sess, f)
            print('载入模型')
            test_feed_dict = {
                data_placeholder: data,
                label_placeholder: label,
                dropout_placeholder: 0
            }
            predicted_labels_val = sess.run(predicted_labels, feed_dict=test_feed_dict) # real_label从1开始，predicted从0开始
            right_predicted = 0
            for fpath, real_label, predicted_label in zip(file_path, label, predicted_labels_val):
                if real_label == predicted_label:
                    right_predicted += 1
                print("%s\t%s\t%s" % (fpath, label_dict[real_label], label_dict[predicted_label]))
            print('%d right predictions in %d samples, the accuracy is %4.2f%%' % (right_predicted, len(label), right_predicted * 100.0 / len(label)))

def run_by_nn(file_path, data, label, label_dict,  iter_num = 100, train=True):
    class_num = len(set(label))
    x = tf.placeholder(tf.float32, shape=[None, 32, 32, 3])
    y = tf.placeholder(tf.int32, shape=[None])
    y_ = tf.one_hot(y, class_num)

    # 定义第一个卷积层的variables和ops
    W_conv1 = tf.Variable(tf.truncated_normal([8, 8, 3, 32], stddev=0.1))
    b_conv1 = tf.Variable(tf.constant(0.1, shape=[32]))
    L1_conv = tf.nn.conv2d(x, W_conv1, strides=[1, 1, 1, 1], padding='SAME')
    L1_relu = tf.nn.relu(L1_conv + b_conv1)
    L1_pool = tf.nn.max_pool(L1_relu, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

    # 定义第二个卷积层的variables和ops
    W_conv2 = tf.Variable(tf.truncated_normal([3, 3, 32, 64], stddev=0.1))
    b_conv2 = tf.Variable(tf.constant(0.1, shape=[64]))
    L2_conv = tf.nn.conv2d(L1_pool, W_conv2, strides=[1, 1, 1, 1], padding='SAME')
    L2_relu = tf.nn.relu(L2_conv + b_conv2)
    L2_pool = tf.nn.max_pool(L2_relu, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

    # 全连接层
    W_fc1 = tf.Variable(tf.truncated_normal([8 * 8 * 64, 1024], stddev=0.1))
    b_fc1 = tf.Variable(tf.constant(0.1, shape=[1024]))
    h_pool2_flat = tf.reshape(L2_pool, [-1, 8*8*64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

    # dropout
    keep_prob = tf.placeholder(tf.float32)
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

    # readout层
    W_fc2 = tf.Variable(tf.truncated_normal([1024, class_num], stddev=0.1))
    b_fc2 = tf.Variable(tf.constant(0.1, shape=[class_num]))
    y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2

    # 定义优化器和训练op
    cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels= y_, logits=y_conv))
    train_step = tf.train.AdamOptimizer((1e-4)).minimize(cross_entropy)
    correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    # 保存模型
    saver = tf.train.Saver(max_to_keep = 1)
    with tf.Session() as sess:
        if train:
            print('--------------Train-------------')
            sess.run(tf.global_variables_initializer())
            for step in range(1, iter_num):
                _, cross_entropy_val = sess.run([train_step, cross_entropy], feed_dict={x:data, y: label, keep_prob: 0.25})
                iterate_accuracy = accuracy.eval(feed_dict={x: data, y: label, keep_prob: 1.0})
                if step % 10 == 0:
                    print("step = %d\tmean loss = %f\ttraining accuracy = %4.2f%%" % (step, cross_entropy_val, iterate_accuracy * 100))
            saver.save(sess, os.path.join(os.getcwd(), 'nn_model/nn_model'))
            print("训练结束,保存模型")

def main(func, label_range = None, random_range = 10):
    label_dict = separate_data('D:\\101_ObjectCategories')
    if label_range is None:
        # 随机抽选样本
        label_range = np.array(range(1,103))
        np.random.shuffle(label_range)
        label_range = label_range[: random_range]
    if func == run_by_layer:
        func(*read_data(label_range, training= True), label_dict)  # 训练
        func(*read_data(label_range, training= False), label_dict, train=False) # 测试
    elif func == run_by_nn:
        func(*read_data(label_range, training= True), label_dict)   # 训练


test_labels = range(1, 10)
# main(run_by_nn, test_labels)
main(run_by_layer, label_range=test_labels)
# main(run_by_nn, label_range=test_labels)
