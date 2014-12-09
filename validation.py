#!/usr/bin/env python
#-*-coding:UTF-8-*-

import os

from classify_preprocess import *
from utils import *
from global_config import *

class Validation(object):

    def split_feature(self, data, begin, end):
        """
        根据feature分割特征数据集
        结果包含样本id（第1列）和指定feature值
        """
        return [d[0:1]+d[begin:end] for d in data]
        
    def validation(self, featurefile, options):
        """
        featurefile: 特征文件名
        options格式：
        options = {
            "section":{
                "begin":1,
                "end"  :2,
                "left_file":file path
            },
            "block":{
                "begin":3,
                "end"  :4,
                "left_file":file path
            }
            "table_header":{
                "begin":5,
                "end"  :26,
                "left_file":file path
            }
        }
    
        特征验证
        section label:    exist_val
        block label: exist_val
        table header: exist_val
        """
        db = DB()
        with open(featurefile) as f:
            data = [l.strip("\n").decode("utf-8").split(",") for l in f.readlines()]
            fields = data[0]
            if options.has_key("section"):
                #验证section label
                print "=============== section label validation ================="
                f_d = self.split_feature(data,options["section"]["begin"], options["section"]["end"])
                print "section feature length:",len(f_d[0])-1
                section_i = fields.index("section label")
                sample_sl = dict((d[0], d[section_i].split("#") if len(d[section_i].strip()) > 0 else []) for d in data[1:])
                self.exist_val(f_d, sample_sl, options['section']['left_file'])
    
            if options.has_key("block"):
                print "=============== block label validation ================="
                f_d = self.split_feature(data,options["block"]["begin"], options["block"]["end"])
                print "block feature length:",len(f_d[0])-1
    
                block_i = fields.index("block label")
                sample_bl = dict((d[0], d[block_i].split("#") if len(d[block_i].strip()) > 0 else []) for d in data[1:])
                
                self.exist_val(f_d, sample_bl, options['block']['left_file'] )
    
            if options.has_key("table_header"):
                print "=============== block label validation ================="
                f_d = self.split_feature(data,options["table_header"]["begin"], options["table_header"]["end"])
                print "table header feature length:",len(f_d[0])-1
    
                block_i = fields.index("table header")
                sample_bl = dict((d[0], d[block_i].split("#") if len(d[block_i].strip()) > 0 else []) for d in data[1:])
                
                self.exist_val(f_d, sample_bl, options['table_header']['left_file'] )
    
    def exist_val(self, data, origin, fn = None):
        """
        判断样本都有哪些特征存在非0特征值
        Args:
        --------------------------------------
            data:二维数组，list of list，从features文件中读取的数据
            origin: 作为验证标准的元数据
                    dict，k：样本id， v：label或关键词。
        Return:
        """
        print "data len:",len(data)
        print "origin len:",len(origin)
        fields = [d.strip("\c") for d in data[0]]
        index_list = []
    
        left_dict = {}
        if fn:
            for l in open(fn):
                l = l.decode("utf-8")
                items =l.strip("\n").split("\t") 
                if len(items) == 1:
                    left_dict[items[0]] = []
                else:
                    s,ls = items
                    left_dict[s] = ls.split(",")
                
        for d in data[1:]:
            print "\n==================="
            items = d
            sample = items[0]
            try:
                ls = set(origin[sample])
            except Exception,e:
                print "WARNING:",sample.encode("utf-8"),"has no labels"
                continue
            print u'sample:',sample.encode("utf-8")
            mine_index = [i for i in range(1,len(items)) if float(items[i]) > 0]
            f_count = len(mine_index)
            label_count = f_count+len(left_dict[sample])
    
            print "feature count:",f_count
            print "label count:",label_count
            print "db count: ",len(ls)
            if not (label_count == len(ls)):
                print "WARNING: Label count and db count: length not equal"
            print "++++++++  feature  +++++++++++++"
            for i in mine_index:
                print "    "+fields[i].encode("utf-8")
            print "++++++++  origin  +++++++++++++"
            for l in sorted(ls):
                print "    "+l.encode("utf-8")
            index_list.append(mine_index)
        return index_list
