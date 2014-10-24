#!/usr/bin/python2.7
#encoding=utf-8

import numpy as np
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import KMeans
from sklearn import metrics
from sklearn.metrics.pairwise import euclidean_distances
import time

def calculate_centroids(X, k):

    n = len(X)

    centroids = []
    
    dis = euclidean_distances(X, X)
    s_dis = sum(dis)
    first = list(s_dis).index(min(s_dis))
    print first
    centroids.append(first)
    minv = sorted(dis[first])
    s = 0
    for j in range(n/k):
        s += minv[j]
    y = s
    print "y =",y
    
    for i in range(1,k):
        D = [0 for j in range(n)]
        for j in range(0,n):
            D[j] = min([dis[j][c] for c in centroids])
        s = 0
        for j in range(2,n):
            old_s = s
            s += (D[j]**2)
            if s >= y and y > old_s:
                centroids.append(j)
                break
    
    print "centroids:",centroids
    return centroids

def run(X,k):
    n = len(X)
    print "n",n
    print "k",k

    #Custom initial center
    centroids = calculate_centroids(X, k)
    init_c = [X[c] for c in centroids]
    init_c = np.array(init_c)
    km = KMeans(init=init_c, n_clusters=k)
    ###################################

    #Use kmeans++
    #km = KMeans(init='k-means++', n_clusters=k, max_iter=1000, n_init=1000)

    km.fit(X)
    labels = km.labels_
    
    label_sample = {}
    for i in range(len(labels)):
        l = labels[i]
        label_sample[l] = label_sample.get(l,[]) + [names[i]]
    
    for k,v in label_sample.items():
        for n in sorted(v):
            print n,k
        
    for i in range(k):
        print i,list(labels).count(i)

    #for i in range(len(labels)):
    #    if list(labels).count(labels[i]) > 1:
    #        print names[i],labels[i]
    
    coef_dict[k] = metrics.silhouette_score(X, labels, metric='sqeuclidean')
    print("Silhouette Coefficient: %0.3f"% coef_dict[k])

if __name__=="__main__":
    start = time.time()
    
    names = []
    X = [] 
    begin = 1
    end = 0
    for line in open("../../data/Classify/result_features1.csv"):
        if not line.split(",")[2].isdigit():
            end = line.split(",").index("sample2")
            continue
        X.append([int(i) for i in line.split(",")[begin:end]])
        names.append(line.split(",")[0])
    
    X = np.array(X)
    
    global coef_dict
    coef_dict = {}

    # Try the best k
    #for k in range(3,20):
    #    run(X,k)
    #for k,v in coef_dict.items():
    #    print k,v
    #best_k = min(coef_dict.items(), key=lambda x:x[1])[0]
    #print "best_k",best_k
    #run(X,best_k)

    #run(X,9)
    run(X,3)
    
    print "Time Consuming:",(time.time()-start)
