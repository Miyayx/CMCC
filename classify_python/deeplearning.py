#!/usr/bin/env python
#-*-coding:utf-8-*-

from gensim.models.word2vec import Word2Vec

from db import *

db = DB('../../conf/conf.properties')
segs = db.read_segmentation()
s_sl = db.get_sample2section()
s_bl = db.get_sample2subsection()

all_ = segs
for k,v in s_sl.items():
    all_[k] += v
for k,v in s_bl.items():
    all_[k] += v

model = Word2Vec(segs.values(), size=100, window=5, min_count=5, workers=4)

for k ,v in model.most_similar(positive=[u'套餐']):
    print k,v

print model.similarity(u'套餐', u'说明')

