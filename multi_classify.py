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
from global_config import *
from classify import *

class SVM:

    def __init__(self, data_file, configs):

        self.lowest_accuracy = float(configs["lowest_accuracy"])
        self.train_test_ratio = 2.0/1
        self.classifer = svm.SVC(kernel='linear', C=1)

        self.data_file = data_file

        self.log = {}#记录本次迭代的各种类样本统计数量

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
        log_file
            每次迭代的样本数量记录结果
        """

        self.iter_n = iter_n 

        self.train_file = train_file
        self.test_file = test_file
        self.predict_file = predict_file
        self.test_result_file = test_result_file

        X_flag, Y_flag, predict = self.get_data(self.data_file)

        #训练与测试
        self.train_test(X_flag, Y_flag)

        name_predict, X_predict = self.name_feature_split(predict)
        name_flag, X_flag = self.name_feature_split(X_flag)

        # 预测
        Y_predict = self.predict(X_predict)

        result = dict((name_predict[i], Y_predict[i]) for i in range(len(name_predict)))
        flag = dict((name_flag[i], Y_flag[i]) for i in range(len(name_flag)))
        
        csv = CSVIO(self.data_file)
        #读取大表中的section label和block label,写入聚类结果文件
        s2sl = csv.read_one_to_one(0, csv.fields.index("section label"))
        s2bl = csv.read_one_to_one(0, csv.fields.index("block label"))
        self.record_result(self.predict_file, [("class",result), ("section label",s2sl),("block label", s2bl)])
        result.update(flag)
        self.append_result(self.data_file, result)

        self.record_log(log_file)

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

    def record_log(self, log_file):
        """
        统计数据写入文件 
        """
        csv = CSVIO(log_file)
        if not os.path.isfile(log_file):
            csv.column("type", dict((s,s) for s in self.log.keys()))
        csv.column("Iter"+str(self.iter_n), self.log)
        csv.write(log_file, ",", True, True )

    def get_data(self, data_file):
        X_flag = [] #标注数据的feature数据
        Y_flag = [] #标注数据的标注结果
        
        predict = [] #待预测数据的feature数据
        
        flag_i = 0
        begin = 0
        end = 0
        
        isheader = True
        for line in codecs.open(data_file,'r','utf-8'):
            items = line.strip("\n").split(",")
            if isheader:#如果是第一行
                end = items.index("sample2")
                flag_i = items.index("flag"+str(self.iter_n))
                try:
                    cluster_i = items.index("cluster"+str(self.iter_n))
                except:
                    cluster_i = 0#如果没有cluster就分所有的
                isheader = not isheader
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

        name_train, X_train = self.name_feature_split(X_train)
        name_test, X_test = self.name_feature_split(X_test)

        self.classifer.fit(X_train, Y_train)
        Y_predict = self.classifer.predict(X_test)
        s = self.classifer.score(X_test, Y_test)
        print "Precision:%0.3f\n"%s
        self.log["test_precision"] = s
        if s < self.lowest_accuracy:
            raise LowAccuracy(s)

        train = dict((name_train[i], Y_train[i]) for i in range(len(name_train)))
        test = dict((name_test[i], Y_test[i]) for i in range(len(name_test)))
        test_result = dict((name_test[i], Y_predict[i]) for i in range(len(name_test)))

        self.record_result(self.train_file, [("class",train)])
        self.record_result(self.test_file, [("class",test)])
        self.record_result(self.test_result_file, [("flag",test),("class",test_result)])

    def predict(self, X_predict):
        """
        预测分类结果
        Args:
        -------------------
          X_predict: 预测数据的feature
        """

        return self.classifer.predict(X_predict)


if __name__=="__main__":
    import sys

    configs = read_properties(os.path.join(BASEDIR, PROP_FILE))
    configs.update(read_properties(os.path.join(BASEDIR, NAME_FILE)))
    configs.update(read_properties(os.path.join(BASEDIR, PATH_FILE)))

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--iter", dest="iter", type="int", help="Iteration of Classify", default=-1)
    parser.add_option("-f", "--featureid", dest="featureid", type="int", help="Feature id", default=configs["featureid"])
    parser.add_option("-a", "--lowest_accuracy", dest="lowest_accuracy", type="float", help="Lowest test accuracy. If result is lower than it, stop", default=configs["lowest_accuracy"])

    (options, args) = parser.parse_args()

    if not options.iter or options.iter < 0:
        print "Need Iteration Num for Argument"
        exit()

    configs.update(vars(options))
         
    iter_n = str(configs['iter'])

    import time
    start = time.time()

    data_file = os.path.join(RESULT_PATH,configs["result"].replace('Y',str(configs["featureid"])))
    classify_train= os.path.join(RESULT_PATH, configs["classify_train"].replace('Y',str(configs["featureid"])).replace('X',str(iter_n)))
    classify_test= os.path.join(RESULT_PATH, configs["classify_test"].replace('Y', str(configs["featureid"])).replace('X',str(iter_n)))
    classify_predict= os.path.join(RESULT_PATH, configs["classify_predict"].replace('Y', str(configs["featureid"])).replace('X',str(iter_n)))
    classify_test_result= os.path.join(RESULT_PATH, configs["classify_test_result"].replace('Y',str(configs["featureid"])).replace('X',str(iter_n)))
    classify_test_statistics= os.path.join(RESULT_PATH, configs["classify_test_statistics"].replace('Y',str(configs["featureid"])).replace('X', str(iter_n)))
    log = os.path.join(LOG_PATH, configs["classify_log"].replace('Y', str(configs['featureid'])))

    svm = SVM(data_file, configs)
    try:
        svm.run(classify_train, classify_test, classify_predict, classify_test_result, classify_test_statistics,log,iter_n)
    except Exception,e:
        print e

    print "Time Consuming:%3f"%(time.time()-start)
        
