#!/usr/bin/python2.7
#-*-coding:utf-8-*-

import numpy as np
from sklearn.cluster import KMeans
from sklearn import metrics
from sklearn.metrics.pairwise import euclidean_distances
import time
import codecs
import os

from utils import *
from csvio import CSVIO
from global_config import *
from centroids import *

class KMEANS:

    def __init__(self, data_file, props):
        """
        Args
        ------------------------------
        data_file:
            feature file
        k
        init:
            method for centroids
        """

        self.k = int(props["k"]) 
        self.min_cluster = int(props["min_cluster_num"])
        self.max_cluster = int(props["max_cluster_num"])

        self.data_file = data_file
        self.init = props['init']
        self.centroids = []
        self.all_centroids = {}

        self.log = {}

    def run(self, result_file, log_file,  iter_n):
        """
        Args
        --------------------------------
        result_file:
            record cluster result in clusterX_fY_result.csv, only include sample and cluster number
        log_file:
            统计数据记录文件
        iter_n:
            iteration number
            
        """
        start = time.time()

        self.result_file = result_file
        self.iter_n = iter_n 

        self.names,self.X = self.get_data(self.data_file)

        # record others sample
        write_lines(props["neg_file"], self.names)
        
        if self.k < 0: #如果k为-1，即没有指定k值，则计算k出来
            self.k = self.calculate_k(self.X, self.init)

        sample_label, coef = self.cluster(self.X, self.k, self.init)

        csv = CSVIO(self.data_file)
        s2sl = s2bl = s2th = None
        if "section label" in csv.fields: #write section label in big table
            s2sl = csv.read_one_to_one(0, csv.fields.index("section label"))
        if "block label" in csv.fields: #write block label in big table
            s2bl = csv.read_one_to_one(0, csv.fields.index("block label"))
        if "table header" in csv.fields: #write table header in big table
            s2th = csv.read_one_to_one(0, csv.fields.index("table header"))
        # write to cluster result file
        self.record_result(self.result_file, sample_label, s2sl, s2bl, s2th )
        # write to big table file
        self.append_result(self.data_file, sample_label)

        t = time.time()-start
        self.log["sample_number"] = len(self.names)
        self.log["k"] = self.k
        self.log["centroid_method"] = self.init
        self.log["time_consuming"] = t

        self.record_log(log_file)

        print "Time Consuming:",t

    def record_log(self, log_file):
        """
        
        """
        csv = CSVIO(log_file)
        if not os.path.isfile(log_file):
            csv.column("type", dict((s,s) for s in self.log.keys()))
        csv.column("Iter"+str(self.iter_n), self.log)
        csv.write(log_file, ",", True, True )

    def get_data(self, data_file):
        """
        读取大表，获得特征向量与对应sample id
        Returns:
        -----------------------------------
        names: sampleid list
        X    : 特征数组
        """

        data = {}
        names = []
        X = [] 
        begin = 2
        end = 0
        classify_i = 0
        for line in codecs.open(data_file,'r','utf-8'):
            line = line.strip("\n").split(",")
            if not line[3].isdigit():
                end = line.index("sample2") #以sample2列为截止列
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
        """
        Write to big table file
        """
        print "Add to "+fn
        colname = "cluster"+self.iter_n
        csv = CSVIO(fn)
        #csv.load(fn)
        csv.column(colname, s2l)
        csv.write(fn, ",", True, True, csv.fields.index(colname))
        #csv.write(fn, ",", True, True, 0)

    def record_result(self, fn, s2l, s2sl = None, s2bl = None, s2th = None ):
        """
        Write to cluster result file
        """
        print "Write to "+fn

        csv = CSVIO(fn,append = False)
        csv.column("sample", dict((s,s) for s in s2l.keys()))
        if s2sl:
            csv.column("section label", s2sl)
        if s2bl:
            csv.column("block label", s2bl)
        if s2th:
            csv.column("table header", s2th)
        csv.column("cluster", s2l)
        csv.write(fn, ",", True, True, csv.fields.index("cluster"))

    def calculate_k(self, X, init):
        """
        计算合适的k, 从min_cluster 到max_cluster进行测试,选取Silhouette Coefficient最大的
        X:
            feature 
        init:
            计算centroids的算法
        """
        coef_dict = {}
        for k in range(self.min_cluster,self.max_cluster):
            if init == 'nbc' and len(self.X) > 1000: #数据量很大的时候用k-means++
                init = 'k-means++'
            r,coef = self.cluster(X, k, init)
            coef_dict[k] = coef
        for k,v in coef_dict.items():
            print k,v
        best_k = max(coef_dict.items(), key=lambda x:x[1])[0]
        print "best_k",best_k
        return best_k

    def init_centroids(self, X, k, init="k-means++"):
        """
        计算初始centroid
        """
        print "Init centroids strategy:",init
        if init == 'k-means++':
            return 'k-means++'
        if init == "density" and self.centroids: #对density方法，只算一次
            init_c = [X[c] for c in self.centroids[:k]]
            init_c = np.array(init_c)
            return np.array(init_c) 
        else:
            self.centroids = []
            if init == 'even':
                self.centroids = CentroidCalculater(strategy=CentroidEven).calculate(X, k)
            elif init == 'spss':
                self.centroids = CentroidCalculater(strategy=CentroidSPSS).calculate(X, k)
            elif init == 'density':
                num = max(self.max_cluster, k) if self.max_cluster else k
                self.centroids = CentroidCalculater(strategy=CentroidDensity).calculate(X, num)
            elif init == 'nbc':
                self.centroids = CentroidCalculater(strategy=CentroidNBC).calculate(X, k)
            else:
                raise ValueError("the init parameter for the k-means should be 'k-means++' or 'even' or 'spss' or 'density' or 'nbc' ,'%s' ('%s') was passed." % (init, type(init)))

            init_c = [X[c] for c in self.centroids[:k]]
            init_c = np.array(init_c)

            return np.array(init_c) 

    def cluster(self, X, k, init = 'k-means++', coef_dict = {}):
        """
        """

        print "k",k

        n = len(X)
        print "n",n,"\n"

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

    props = read_properties(os.path.join(BASEDIR, PROP_FILE))
    props.update(read_properties(os.path.join(BASEDIR, NAME_FILE)))
    props.update(read_properties(os.path.join(BASEDIR, PATH_FILE)))

    props['k'] = -1
    props['init'] = 'k-means++'

    if len(sys.argv) < 2:
        print "Need Iteration Num for Argument"
        exit()
    else:
        if sys.argv[1].isdigit() or sys.argv[1]=='-iter':
            if sys.argv[1].isdigit():
                sys.argv.insert(1, '-iter')
            props.update(parse_argv(sys.argv))
        else:
            print "Need Iteration Num for Argument"
            exit()

    iter_n = str(props['iter'])
    if not props.has_key('k'):
        print "Need Cluster Num k for argument: -k 3"
        exit()

    data_file = os.path.join(RESULT_PATH, props["result"].replace('Y',str(props["featureid"]))) #大表
    log = os.path.join(LOG_PATH, props["cluster_log"].replace('Y', str(props['featureid'])))
    cluster_result = os.path.join(RESULT_PATH, props["cluster_result"].replace('Y',str(props["featureid"])).replace('X',str(iter_n)))

    km = KMEANS(data_file, props)
    km.run(cluster_result, log, iter_n)


