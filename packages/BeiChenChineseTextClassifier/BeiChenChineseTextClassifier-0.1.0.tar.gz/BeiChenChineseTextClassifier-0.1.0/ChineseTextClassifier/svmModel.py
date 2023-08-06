from get_tokens import segment
from to_bunch import toBunch
from TFIDF_space import vector_space
from SVM_Predict import readBunchObj
from use import predict

def train_SVMmodel(file_path,save_path):
    raw_path = file_path
    seg_path = save_path+'/train_tokens/'
    segment(raw_path, seg_path)
    bunch_path = save_path+'/train_word_bag/train_wordbag.dat'
    stopword_path = save_path+'/train_word_bag/hit_stopwords.txt'
    toBunch(bunch_path, seg_path, stopword_path)
    train_path = save_path+'/train_word_bag/tfidfspace.dat'
    vector_space(bunch_path, train_path)
    train_set = readBunchObj(train_path)
    from sklearn.externals import joblib
    from sklearn import svm
    clf = svm.SVC(kernel="poly", class_weight="balanced")  # 增加了权重 对比的时候去掉
    print("正在计算")
    clf.fit(train_set.tdm, train_set.label)
    save_dir = save_path + "/clf_poly.dat"
    joblib.dump(clf, save_dir)  # 保存模型
    print("训练完毕")


def predict_SVMmodel(filepath,save_path):
    predict(filepath,save_path)

