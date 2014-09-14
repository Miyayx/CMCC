#!/usr/bin/python
#encoding=utf-8

import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

def normalize(X):
    X = np.array(X)
    meanVals = np.mean(X, axis=0)  
    meanRemoved = X - meanVals #减去均值  
    stded = meanRemoved / np.std(X) #用标准差归一化  
    return stded

def calculate_centroid_PCA(X, k):
    #from sklearn.decomposition import PCA
    #pca = PCA(n_components=k)
    #pca.fit(X)
    #print pca.explained_variance_ratio_
    #print pca.components_

    X = np.mat(X)
    X = np.transpose(X)
    X = np.array(X)
    meanVals = np.mean(X, axis=0)  
    meanRemoved = X - meanVals #减去均值  
    stded = meanRemoved / np.std(X) #用标准差归一化  
    covMat = np.cov(stded, rowvar=0) #求协方差方阵  
    eigVals, eigVects = np.linalg.eig(np.mat(covMat)) #求特征值和特征向量  
    print len(eigVals)
    print eigVals
    eigd = dict((i,eigVals[i]) for i in range(len(eigVals)))
    sorted_eig = sorted(eigd, key=eigd.get)
    print sorted_eig[:k]
    return sorted_eig[:k]

def calculate_centroid_even(X, k):
    """
    Takes N, the number of points in the dataset, and uses the points at the indexes of the integer values of N/K, 2N/K, 3N/K a        nd so on, as the initial center points, until reaching the points at (K-1)*N/K and finally N, the last point in the sorted         data set. 
    """

    n = len(X)
    centroids = [(i*n)/k for i in range(k)]
    return centroids

def calculate_centroid_SPSS(X, k):
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

class CentroidCalculater:

    def __init__(self, X, k):
        self.X = X
        self.N = len(X)
        self.k = k

    def calculate_rho(self, dis, dc):
        assert self.N == len(dis)
        rho_arr = []
        for i in range(self.N):
            ps = [dis[i][j] for j in range(self.N) if dis[i][j] <= dc]
            rho_arr.append(len(ps))
        return rho_arr

    def calculate_delta(self, dis, rho_arr):
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
        
    def calculate_centroid(self):
        """
        Algorithm From Paper: Clustering by fast search and find of density peaks
        """
        print "Calculating centroids..."
        centroids = []
        
        print "Sample:", len(self.X)
        dis = euclidean_distances(self.X, self.X)
        dc = self.estimate_dc(dis)
        rho_arr = self.calculate_rho(dis, dc)
        rho_arr = normalize(rho_arr)
        print "rho:",rho_arr
        delta_arr = self.calculate_delta(dis, rho_arr)
        delta_arr = normalize(delta_arr)
        print "delta_arr:",delta_arr
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

if __name__=="__main__":
    from sklearn import datasets
    from sklearn.cluster import KMeans
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    # import some data to play with
    iris = datasets.load_iris()
    X = iris.data  # we only take the first two features.
    y = iris.target
    centroids = CentroidCalculater(X, 3).calculate_centroid()
    init_c = [X[c] for c in centroids]
    init_c = np.array(init_c)

    estimators = {'k_means_iris_3': KMeans(n_clusters=3),
                  #'k_means_iris_8': KMeans(n_clusters=8),
                  'k_means_iris_bad_init': KMeans(n_clusters=3, n_init = 1,init=init_c)}

    fignum = 1
    for name, est in estimators.items():
        fig = plt.figure(fignum, figsize=(4, 3))
        plt.clf()
        ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)

        plt.cla()
        print name
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
