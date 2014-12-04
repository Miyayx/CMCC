#/usr/bin/python2.7
#encoding=utf-8

import codecs

def read_class_file(fn):
    sample_class = {}
    with open(fn) as f:
        line = f.readline()
        while line:
            ls = line.strip("\n").split("\t\t")
            sample_class[ls[1]] = ls[2]
            line = f.readline()
        return sample_class

def read_feature_file(fn):
    sample_feature = {}
    with open(fn) as f:
        colname = f.readline().strip("\n")
        line = f.readline()
        while line:
            ls = line.strip("\n").split(",",1)
            sample_feature[ls[0]] = ls[1]
            line = f.readline()
        return colname, sample_feature

def write_classify_dataset(sample_class,sample_feature,colname, allfile, trainfile, testfile):
    d = {}
    train = {}
    test = {}

    colname= colname.strip("\n")+",class\n"

    for s,c in sample_class.items():
        if not d.has_key(c):
            d[c] = []
        d[c].append(s)
    for c,l in d.items():
        i = len(l)*2/3
        import random
        train[c] = random.sample(l,i)
        test[c] = random.sample(l,len(l)-i)
    write_classify(sample_feature, allfile, colname, d)
    write_classify(sample_feature, trainfile, colname,train)
    write_classify(sample_feature, testfile, colname,test)

def write_classify(sample_feature, fn, colname, d, code="utf-8"):
    with codecs.open(fn, "w") as f:
        f.write(colname)
        for c,l in d.items():
            for s in l:
                f.write(s+","+sample_feature[s]+","+c+"\n")

if __name__=="__main__":
    sample_class = read_class_file("../etc/correctInstance.txt")
    colname,sample_feature = read_feature_file("../etc/features1.csv")
    write_classify_dataset(sample_class, sample_feature, colname, "../etc/all_data_f1.csv","../etc/train2_f1.csv","../etc/test2_f1.csv")
            
