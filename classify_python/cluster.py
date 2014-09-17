#!/usr/bin/python2.7
#encoding=utf-8

import numpy as np
from sklearn.cluster import KMeans
from sklearn import metrics
from sklearn.metrics.pairwise import euclidean_distances
import time
import codecs

from utils import *
from csvio import CSVIO
from config_global import *
from centroids import *

class KMEANS:

    def __init__(self, data_file, k=-1, init='k-means++'):
        props = read_properties(PROP_FILE)
        props.update(read_properties(COL_FILE))

        self.feature_count = int(props["feature_count"])
        self.k = int(props["cluster_num"]) if int(k) < 0 else k
        self.k = int(self.k)
        self.min_cluster = int(props["min_cluster_num"])
        self.max_cluster = int(props["max_cluster_num"])

        self.data_file = data_file
        self.init = init

    def run(self, result_file, iter_n):
        self.result_file = result_file
        self.iter_n = iter_n 

        self.names,self.X = self.get_data(self.data_file)

        write_lines(props["neg_file"], self.names)
        
        if self.k < 0:
            self.k = self.calculate_k(self.X, self.init)

        sample_label, coef = self.cluster(self.X, self.k, self.init)
        csv = CSVIO(self.data_file)
        s2sl = s2bl = None
        if "section label" in csv.fields:
            s2sl = csv.read_one_to_one(0, csv.fields.index("section label"))
        if "block label" in csv.fields:
            s2bl = csv.read_one_to_one(0, csv.fields.index("block label"))
        self.record_result(self.result_file, sample_label, s2sl, s2bl )
        self.append_result(self.data_file, sample_label)

    def get_data(self, data_file):
        data = {}
        names = []
        X = [] 
        begin = 2
        end = 0
        classify_i = 0
        for line in codecs.open(data_file,'r','utf-8'):
            line = line.strip("\n").split(",")
            if not line[3].isdigit():
                end = line.index("sample2")
                if int(self.iter_n) > 1:
                    classify_i = line.index("class"+str(int(self.iter_n)-1))
                continue
            if classify_i > 0:
                if line[classify_i] == "others":
                    data[line[0]] = [float(i) for i in line[begin:end]]
            else:
                data[line[0]] = [float(i) for i in line[begin:end]]
                #X.append([int(i) for i in line[begin:end]])
                #names.append(line[0])

        data = sorted(data.items(), key=lambda x: x[0])
        names = [d[0] for d in data]
        X = [d[1] for d in data]
        X = np.array(X)

        return names,X

    def append_result(self, fn, s2l):
        print "Add to "+fn
        colname = "cluster"+self.iter_n
        csv = CSVIO(fn)
        #csv.load(fn)
        csv.column(colname, s2l)
        csv.write(fn, ",", True, True, csv.fields.index(colname))
        #csv.write(fn, ",", True, True, 0)

    def record_result(self, fn, s2l, s2sl = None, s2bl = None ):
        print "Write to "+fn

        csv = CSVIO(fn,append = False)
        csv.column("sample", dict((s,s) for s in s2l.keys()))
        if s2sl:
            csv.column("section label", s2sl)
        if s2bl:
            csv.column("block label", s2bl)
        csv.column("cluster", s2l)
        csv.write(fn, ",", True, True, csv.fields.index("cluster"))

    def calculate_k(self, X, init):
        coef_dict = {}
        for k in range(self.min_cluster,self.max_cluster):
            if init == 'nbc':
                init = 'k-means++'
            r,coef = self.cluster(X, k, init)
            coef_dict[k] = coef
        for k,v in coef_dict.items():
            print k,v
        best_k = max(coef_dict.items(), key=lambda x:x[1])[0]
        print "best_k",best_k
        return best_k

    def init_centroids(self, X, k, init="k-means++"):
        if init == 'k-means++':
            return 'k-means++'
        else:
            centroids = []
            if init == 'even':
                centroids = CentroidCalculater(strategy=CentroidEven).calculate(X, k)
            elif init == 'spss':
                centroids = CentroidCalculater(strategy=CentroidSPSS).calculate(X, k)
            elif init == 'density':
                centroids = CentroidCalculater(strategy=CentroidDensity).calculate(X, k)
            elif init == 'nbc':
                centroids = CentroidCalculater(strategy=CentroidNBC).calculate(X, k)
            else:
                raise ValueError("the init parameter for the k-means should be 'k-means++' or 'even' or 'spss' or 'density' or 'nbc' ,'%s' (type '%s') was passed." % (init, type(init)))

            init_c = [X[c] for c in centroids]
            init_c = np.array(init_c)

            return np.array(init_c) 

    def cluster(self, X, k, init = 'k-means++', coef_dict = {}):

        print "k",k

        n = len(X)
        print "n",n,"\n"

        # Get centroids ndarray
        km = KMeans(init=self.init_centroids(X, k, init), n_clusters=k, n_init=1 )

        km.fit(X)
        labels = km.labels_
        
        sample_label = dict((self.names[i], str(labels[i])) for i in range(len(labels)))
            
        for i in range(k):
            print i,list(labels).count(i)
        #for i in range(len(labels)):
        #    if list(labels).count(labels[i]) > 1:
        #        print names[i],labels[i]

        coef = metrics.silhouette_score(X, labels, metric='sqeuclidean')
        print("Silhouette Coefficient: %0.3f\n"% coef)

        return sample_label, coef
        

if __name__=="__main__":
    import sys
    if len(sys.argv) < 2:
        print "Need Iteration Num for Argument"
         
    iter_n = sys.argv[1]
    init_c = 'k-means++'
    if len(sys.argv) == 3:
        if sys.argv[2].isdigit():
            k = int(sys.argv[2])
        else:
            k = -1
            init_c = sys.argv[2]

    if len(sys.argv) == 4:
        k = int(sys.argv[2])
        init_c = sys.argv[3]


    import time
    start = time.time()

    props = read_properties(PROP_FILE)
    props.update(read_properties(NAME_FILE))
    props["file_path"] = "../"+props["file_path"].strip("/")+"/"

    data_file = props["file_path"]+props["result"].replace('Y',props["featureid"])
    cluster_result = props["file_path"]+props["cluster_result"].replace('Y',props["featureid"]).replace('X',iter_n)
    km = KMEANS(data_file, k, init_c)
    km.run(cluster_result,iter_n)

    print "Time Consuming:",(time.time()-start)

