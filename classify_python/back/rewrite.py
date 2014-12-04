#!/usr/bin/python
#encoding=utf-8

from csvio import *

csv = CSVIO("../../data/Classify/result_features1.csv")
for i in range(10,11):
    cluster = CSVIO("../../data/Classify/cluster%d_f1_result.csv"%i)
    s_c = cluster.read_one_to_one(0,3)
    csv.column("cluster%d"%i, s_c)
    train = CSVIO("../../data/Classify/classify%d_f1_train.csv"%i)
    s_tr = train.read_one_to_one(0,1)
    test = CSVIO("../../data/Classify/classify%d_f1_test.csv"%i)
    s_te = test.read_one_to_one(0,1)
    s_a = s_tr
    s_a.update(s_te)
    csv.column("flag%d"%i, s_a)
    predict = CSVIO("../../data/Classify/classify%d_f1_predict.csv"%i)
    s_p = predict.read_one_to_one(0,1)
    s_a.update(s_p)
    csv.column("class%d"%i, s_a)
    csv.write("../../data/Classify/result_features1.csv")

    

