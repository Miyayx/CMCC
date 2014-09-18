#!/usr/bin/python2.7
#-*-coding:utf-8-*-

import numpy as np
from sklearn import svm
from sklearn import cross_validation
import time
import codecs
import os

from utils import *
from csvio import CSVIO
from config_global import *

class LowAccuracy(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "Low Accuracy:",self.value

class SVM:

    def __init__(self, data_file):
        props = read_properties(PROP_FILE)
        props.update(read_properties(COL_FILE))

        self.feature_count = int(props["feature_count"])
        self.lowest_accuracy = float(props["lowest_accuracy"])
        self.train_test_ratio = 2.0/1
        self.classifer = svm.SVC(kernel='linear', C=1)

        self.data_file = data_file

        self.log = {}

    def run(self, train_file, test_file, predict_file, test_result_file, test_statistic,log_file, iter_n):
        """
        Args
        -----------------------------------
        train_file:
            记录训练数据
        test_file:
            记录测试数据
        predict_file:
            记录预测数据与预测结果
        test_result_file
            测试结果与标柱对比
        test_statistic
            测试结果数据统计与准确率记录
        log_file
            每次迭代的样本数量记录结果
        """

        self.iter_n = iter_n 

        self.train_file = train_file
        self.test_file = test_file
        self.predict_file = predict_file
        self.test_result_file = test_result_file
        self.test_statistic = test_statistic

        X_flag, Y_flag, predict = self.get_data(self.data_file)

        #训练与测试
        self.train_test(X_flag, Y_flag)

        name_predict, X_predict = self.name_feature_split(predict)
        name_flag, X_flag = self.name_feature_split(X_flag)

        # 预测
        Y_predict = self.predict(X_predict)

        self.log["predict_all"] = len(Y_predict)
        self.log["predict_pos"] = len(Y_predict) - list(Y_predict).count("others")
        self.log["predict_neg"] = list(Y_predict).count("others")
        self.log["all_pos"] = self.log.get("all_pos",0) + self.log["predict_pos"]
        self.log["all_neg"] = self.log.get("all_neg",0) + self.log["predict_neg"]

        result = dict((name_predict[i], Y_predict[i]) for i in range(len(name_predict)))
        flag = dict((name_flag[i], Y_flag[i]) for i in range(len(name_flag)))
        
        csv = CSVIO(self.data_file)
        s2c = csv.read_one_to_one(0,csv.fields.index("cluster"+str(self.iter_n)))
        self.log["cluter_num"] = len(set(s2c.values()))
        s2sl = csv.read_one_to_one(0, csv.fields.index("section label"))
        s2bl = csv.read_one_to_one(0, csv.fields.index("block label"))
        self.record_result(self.predict_file, [("class",result), ("section label",s2sl),("block label", s2bl)])
        result.update(flag)
        self.append_result(self.data_file, result)

        csv = CSVIO(log_file)
        if not os.path.isfile(log_file):
            csv.column("type", dict((s,s) for s in self.log.keys()))
        csv.column("Iter"+str(self.iter_n), self.log)
        csv.write(log_file, ",", True, True )

    def name_feature_split(self, data):
        """
        把name和feature分开
        """
        name = []
        feature = []
        for d in data:
            name.append(d[0])
            feature.append(d[2:])
        return name, np.array(feature)

    def get_data(self, data_file):
        X_flag = []
        Y_flag = []
        
        predict = []
        
        flag_i = 0
        begin = 0
        end = 0
        
        for line in codecs.open(data_file,'r','utf-8'):
            items = line.strip("\n").split(",")
            if not items[2].isdigit():
                end = items.index("sample2")
                flag_i = items.index("flag"+str(self.iter_n))
                cluster_i = items.index("cluster"+str(self.iter_n))
                continue
            if len(items[flag_i]) > 1:
                X_flag.append([i for i in items[begin:end]])
                Y_flag.append(items[flag_i])
            elif len(items[cluster_i].strip()) > 0:
                predict.append([i for i in items[begin:end]])
        print "Flag all:",len(Y_flag)
        print "Predict all:",len(predict)

        return X_flag, Y_flag, predict

    def append_result(self, fn, s2l):
        """
        Write to big table file
        """
        print "Add to "+fn
        colname = "class"+self.iter_n
        csv = CSVIO(fn)
        csv.column(colname, s2l)
        csv.write(fn, ",", True, True, csv.fields.index(colname))

    def record_result(self, fn, columns = [] ):
        """
        Write to cluster result file
        """
        print "Write to "+fn

        csv = CSVIO(fn,append = False)
        csv.column("sample", dict((s,s) for s in columns[0][1].keys()))
        for colname, col in columns:
             csv.column(colname, col)
        csv.write(fn, ",", True, True)

    def write_statistic(self, fn, Y_test, Y_predict, score):
        """
        Write precision and statistic to file
        """
        print "Precision:%0.3f\n"%score
        import annotation
        c = annotation.read_config(ANNOTATION_FILE)
        neg = c["neg_class"]
        pos_pos = pos_neg = neg_pos = neg_neg = 0
        for i in range(len(Y_test)):
            if not Y_test[i] == neg and not Y_predict[i] == neg:
                pos_pos += 1
            elif Y_test[i] == neg and not Y_predict[i] == neg:
                neg_pos += 1
            elif (not Y_test[i] == neg) and (Y_predict[i] == neg):
                pos_neg += 1
            elif Y_test[i] == neg and Y_predict[i] == neg:
                neg_neg += 1

        print "    Pos   Neg"
        print "Pos %4d %4d"%(pos_pos, pos_neg)
        print "Neg %4d %4d"%(neg_pos, neg_neg)

        with open(fn, "w") as f:
            f.write("    Pos   Neg\n")
            f.write("Pos %4d %4d\n"%(pos_pos, pos_neg))
            f.write("Neg %4d %4d\n"%(neg_pos, neg_neg))
            f.write("\n")
            f.write("Precision:%0.3f"%score)

    def train_test(self, X_flag, Y_flag):
        """
        X_flag:
            feature
        Y_flag:
            标注结果
        """

        X_train, X_test, Y_train, Y_test = cross_validation.train_test_split(np.array(X_flag), np.array(Y_flag), test_size=1.0/(self.train_test_ratio+1), random_state=0)
        print "Train all:",len(Y_train)
        print "Test all:",len(Y_test)
        self.log["train_all"] = len(Y_train)
        self.log["train_pos"] = len(Y_train) - list(Y_train).count("others")
        self.log["train_neg"] = list(Y_train).count("others")
        self.log["test_all"] = len(Y_test)
        self.log["test_pos"] = len(Y_test) - list(Y_test).count("others")
        self.log["test_neg"] = list(Y_test).count("others")
        self.log["all_pos"] = self.log.get("all_pos",0)+self.log["train_pos"]+self.log["test_pos"]
        self.log["all_neg"] = self.log.get("all_neg",0)+self.log["train_neg"]+self.log["test_neg"]

        name_train, X_train = self.name_feature_split(X_train)
        name_test, X_test = self.name_feature_split(X_test)

        self.classifer.fit(X_train, Y_train)
        Y_predict = self.classifer.predict(X_test)
        s = self.classifer.score(X_test, Y_test)
        self.log["test_precision"] = s
        if s < self.lowest_accuracy:
            raise LowAccuracy(s)

        train = dict((name_train[i], Y_train[i]) for i in range(len(name_train)))
        test = dict((name_test[i], Y_test[i]) for i in range(len(name_test)))
        test_result = dict((name_test[i], Y_predict[i]) for i in range(len(name_test)))

        self.record_result(self.train_file, [("class",train)])
        self.record_result(self.test_file, [("class",test)])
        self.record_result(self.test_result_file, [("flag",test),("class",test_result)])
        self.write_statistic(self.test_statistic, Y_test, Y_predict, s)

    def predict(self, X_predict):
        """
        """

        return self.classifer.predict(X_predict)


if __name__=="__main__":
    import sys
    if len(sys.argv) < 2:
        print "Need Iteration Num for Argument"
         
    iter_n = sys.argv[1]

    import time
    start = time.time()

    props = read_properties(PROP_FILE)
    props.update(read_properties(NAME_FILE))
    props["file_path"] = "../"+props["file_path"].strip("/")+"/"

    data_file = props["file_path"]+props["result"].replace('Y',props["featureid"])
    classify_train= props["file_path"]+props["classify_train"].replace('Y',props["featureid"]).replace('X',iter_n)
    classify_test= props["file_path"]+props["classify_test"].replace('Y',props["featureid"]).replace('X',iter_n)
    classify_predict= props["file_path"]+props["classify_predict"].replace('Y',props["featureid"]).replace('X',iter_n)
    classify_test_result= props["file_path"]+props["classify_test_result"].replace('Y',props["featureid"]).replace('X',iter_n)
    classify_test_statistics= props["file_path"]+props["classify_test_statistics"].replace('Y',props["featureid"]).replace('X',iter_n)
    log = props["file_path"]+props["log"]

    svm = SVM(data_file)
    svm.run(classify_train, classify_test, classify_predict, classify_test_result, classify_test_statistics,log,iter_n)

    print "Time Consuming:",(time.time()-start)
        
