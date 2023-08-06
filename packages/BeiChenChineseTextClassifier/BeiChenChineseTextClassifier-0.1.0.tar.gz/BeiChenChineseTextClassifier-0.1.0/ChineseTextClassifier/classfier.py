import os
import shutil
import jieba
import numpy as np
# import nltk
# from nltk.corpus import names
import random
from shutil import copyfile
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer


dirs = 'E:/easy_article'
save_dir = 'seg_article'
'''
def make_simple_dataset():
    """复旦数据集的简化版"""
    path = 'E:/Fudan/train'
    new_path = 'E:/easy_article'
    labels = {}
    for label in os.listdir(path):
        new_label = label.split('-')[1]
        labels[label.split('-')[1]] = len(labels)
        os.makedirs(new_path+'/'+new_label)
        if label == 'utf8' : continue
        i = 1
        for file in os.listdir(path + '/' + label):
            print(file)
            if file =='utf8':continue
            shutil.copyfile(path+'/'+label+'/'+file,new_path+'/'+new_label+'/'+file)
            i+=1
            if i==10: break
    print(labels)
'''
labels = {}


def get_corpus(dir):
    corpus = []
    y = []
    for label in os.listdir(dir):
        labels[label] = len(labels)
    print(labels)
    for label in os.listdir(dir):
        for file in os.listdir(dir + '/' + label):
            # corpus += [(get_tokens(dir+'/'+label+'/'+file),labels[label]) for file in os.listdir(dir+'/'+label)]
            corpus.append(get_tokens(dir + '/' + label + '/' + file))
            y.append(labels[label])
        # TODO 测试第一个
    # print(corpus)
    return corpus, y


def read_file(file):
    with open(file, 'rb') as fp:
        content = fp.read()
    return content


def read_Ufile(file):
    with open(file, "r", encoding="utf8") as fp:
        content = fp.read()
    return content


def get_tokens(file):
    """对中文文档分词"""
    content = read_file(file)
    content = content.replace("\r\n".encode('utf-8'), "".encode('utf-8'))  # 删除换行
    content = content.replace(" ".encode('utf-8'), "".encode('utf-8'))  # 删除空行、多余的空格
    content_seg = jieba.cut(content)  # 为文件内容分词
    temp = " "
    stopwords = read_Ufile('hit_stopwords.txt').splitlines()
    for token in content_seg:
        if token not in stopwords:
            temp += token
            temp += ","
            temp += " "
    # print(temp)
    return temp


def get_features(corpus):
    # 文本特征抽取
    """

    :return: features : dict 一个带有特征的列表
    """
    vectorizer = CountVectorizer()
    counts = vectorizer.fit_transform(corpus)
    counts = counts.toarray()
    vocabulary = vectorizer.vocabulary_
    return counts
    # print('------------')
    # print(counts[0])
    # print(vocabulary)


def split_train_and_test(docs, label, d):
    s = int(len(docs) * d)
    X_train = docs[:s]
    Y_train = label[:s]
    X_test = docs[s:]
    Y_test = label[s:]
    return X_train, Y_train, X_test, Y_test


def run_bayes_model(dir, seed, rate):
    corpus, y = get_corpus(dir)
    print('文本处理完毕')
    counts = get_features(corpus)
    print('特征提取完成')
    y = np.array(y)
    data = np.column_stack((counts, y))
    print(data.shape)
    random.seed(seed)
    random.shuffle(data)
    docs = data[:, :-1]
    print(docs.shape)
    labels = data[:, -1]
    x1, y1, x2, y2 = split_train_and_test(docs, labels, rate)
    clf = MultinomialNB()
    clf.fit(x1, y1)
    print('模型训练完毕')
    print(clf.predict(x2))
    print('结果预测完毕')
    print(y2)
    print('对模型进行打分')
    print(clf.score(x2, y2))

# dirs = 'E:/SVMmodel/train_tokens'
# run_bayes_model(dirs, 80820, 0.9)
