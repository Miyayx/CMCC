#!/usr/bin/python
#encoding=utf-8

import sys
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.decomposition import PCA
from sklearn import datasets
from sklearn.cluster import KMeans

"""
4 methods for centroid calculating
even, spss, density, nbc
"""

def plot_2D(data, target, target_names, p_list=None):
    """
    把feature降维成2维做出聚类结果图
    """
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from itertools import cycle
    import pylab as pl

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


def normalize(X):
    X = np.array(X)
    meanVals = np.mean(X, axis=0)  
    meanRemoved = X - meanVals #减去均值  
    stded = meanRemoved / np.std(X) #用标准差归一化  
    return stded

class CentroidCalculater(object):
    """
    运用策略模式，每次添加新的策略时请覆写calculate方法，并将新策略作为CentroidCalculater的参数传递进来
    """

    def __init__(self, strategy=None):

        if strategy:
           #get a handle to the object
           self.action = strategy() #创建新的策略实例
           
    def calculate(self, X, k):
        if(self.action):
            print type(self.action)
            return self.action.calculate(X, k) #使用策略算法
        else:
            raise UnboundLocalError('Exception raised, no strategyClass supplied to CentroidCalculater!')


class CentroidEven(object):

    def calculate(self, X, k):
        """
        Takes N, the number of points in the dataset, and uses the points at the indexes of the integer values of N/K, 2N/K, 3N/K and so on, as the initial center points, until reaching the points at (K-1)*N/K and finally N, the last point in the sorted data set. 
        """

        n = len(X)
        centroids = [(i*n)/k for i in range(k)]
        return centroids

class CentroidSPSS(object):

    def calculate(self, X, k):
        """
        An enhanced kmeans++ method
        Algorithm From Paper: Single Pass Seed Selection Algorithm for k-Means 
        """
        centroids = []

        n = len(X)
        
        print len(X),len(X[0])
        dis = euclidean_distances(X, X)
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

        #for i in range(1,k):
        #    D = [0 for j in range(n)]
        #    for j in range(0,n):
        #        D[j] = sum([dis[j][c] for c in centroids])
         
        #    candidates = [D.index(m) for m in sorted(D, reverse=True)[:k]]
        #    min_sum = [sum(sorted(dis[c])[:int(n/k)]) for c in candidates]
        #    c = candidates[min_sum.index(min(min_sum))]
         
        #    centroids.append(c)
        

        print "Centroids:",centroids
        return centroids

class CentroidDensity(object):
    """
    Reference:
    Algorithm From Paper: Clustering by fast search and find of density peaks
    The algorithm has its basis in the assumptions that cluster centers are surrounded by neighbors with lower local density and that they are at a relatively large distance from any points with a higher local density. For each data point i, we compute two quantities: its local density RHO and its distance DELTA from points of higher density. 
    """

    def __init__(self):
        pass

    def calculate_rho(self, dis, dc):
        """
        Basically, rho(i) is equal to the number of points that are closer than dc to point i. The algorithm is sensitive only to the relative magnitude of rho(i) in different points, implying that, for large data sets, the results of the analysis are robust with respect to the choice of dc .
        """
        assert self.N == len(dis)
        rho_arr = []
        for i in range(self.N):
            ps = [dis[i][j] for j in range(self.N) if dis[i][j] <= dc]
            rho_arr.append(len(ps))
        return rho_arr

    def calculate_delta(self, dis, rho_arr):
        """
        delta(i) is measured by computing the minimum distance between the point i and any other point with higher density
        """
        delta_arr = []
        for i in range(self.N):
            rho_j = []
            for j in range(self.N):
                if j == i:
                    continue
                if rho_arr[j] > rho_arr[i]:
                    rho_j.append(j)
            if len(rho_j) == 0: #the point with highest density
                delta = max(dis[i])
            else:
                delta = min([dis[i][j] for j in rho_j])
            delta_arr.append(delta)
        return delta_arr

    def estimate_dc(self, dis):

        tmp = []
        index = int(self.N * 0.1)
        for i in range(self.N):
            ttt = []
            for j in range(self.N):
                ttt.append(dis[i][j])
            ttt = sorted(ttt)
            tmp.append(ttt[index])
        tmp = sorted(tmp)
        dc = tmp[self.N/4]
        print "dc:",dc
        return dc

    def get_area(self, rho_arr, delta_arr):
        assert len(rho_arr) == len(delta_arr)
        return [rho_arr[i] * delta_arr[i] for i in range(len(rho_arr))]

    def get_slope(self, rho_arr, delta_arr):
        assert len(rho_arr) == len(delta_arr)
        return [(rho_arr[i]*1000/delta_arr[i])for i in range(len(rho_arr))]
        
    def calculate(self, X, k):

        self.X = X
        self.k = k
        self.N = len(X)

        print "Calculating centroids..."
        centroids = []
        
        print "Sample:", len(self.X)
        dis = euclidean_distances(self.X, self.X)
        dc = self.estimate_dc(dis)
        rho_arr = self.calculate_rho(dis, dc)
        rho_arr = normalize(rho_arr)
        #print "rho:",rho_arr
        delta_arr = self.calculate_delta(dis, rho_arr)
        delta_arr = normalize(delta_arr)
        #print "delta_arr:",delta_arr
        area_arr = self.get_area(rho_arr, delta_arr)
        slope_arr = self.get_slope(rho_arr, delta_arr)

        instances = [(i, area_arr[i], slope_arr[i]) for i in range(self.N)]

        #get appropriate slope range
        slope_arr = sorted(slope_arr)
        i = self.N/4
        low_slope = slope_arr[i]
        high_slope = slope_arr[-i]

        # sorted by area
        instances = sorted(instances, key=lambda x:x[1], reverse = True)

        #选取rho和delta尽可能大的点，即area大的点。但slope要在一定范围内，否则可能会出现某一值很大，另一值很小的情况
        tmp = 0
        for ins in instances:
            s = ins[2] # get slope
            a = ins[1]
            if tmp == a:
                continue
            if s > low_slope and s < high_slope:
                centroids.append(ins[0])
                tmp = a
            if len(centroids) == self.k:
                break

        print "Centroids:",centroids
        return centroids


class point:
    """
    记录每个点的中间值
    """
    
    def __init__(self, id_):
        self.id_ = id_

class CentroidNBC(object):

    """
    Referrence:
    1. A Neighborhood-Based Clustering Algorithm
    2. Neighborhood Density Method for Selecting Initial Cluster Centers in K-Means Clustering
    """

    def kNB(self, X, k_nbc, p_list):
        """
        kNB(p) is the set of p’s k-nearest neighbor points
        """
    
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
    
    def R_kNB(self, p_list):
        """
        R−kNB(p) is the set of the reverse k-nearest neighbor points of p. R−kNB(p) is defined as the set of points whose k-nearest neighborhoods contain p
        """
    
        RkNBs = [[] for i in range(len(p_list))]
    
        for p in p_list:
            for j in p.kNB:
                RkNBs[j] = RkNBs[j] + [p.id_]
    
        for p in p_list:
            p.RkNB = RkNBs[p.id_]
    
        return p_list
    
    def NDF(self, p_list):
        """
        Neighborhood Density Factor
        defined as |R-kNB(p)| / |kNB(p)|
        The value of NDF (p) measures the local density of the object p
        Generally speaking, NDF (p) > 1 indicates that p is located in a dense area. NDF (p) < 1 indicates that p is in a sparse area. If NDF (p) = 1, then p is located in an area where points are evenly distributed in space.
        """
    
        for p in p_list:
            p.NDF = len(p.RkNB) * 1.0 / len(p.kNB)
    
        return p_list 
    
    def NBC(self, X, k_nbc, p_list):
        """
        NBC Cluster result 
        Reference:
            A Neighborhood-Based Clustering Algorithm
        """
    
        p_list = self.kNB(X, k_nbc, p_list)
        p_list = self.R_kNB(p_list)
        p_list = self.NDF(p_list)
    
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
            

    def merge_cluster(self, X, k, cluster_p):
        """
        Merge NBC result to k clusters according to distance between current clusters. Merge the nearest pair each time
    
        Args
        X : ndarray
            feature array
        k : int
            the number of cluster wanted finally
        cluster_p : list of list
            collection of cluster points, index means cluster id, item means list of points of this cluster
    
        Returns
        cluster_p:
            Merge result, key: cluster_id, value: point list
            
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
        
    def calculate(self, X, k):
        print "k",k
        n = len(X)
        p_list = [point(i) for i in range(n)]
    
        #pca = PCA(n_components=2, whiten=True).fit(X)
        #X_pca = pca.transform(X)
    
        #使用NBC算法先聚出多个类
        p_list = self.NBC(X, 10, p_list)
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
    
        #如果簇数大于k，合并相近的簇直到簇数等于k
        cluster_p = self.merge_cluster(X, k, cluster_p)
    
        # 将簇的中心点作为聚类中心，计算距离聚类中心最近的点作为centroid
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
    
        return centroids


if __name__=="__main__":
    from sklearn import datasets
    from sklearn.cluster import KMeans
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from itertools import cycle
    import pylab as pl

    k = 3
    # import some data to play with
    iris = datasets.load_iris()
    X = iris.data  # we only take the first two features.
    y = iris.target

    centroids_set = []

    centroids = CentroidCalculater(strategy=CentroidNBC).calculate(X, k)
    print centroids
    init_c = [X[c] for c in centroids]
    init_c = np.array(init_c)
    centroids_set.append(init_c)

    centroids = CentroidCalculater(strategy=CentroidEven).calculate(X, k)
    print centroids
    init_c = [X[c] for c in centroids]
    init_c = np.array(init_c)
    centroids_set.append(init_c)

    centroids = CentroidCalculater(strategy=CentroidSPSS).calculate(X, k)
    print centroids
    init_c = [X[c] for c in centroids]
    init_c = np.array(init_c)
    centroids_set.append(init_c)

    centroids = CentroidCalculater(strategy=CentroidDensity).calculate(X, k)
    print centroids
    init_c = [X[c] for c in centroids]
    init_c = np.array(init_c)
    centroids_set.append(init_c)

    estimators = {'k_means_iris_3': KMeans(n_clusters=k),
                  #'k_means_iris_8': KMeans(n_clusters=8),
                  #'k_means_iris_init_NBC': KMeans(n_clusters=k, n_init = 1,init=init_c)}
                  'k_means_iris_init_NBC': KMeans(n_clusters=k, n_init = 1,init=centroids_set[0]),
                  'k_means_iris_init_even': KMeans(n_clusters=k, n_init = 1,init=centroids_set[1]),
                  'k_means_iris_init_spss': KMeans(n_clusters=k, n_init = 1,init=centroids_set[2]),
                  'k_means_iris_init_density': KMeans(n_clusters=k, n_init = 1,init=centroids_set[3])}

    fignum = 1
    for name, est in estimators.items():
        fig = plt.figure(fignum, figsize=(4, 3))
        plt.clf()
        ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)

        plt.cla()
        est.fit(X)
        labels = est.labels_

        ax.scatter(X[:, 3], X[:, 0], X[:, 2], c=labels.astype(np.float))

        ax.w_xaxis.set_ticklabels([])
        ax.w_yaxis.set_ticklabels([])
        ax.w_zaxis.set_ticklabels([])
        ax.set_xlabel('Petal width')
        ax.set_ylabel('Sepal length')
        ax.set_zlabel('Petal length')
        fignum = fignum + 1

    # Plot the ground truth
    fig = plt.figure(fignum, figsize=(4, 3))
    plt.clf()
    ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)
    
    plt.cla()

    for name, label in [('Setosa', 0),('Versicolour', 1),('Virginica', 2)]:
        ax.text3D(X[y == label, 3].mean(),
                  X[y == label, 0].mean() + 1.5,
                  X[y == label, 2].mean(), name,
                  horizontalalignment='center',
                  bbox=dict(alpha=.5, edgecolor='w', facecolor='w'))
    # Reorder the labels to have colors matching the cluster results
    y = np.choose(y, [1, 2, 0]).astype(np.float)
    ax.scatter(X[:, 3], X[:, 0], X[:, 2], c=y)

    ax.w_xaxis.set_ticklabels([])
    ax.w_yaxis.set_ticklabels([])
    ax.w_zaxis.set_ticklabels([])
    ax.set_xlabel('Petal width')
    ax.set_ylabel('Sepal length')
    ax.set_zlabel('Petal length')
    plt.show()
