#!/usr/bin/env python
#-*-coding:utf-8-*-

from gensim.models.word2vec import Word2Vec
import numpy as np
from sklearn.cluster import SpectralClustering
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from db import *

db = DB('../../conf/conf.properties')
segs = db.read_segmentation()

words = []
for v in segs.values():
    words += v
words = set(words)
words = list(words)

#s_sl = db.get_sample2section()
#s_bl = db.get_sample2subsection()

all_ = segs
#for k,v in s_sl.items():
#    all_[k] += v
#for k,v in s_bl.items():
#    all_[k] += v

model = Word2Vec(segs.values(), size=100, window=10, min_count=5, workers=4)

features = [model[w] for w in words if w in model]

X = np.array(features)
scaler = StandardScaler(with_mean=False)
X = scaler.fit_transform(X=X.astype(np.float))

#sc = SpectralClustering(n_clusters=8, eigen_solver=None, random_state=None, n_init=10, gamma=1.0, affinity='rbf', n_neighbors=5, eigen_tol=0.0, assign_labels='kmeans', degree=3, coef0=1, kernel_params=None)
#sc.fit(X)
#labels = sc.labels_

km = KMeans(n_clusters=8, n_init=1 )
km.fit(X)
labels = km.labels_

sample_label = dict((words[i], str(labels[i])) for i in range(len(labels)))

for k,v in sample_label.items():
    print k,v

c_sample = {}
for k,v in sample_label.items():
    c_sample[v] = c_sample.get(v, []) + [k]

for k,v in c_sample.items():
    print "*"*5,k,"*"*5
    for vv in v:
        print vv
    

#for k ,v in model.most_similar(positive=[u'套餐']):
#    print k,v
#
#print model.similarity(u'套餐', u'说明')

