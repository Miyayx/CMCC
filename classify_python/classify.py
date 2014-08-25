
#!/usr/bin/python2.7
#encoding=utf-8

import numpy as np
from sklearn import svm
from sklearn import cross_validation
import time
import codecs

from utils import *
from csvio import CSVIO
from config_global import *

class SVM:

    def __init__(self, data_file):
        props = read_properties(PROP_FILE)
        props.update(read_properties(COL_FILE))

        self.feature_count = int(props["feature_count"])
        self.train_test_ratio = 2.0/1
        self.classifer = svm.SVC(kernel='linear', C=1)

        self.data_file = data_file

    def run(self, train_file, test_file, predict_file, test_result_file, test_statistic, iter_n):

        self.iter_n = iter_n 

        self.train_file = train_file
        self.test_file = test_file
        self.predict_file = predict_file
        self.test_result_file = test_result_file
        self.test_statistic = test_statistic

        X_flag, Y_flag, predict = self.get_data(self.data_file)

        self.train_test(X_flag, Y_flag)

        name_predict, X_predict = self.name_feature_split(predict)
        name_flag, X_flag = self.name_feature_split(X_flag)

        Y_predict = self.predict(X_predict)

        result = dict((name_predict[i], Y_predict[i]) for i in range(len(name_predict)))
        flag = dict((name_flag[i], Y_flag[i]) for i in range(len(name_flag)))
        
        csv = CSVIO(self.data_file)
        s2sl = csv.read_one_to_one(0, csv.fields.index("section label"))
        s2bl = csv.read_one_to_one(0, csv.fields.index("block label"))
        self.record_result(self.predict_file, [("class",result), ("section label",s2sl),("block label", s2bl)])
        result.update(flag)
        self.append_result(self.data_file, result)

    def name_feature_split(self, data):
        name = []
        feature = []
        for d in data:
            name.append(d[0])
            feature.append(d[1:])
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
                continue
            if len(items[flag_i]) > 1:
                X_flag.append([i for i in items[begin:end]])
                Y_flag.append(items[flag_i])
            else:
                predict.append([i for i in items[begin:end]])
        print "Flag all:",len(Y_flag)
        print "Predict all:",len(predict)

        return X_flag, Y_flag, predict

    def append_result(self, fn, s2l):
        print "Add to "+fn
        colname = "class"+self.iter_n
        csv = CSVIO(fn)
        csv.column(colname, s2l)
        csv.write(fn, ",", True, True, csv.fields.index(colname))

    def record_result(self, fn, columns = [] ):
        print "Write to "+fn

        csv = CSVIO(fn,append = False)
        csv.column("sample", dict((s,s) for s in columns[0][1].keys()))
        for colname, col in columns:
             csv.column(colname, col)
        csv.write(fn, ",", True, True)

    def write_statistic(self, fn, Y_test, Y_predict, score):
        import annotation
        c = annotation.read_config(ANNOTATION_FILE)
        neg = c["neg_class"]
        pos_pos = pos_neg = neg_pos = neg_neg = 0
        for i in range(len(Y_test)):
            if not Y_test[i] == neg and not Y_predict[i] == neg:
                pos_pos += 1
            elif not Y_test[i] == neg and Y_predict == neg:
                pos_neg += 1
            elif Y_test[i] == neg and not Y_predict[i] == neg:
                neg_pos += 1
            elif Y_test[i] == neg and Y_predict[i] == neg:
                neg_neg += 1

        print "    Pos   Neg"
        print "Pos %4d %4d"%(pos_pos, pos_neg)
        print "Neg %4d %4d"%(neg_pos, neg_neg)
        print "Precision:%0.3f\n"%score

        with open(fn, "w") as f:
            f.write("    Pos   Neg\n")
            f.write("Pos %4d %4d\n"%(pos_pos, pos_neg))
            f.write("Neg %4d %4d\n"%(neg_pos, neg_neg))
            f.write("\n")
            f.write("Precision:%0.3f"%score)

    def train_test(self, X_flag, Y_flag):

        X_train, X_test, Y_train, Y_test = cross_validation.train_test_split(np.array(X_flag), np.array(Y_flag), test_size=1.0/(self.train_test_ratio+1), random_state=0)
        print "Train all:",len(Y_train)
        print "Test all:",len(Y_test)

        name_train, X_train = self.name_feature_split(X_train)
        name_test, X_test = self.name_feature_split(X_test)

        self.classifer.fit(X_train, Y_train)
        Y_predict = self.classifer.predict(X_test)
        s = self.classifer.score(X_test, Y_test)

        train = dict((name_train[i], Y_train[i]) for i in range(len(name_train)))
        test = dict((name_test[i], Y_test[i]) for i in range(len(name_test)))
        test_result = dict((name_test[i], Y_predict[i]) for i in range(len(name_test)))

        self.record_result(self.train_file, [("class",train)])
        self.record_result(self.test_file, [("class",test)])
        self.record_result(self.test_result_file, [("flag",test),("class",test_result)])
        self.write_statistic(self.test_statistic, Y_test, Y_predict, s)
            

    def predict(self, X_predict):

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

    svm = SVM(data_file)
    svm.run(classify_train, classify_test, classify_predict, classify_test_result, classify_test_statistics,iter_n)

    print "Time Consuming:",(time.time()-start)
        