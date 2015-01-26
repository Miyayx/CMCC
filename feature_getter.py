#/usr/bin/env/python2.7
# -*- coding: utf-8 -*-

from utils import *
from fileio import *
from db import *
from filter import *

import re
import codecs

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
