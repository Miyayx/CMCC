#/usr/bin/env/python2.7
# -*- coding: utf-8 -*-

from utils import *
from fileio import *
from db import *
from filter import *

import re
import codecs

def get_title_keywords(segs):
    """
    Args:
        fn: title keyword file name
    Returns:
        list: title keywords
    """
    kws = set()
    for v in segs.values():
        for w in v:
            kws.add(w)
        
    return list(kws)

def get_custom_title_keywords(fn):
    """
    Args:
        title_keyword filename
    Returns:
        list: title keywords
    """
    kws = [line.strip("\n").decode("utf-8") for line in open(fn)]
    return kws

########################################################
#feature functions

def tfidf(kws, doc_segs):
    """
    自己写的tfidf算法
    根据wiki:   tf = word[i] num in doc[j]/ all word in doc[j]
                idf = log2( all doc/ doc num word[i] occurs )
    根据gensim: tf = word[i] in doc[j]
    Args:
        kws: keyword列表
        doc_segs: dict, k:样本id，v:对应的分词list
    Returns:
        doc_tfidf: dict, k:样本id，v：tfidf值
    """
    import math
    doc_tfidf = {}
    num_doc = len(doc_segs) #文档总数
    kw_in_doc = {}#kw出现在多少个文档中
    for d, s in doc_segs.items():
        for w in set(s):
            kw_in_doc[w] = kw_in_doc.get(w, 0) + 1
        
    for doc, seg in doc_segs.items():
        doc_tfidf[doc] = []
        all_count = 0 #所有词出现的总数
        #for kw in kws:
        #    all_count += seg.count(kw)
        for kw in kws:
            if not kw in seg:
                doc_tfidf[doc].append(0)
                continue
            #tf = seg.count(kw)/float(all_count)
            tf = seg.count(kw)
            df = kw_in_doc[kw]
            idf = math.log(1.0 * num_doc/df, 2) 
            tfidf = tf*idf
            doc_tfidf[doc].append(tfidf)
    
    return doc_tfidf

def tfidf_gensim(doc_segs):
    """
    用gensim求tfidf值
    """
    doc_tfidf = {}
    kws = []
    segs = []
    docs = []
    doc_segs = filter_keyword(doc_segs)
    for doc,seg in doc_segs.items():
        docs.append(doc)
        segs.append(seg)

    from gensim import corpora, models
    dictionary = corpora.Dictionary()

    corpus = [dictionary.doc2bow(seg,allow_update=True) for seg in segs]
    try:
        kws = [dictionary[i].decode("utf-8") for i in range(len(dictionary))]
    except:
        kws = [dictionary[i] for i in range(len(dictionary))]
    
    tfidf = models.TfidfModel(corpus, normalize=True)
    corpus_tfidf = tfidf[corpus]

    i = 0
    for c in corpus_tfidf:
        tfidf = [0 for j in range(len(kws))]
        for k,v in c:
            tfidf[k] = v
        doc_tfidf[docs[i]] = tfidf
        i += 1

    return kws, doc_tfidf

def get_labels(label_list):
    """
    get_section_labels(label_block) -> list of labels

    1. Get section labels from xls
    2. Delete the label occurs only once
    Args: 
        dict (k:样本id v:对应section labels)
    Returns: 
        所有section label列表（所有文档范围内）
    """
    labels = set() 
    for label_block in label_list:
        for s,lls in label_block.items():
            for l in lls:
                labels.add(l)
    return list(labels)

def get_common_labels(label_list):
    labels = []
    label_c = {}

    for sample_sl in label_list:
        for sample, ls in sample_sl.items():
            for label in ls:
                label_c[label] = label_c.get(label, 0) + 1

    labels = [k for k,v in label_c.items() if v > 1]

    return labels

def label_count(samples, label_block):
    """
    How many label are there is a document
    Args: 
        samples: list 所有样本id（路径+标题）
        label_block: dict (k:样本id v:对应 labels)
    Returns: 
        label_count: dict(k:样本id v:此文档中的label 数量)
    """
    label_count = {}
    for i in range(len(samples)):
        b = label_block[samples[i]]
        if type(b) == str:
            labels = [l for l in b.split(" ") if len(l) > 1] # >1 delete space
        if type(b) == list or type(b) == set:
            labels = b
        label_count[samples[i]] = len(labels)
    return label_count

def title_keyword_feature(samples):
    """
    标题特征
    针对title_keywords词组，看文档标题中是否存在词组中的关键字。
    词组中一个词为一个特征,存在则特征值为1，否则为0
    Args: 
        samples: list 所有样本id（路径+标题）
    Returns: 
        title_kw_feature: dict(k:样本id v:特征值，因title keywords不止一个，因此v是个list，每个元素对应一个keyword)
    """

    #标题特征，目前是以类别为关键词
    title_keywords2 = get_custom_title_keywords(file_configs["title_keywords"])

    title_kw_feature = {}
    for sample in samples:
        title = sample.rsplit("/",3)[-2]#获得标题（不含路径）
        fs = []
        for k in title_keywords2:
            if k in title:
                fs.append(1)
            else:
                fs.append(0)
        title_kw_feature[sample] = fs
    return title_keywords2, title_kw_feature

def label_feature(sample_block, sample_sl, common = False):
    if common:
        sublabels = get_common_labels([sample_sl])
    else:
        sublabels = get_labels([sample_sl])
    sublabel_feature = {}
    for s in sample_block:
        labels = sample_sl[s] if sample_sl.has_key(s) else []
        sublabel_feature[s] = []
        for l in sublabels:
            if l in labels:
                sublabel_feature[s].append(1)
            else:
                sublabel_feature[s].append(0)
    return sublabels, sublabel_feature

def get_doc_keywords(sample_key):
    """
    get_section_labels(label_block) -> list of labels

    1. Get section labels from xls
    2. Delete the label occurs only once
    Args: 
        dict (k:样本id v:对应section labels)
    Returns: 
        所有section label列表（所有文档范围内）
    """
    keywords = set() 
    for s,ks in sample_key.items():
        for k in ks:
            keywords.add(k)
    return list(keywords)

def get_common_doc_keywords(sample_key):
    """
    get_common_doc_keywords(sample_key) -> list of common keywords

    1. Get keywords from db
    2. Delete the label occurs only once
    Args: 
        dict (k:样本id v:对应keywords)
    Returns: 
        出现次数大于1的keyword列表（所有文档范围内）
    """
    keywords = []
    keywords_count = {}

    for s, ks in sample_key.items():
        for k in ks:
            keywords_count[k] = keywords_count.get(k, 0) + 1

    keywords = [k for k,v in keywords_count.items() if v > 1]

    return keywords

def doc_keyword_feature(samples, sample_key, common = False):
    """
    doc_keyword_feature(list of sample ids, sample_key) -> (list of keywords, dict of features) 

    Take section labels appear more than once as feature.
    If a section label has this label, value is 1.
    Value of the feature dict is list type

    Args: 
        samples:       list 所有样本id（路径+标题）
        label_block:   dict (k:样本id v:对应section labels)
    Returns: 
        labels:        出现次数大于1的section label列表（所有文档范围内）
        label_feature: dict(k:样本id v:section label 特征值，因label不止一个，因此v是个list，每个元素对应一个label)
    """
    if common:
        keywords = get_doc_keywords(sample_key)
    else:
        keywords = get_common_doc_keywords(sample_key)
    keyword_feature = {}
    for s in samples:
        this_keyword = sample_key[s] if sample_key.has_key(s) else []
        keyword_feature[s] = []
        for k in keywords:
            if k in this_keyword:
                keyword_feature[s].append(1)
            else:
                keyword_feature[s].append(0)
    return keywords, keyword_feature

def read_link_file(fn):
    """
    读取链接关系数据
    """
    d = {}
    if not os.path.isfile(fn):
        raise IOError

    with open(fn) as f:
        line = f.readline().decode("utf-8")
        while line:
            items = line.strip("\n").split("\t")
            if (len(items) == 1):
                items = line.strip("\n").split()
            items[0] += "/"
            items[1] += "/"
            if not d.has_key(items[0]):
                d[items[0]] = set()
            d[items[0]].add(items[1])
            line = f.readline().decode("utf-8")
    return d

def get_link(fn):
    """
    读取链接关系数据，并放入dict格式
    Returns:
        sample_links: dict (k:样本id v: list of link)
        sample_linknum: dict (k:样本id v:link 数量)
    """
    sample_links = read_link_file(fn)
    sample_linknum = {}
    for k,v in sample_links.items():
        sample_linknum[k] = sample_linknum.get(k,0)+len(v)
    return sample_links, sample_linknum

def table_header_feature(sample_block, sample_h):
    headers = get_common_labels([sample_h])
    header_feature = {}
    for s in sample_block:
        labels = sample_h[s] if sample_h.has_key(s) else []
        header_feature[s] = []
        for l in headers:
            if l in labels:
                header_feature[s].append(1)
            else:
                header_feature[s].append(0)
    return headers, header_feature
