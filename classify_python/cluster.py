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

class KMEANS:

    def __init__(self, data_file, k=-1):
        props = read_properties(PROP_FILE)
        props.update(read_properties(COL_FILE))

        self.feature_count = int(props["feature_count"])
        self.k = int(props["cluster_num"]) if int(k) < 0 else k
        self.k = int(self.k)
        self.min_cluster = int(props["min_cluster_num"])
        self.max_cluster = int(props["max_cluster_num"])

        self.data_file = data_file

    def run(self, result_file, iter_n):
        self.result_file = result_file
        self.iter_n = iter_n 

        self.names,self.X = self.get_data(self.data_file)

        write_lines(props["neg_file"], self.names)
        
        if self.k < 0:
            self.k = self.calculate_k(self.X)

        sample_label, coef = self.cluster(self.X, self.k)
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
            if not line[2].isdigit():
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

    def calculate_k(self, X):
        coef_dict = {}
        for k in range(self.min_cluster,self.max_cluster):
            r,coef = self.cluster(X, k)
            coef_dict[k] = coef
        for k,v in coef_dict.items():
            print k,v
        best_k = max(coef_dict.items(), key=lambda x:x[1])[0]
        print "best_k",best_k
        return best_k

    def calculate_centroid(self, X, k):
        """
        Algorithm From Paper: Single Pass Seed Selection Algorithm for k-Means 
        """
        centroids = []

        n = len(X)
        
        print len(X),len(X[0])
        dis = euclidean_distances(X, X)
        print "dis",len(dis),len(dis[0])
        s_dis = sum(dis)

        first = list(s_dis).index(max(s_dis))
        centroids.append(first)

        #maxv = sorted(dis[first], reverse=True)

        #y = sum([m for m in maxv if m > 0][:int(n/k)])

        #print "y =",y
        
        #for i in range(0,k):
        #    D = [0 for j in range(n)]
        #    for j in range(0,n):
        #        D[j] = max([dis[j][c] for c in centroids])

        #    D = sorted(D, reverse=True)
        #    y = sum(D[:int(n/k)])
        #    print "y =",y

        #    DD = sorted([D[j]**2 for j in range(len(D))])

        #    for j in range(0,n):
        #        if sum(DD[:j]) >= y and y > sum(DD[:j-1]) and j not in centroids:
        #            centroids.append(j)
        #            break
        
        #first = list(s_dis).index(min(s_dis))
        #print first
        #centroids.append(first)
        #minv = sorted(dis[first])
        #s = 0
        #for j in range(n/k):
        #    s += minv[j]
        #y = s
        #print "y =",y
        
        print centroids
        for i in range(1,k):
            D = [0 for j in range(n)]
            for j in range(0,n):
                D[j] = min([dis[j][c] for c in centroids])

            y = sum(sorted([d for d in D if d > 0])[:int(n/k)])

            s = 0
            for j in range(n):
                old_s = s
                s += (D[j]**2)
                if s >= y and y > old_s:
                    centroids.append(j)
                    break

       # for i in range(1,k):
       #     D = [0 for j in range(n)]
       #     for j in range(0,n):
       #         D[j] = sum([dis[j][c] for c in centroids])

       #     candidates = [D.index(m) for m in sorted(D, reverse=True)[:k]]
       #     min_sum = [sum(sorted(dis[c])[:int(n/k)]) for c in candidates]
       #     c = candidates[min_sum.index(min(min_sum))]

       #     centroids.append(c)
        

        print "Centroids:",centroids
        return centroids

    def cluster(self, X, k, coef_dict = {}):

        print "k",k

        n = len(X)
        print "n",n,"\n"

        # Get centroids ndarray
        #centroids = self.calculate_centroid(X, k)
        #init_c = [X[c] for c in centroids]
        #init_c = np.array(init_c)
        #km = KMeans(init=init_c, n_clusters=k )

        km = KMeans(init='k-means++', n_clusters=k, max_iter = 1000)
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
    if len(sys.argv) == 3:
        k = sys.argv[2]
    else:
        k = -1
    import time
    start = time.time()

    props = read_properties(PROP_FILE)
    props.update(read_properties(NAME_FILE))
    props["file_path"] = "../"+props["file_path"].strip("/")+"/"

    data_file = props["file_path"]+props["result"].replace('Y',props["featureid"])
    cluster_result = props["file_path"]+props["cluster_result"].replace('Y',props["featureid"]).replace('X',iter_n)
    km = KMEANS(data_file, k)
    km.run(cluster_result,iter_n)

    print "Time Consuming:",(time.time()-start)

