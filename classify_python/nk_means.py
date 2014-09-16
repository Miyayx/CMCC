#!/usr/bin/python
#encoding=utf-8

"""
Referrence:
1. A Neighborhood-Based Clustering Algorithm
2. Neighborhood Density Method for Selecting Initial Cluster Centers in K-Means Clustering
"""

import sys
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

import matplotlib.pyplot as plt

from sklearn import datasets
from sklearn.cluster import KMeans
from mpl_toolkits.mplot3d import Axes3D
from itertools import cycle
import pylab as pl

from sklearn.decomposition import PCA


def plot_2D(data, target, target_names, p_list=None):
    target = np.array(target)
    colors = cycle('rgbcmykw')
    target_ids = range(len(target_names))
    pl.figure()
    for i, c, label in zip(target_ids, colors, target_names):
        pl.plot(data[target == i, 0],
        data[target == i, 1], 'o',c=c, label=label)
        pl.legend(target_names)
    if p_list:
        for p in p_list:
            i = p.id_
            #pl.text(data[i][0],data[i][1],"%.3f"%p.NDF)
            pl.text(data[i][0], data[i][1], p.id_)

class point:
    
    def __init__(self, id_):
        self.id_ = id_


def kNB(X, k_nbc, p_list):

    dis = euclidean_distances(X, X)

    for p in p_list:
        i = p.id_
        id_x = zip([j for j in range(len(dis[i]))], dis[i])
        id_x.pop(i)
        l = sorted(id_x, key=lambda x: x[1])
        r = l[k_nbc-1][1]
        knbs = [id_x[j][0] for j in range(len(id_x)) if id_x[j][1] <= r]
        p.kNB = knbs

    return p_list

def R_kNB(p_list):

    RkNBs = [[] for i in range(len(p_list))]

    for p in p_list:
        for j in p.kNB:
            RkNBs[j] = RkNBs[j] + [p.id_]

    for p in p_list:
        p.RkNB = RkNBs[p.id_]

    return p_list

def NDF(p_list):

    for p in p_list:
        p.NDF = len(p.RkNB) * 1.0 / len(p.kNB)

    return p_list 

def NBC(X, k_nbc, p_list):

    p_list = kNB(X, k_nbc, p_list)
    p_list = R_kNB(p_list)
    p_list = NDF(p_list)

    for p in p_list:
        p.cluster = -1

    count = 0

    for p in p_list:

        #pca = PCA(n_components=2, whiten=True).fit(X)
        #X_pca = pca.transform(X)

        #if p.cluster >= 0 or p.NDF < 1: 
        if p.cluster >= 0: #不要离群点
            continue
        p.cluster = count # A new cluster

        dp_set = []
        for j in p.kNB:
            q = p_list[j]
            if q.cluster > -1:
                continue
            q.cluster = count

            if q.NDF >= 1:
                dp_set.append(q)

        while len(dp_set) > 0:
            m = dp_set.pop()
            for j in m.kNB:
                q = p_list[j]
                if q.cluster > -1:
                    continue
                q.cluster = count
                if q.NDF >= 1:
                    dp_set.append(q)

        #plot_2D(X_pca, [p.cluster for p in p_list], [i for i in range(count)], p_list)
        #plt.show()

        count += 1

    return p_list
        
def calculate_knbc():
    pass

def merge_cluster(X, k, cluster_p):
    """
    Merge NBC result to k clusters according to distance between current clusters.

    Args
    X : ndarray
        feature array
    k : int
        the number of cluster wanted finally
    cluster_p : list of list
        collection of cluster points, index means cluster id, item means list of points of this cluster

    Returns
        
    """

    def get_center_and_radius(ps):
        x = [X[p] for p in ps]
        z = np.mean(x, axis=0)
        dis = euclidean_distances(x, z)
        r = np.max(dis) 

        return z, r

    c_num = len(cluster_p)
    print "c_num",c_num

    r = [0 for i in range(c_num)]
    z = [0 for i in range(c_num)]

    for c in range(c_num): 
        print c,len(cluster_p[c])

    for c in range(c_num):
        ps = cluster_p[c]
        z[c], r[c] = get_center_and_radius(ps)

    d_c = [[sys.maxint for i in range(c_num)] for i in range(c_num)]
    for i in range(c_num):
        for j in range(i):
            if i == j:
                d_c[i].insert(j, np.inf)
            else: #calculate triangle matrix
                d = euclidean_distances(z[i], z[j])/(r[i] + r[j] + 1)
                d_c[i][j] = d
                d_c[j][i] = d

    while len(cluster_p) > k:
    #while len(cluster_p) < k:

        c_num = len(cluster_p)
        print "c_num",c_num

        min_d = np.min(np.min(d_c, 1))
        c_i = list(np.min(d_c,1)).index(min_d)
        c_j = list(d_c[c_i]).index(min_d)
        

        # merge i and j to i
        cluster_p[c_i] = cluster_p[c_i] + cluster_p[c_j]
        #print "merge:",c_i,c_j
        cluster_p.pop(c_j)

        z.pop(c_j)
        r.pop(c_j) 
        # recalculate the new center and radius
        #print "r len",len(r)
        #print "z len",len(z)
        #print "c len",len(cluster_p)
        #print "c_i",c_i
        #print "c_j",c_j
        z[c_i], r[c_i] = get_center_and_radius(cluster_p[c_i])
        for j in range(len(d_c)):
            d_c[j].pop(c_j)

        d_c.pop(c_j)

        #recalculate distance between cluster i and others
        c_num = len(cluster_p)
        for j in range(c_num):
            d = euclidean_distances(z[c_i], z[j])/(r[c_i] + r[j] + 1)
            if str(d[0][0]) == "nan":
                d = np.inf
            d_c[c_i][j] =  d
            d_c[j][c_i] =  d

    print cluster_p
    return cluster_p
    

def calculate_centroid(X, k):
    print "k",k
    n = len(X)
    p_list = [point(i) for i in range(n)]

    #pca = PCA(n_components=2, whiten=True).fit(X)
    #X_pca = pca.transform(X)

    p_list = NBC(X, 10, p_list)
    c_num = len(set(p.cluster for p in p_list))

    #for p in p_list:
    #    print "point",p.id_
    #    print "kNB",p.kNB
    #    print "RkNB",p.RkNB
    #    print "NDF",p.NDF
    #    print "cluster", p.cluster
    #    print ""


    #plot_2D(X_pca, [p.cluster for p in p_list], [i for i in range(c_num)], p_list)
    #plt.show()

    cluster_p = [[] for i in range(c_num)]
    for p in p_list:
        cluster_p[p.cluster] = cluster_p[p.cluster] + [p.id_]
        #cluster_p[p.cluster] = cluster_p.get(p.cluster, []) + [p.id_] # -1 turn to 0

    cluster_p = merge_cluster(X, k, cluster_p)

    centroids = []
    for c in range(len(cluster_p)):
        ps = cluster_p[c]
        x = [X[p] for p in ps]
        z = np.mean(x, axis=0)
        dis = euclidean_distances(x, z)
        dis = np.transpose(dis)[0]
        ctd = list(dis).index(min(dis))
        centroids.append(ps[ctd])
    print centroids

    for c in range(len(cluster_p)):
        ps = cluster_p[c]
        for p in ps:
            p_list[p].cluster = c

    return centroids, p_list


if __name__=="__main__":

    # import some data to play with
    iris = datasets.load_iris()
    X = iris.data
    y = iris.target
    centroids, p_list = calculate_centroid(X, 3)
    print centroids
    for c in centroids:
        print y[c]
    init_c = [X[c] for c in centroids]
    init_c = np.array(init_c)


    #----------------------------------------------------------------------
    # First figure: PCA
    pca = PCA(n_components=2, whiten=True).fit(X)
    X_pca = pca.transform(X)
    plot_2D(X_pca, iris.target, iris.target_names)
    
    
    #estimators = {'k_means_iris_3': KMeans(n_clusters=3, init='k-means++'),
    #              #'k_means_iris_8': KMeans(n_clusters=8),
    #              'k_means_iris_bad_init': KMeans(n_clusters=3, n_init = 1,init=init_c)}

    #fignum = 1

    #for name, est in estimators.items():

    #    est.fit(X)
    #    labels = est.labels_

    #    plot_2D(X_pca, labels, ["c0", "c1", "c2"], p_list)

    for k in range(3,2,-1):
        centroids, p_list = calculate_centroid(X, k)
        print centroids
        init_c = [X[c] for c in centroids]
        init_c = np.array(init_c)
        km = KMeans(n_clusters=k, n_init=1, init = init_c)
        labels = km.fit(X).labels_
        print "num:",len(labels)

        plot_2D(X_pca, labels, [i for i in range(k)])

    #estimators = {'k_means_iris_3': KMeans(n_clusters=3),
    #              #'k_means_iris_8': KMeans(n_clusters=8),
    #              'k_means_iris_bad_init': KMeans(n_clusters=3, n_init = 1,init=init_c)}

    #fignum = 1
    #for name, est in estimators.items():
    #    fig = plt.figure(fignum, figsize=(4, 3))
    #    plt.clf()
    #    ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)

    #    plt.cla()
    #    print name
    #    est.fit(X)
    #    labels = est.labels_

    #    ax.scatter(X[:, 3], X[:, 0], X[:, 2], c=labels.astype(np.float))

    #    ax.w_xaxis.set_ticklabels([])
    #    ax.w_yaxis.set_ticklabels([])
    #    ax.w_zaxis.set_ticklabels([])
    #    ax.set_xlabel('Petal width')
    #    ax.set_ylabel('Sepal length')
    #    ax.set_zlabel('Petal length')
    #    fignum = fignum + 1

    ## Plot the ground truth
    #fig = plt.figure(fignum, figsize=(4, 3))
    #plt.clf()
    #ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)
    #
    #plt.cla()

    #for name, label in [('Setosa', 0),('Versicolour', 1),('Virginica', 2)]:
    #    ax.text3D(X[y == label, 3].mean(),
    #              X[y == label, 0].mean() + 1.5,
    #              X[y == label, 2].mean(), name,
    #              horizontalalignment='center',
    #              bbox=dict(alpha=.5, edgecolor='w', facecolor='w'))
    ## Reorder the labels to have colors matching the cluster results
    #y = np.choose(y, [1, 2, 0]).astype(np.float)
    #ax.scatter(X[:, 3], X[:, 0], X[:, 2], c=y)

    #ax.w_xaxis.set_ticklabels([])
    #ax.w_yaxis.set_ticklabels([])
    #ax.w_zaxis.set_ticklabels([])
    #ax.set_xlabel('Petal width')
    #ax.set_ylabel('Sepal length')
    #ax.set_zlabel('Petal length')


    plt.show()

