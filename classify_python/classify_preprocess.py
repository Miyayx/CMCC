#/usr/bin/env/python2.7
# -*- coding: utf-8 -*-

from utils import *
from fileio import *
from attribute import *
from db import *
from synonym import *
from filter import *
from feature_getter import *

import re
import os
import codecs
import ConfigParser

def get_common_section_labels(label_block, synonym_merge = True):
    """
    get_common_section_labels(label_block) -> list of common labels

    1. Get section labels from xls
    2. Delete the label occurs only once
    Args: 
        dict (k:样本id v:对应section labels)
    Returns: 
        出现次数大于1的section label列表（所有文档范围内）
    """
    labels_num = {}

    synonym_dict, synonym_list = get_synonym_dict(file_configs["synonym_dict"])
    for s, labels in label_block.items():
        if synonym_merge:
            labels = filter_use_synonym(labels, synonym_dict)
        for l in labels:
            labels_num[l] = labels_num.get(l,0) + 1
    return [k for k in labels_num.keys() if labels_num[k] > 1]    

def section_label_feature(samples, label_block, common = False, synonym_merge = True):
    """
    section_label_feature(list of sample ids, label_block) -> (list of labels, dict of features) 

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
    labels = []
    if common:
        labels = get_common_section_labels(label_block, synonym_merge)
    else:
        labels = get_labels([label_block])

    print "Have",len(labels),"labels"

    #同义词
    synonym_dict, synonym_list = get_synonym_dict(file_configs["synonym_dict"])
    if synonym_merge:
        labels = filter_use_synonym(labels, synonym_dict)
    else:
        labels = expand_all_synonym(labels, synonym_list)
    print "Have",len(labels),"labels"
    
    for s in label_block.keys():
        if synonym_merge:
            label_block[s] = filter_use_synonym(label_block[s],synonym_dict)
        else:
            label_block[s] = expand_use_synonym(label_block[s],synonym_list)

    label_feature = {}
    for i in range(len(samples)):
        fs = []
        for l in labels:
            if l in label_block[samples[i]]:
                fs.append(1) 
            else:
                fs.append(0)
        label_feature[samples[i]] = fs
    return labels,label_feature

#feature functions
########################################################

def set_weight(weights = [], *features):
    """为特征添加权重
    Args：
        weights: 权重数组，一个元素对应一种特征
            注：一种特征，如section label，可能包含很多个特征, 如一个label是一特征，同一种特征使用一个权值
            weights权重应该与输入特征种类相同
        features: 可变长参数，任意个数特征,如
            set_weight(feature1, feature2, feature3)
            set_weight(feature1, feature2)
            set_weight(feature1)
            但每一个feature都是一个dict,weights的顺序要与feature的顺序相同
    """
    assert len(weights) == len(features)
    
    if len(weights) > 0:
        for i in range(min(len(weights),len(features))):
            f = features[i]
            w = weights[i]
            if type(f.values()[0]) == list:
                for k,v in f.items():
                    f[k] = [ j*w for j in v]
            else:
                for k,v in f.items():
                    f[k] = v*w

def write_dataset(samples, colname, features, classes={}, fn = "all_data.csv", ):
    """数据集写入文本
    Args:
        samples: list 所有样本id（路径+标题）
        classes: dict (k:样本id v:对应类别)
        colname: 属性列名
        fn:      filename 结果文件名 如果是训练集就是filname_train.csv
        features: 可变长参数，任意个数特征

    """
    print "feature colnum:",len(colname)
    print "features length:",len(features)
    classify = True if len(classes) > 0 else False

    print "Writing..."
    write_features(colname, classify, fn, generate_dataset(samples, features, classes, classify))
    print "Total:",len(samples)

def generate_dataset(samples, features, classes={}, classify = False):
    """整合数据格式，分割数据集
    Args:
        samples: list 所有样本id（路径+标题）
        classes: dict (k:样本id v:对应类别)
        features: 可变长参数，任意个数特征
    Returns:
        dict格式，k为文档id，v为写入的字符串
        字符串格式：文档id，特征值1，特征值2，...特征值n,类别
    """

    for i in xrange(len(samples)):
        sample = samples[i]
        if i%100 == 0:
            print "sample",str(i)
        s = ""
        # write sample name
        s += sample
        s += ","

        # write feature string
        for f in features:
            if not f.has_key(sample):
                print "No this sample:",sample
                for j in range(len(f.values()[0])):
                    s += str(0)
                    s += ","

            elif type(f.values()[0]) == list:
                for v in f[sample]:
                    try:
                        s += str(v)
                    except:
                        s += v
                    s += ","
            else:
                s += f[sample] if type(f[sample] == str) else str(f[sample])
                s += ","

        #所属类
        d = {}
        if classify:
            c = classes[sample].strip()
            s += c
            if not d.has_key(c):
                d[c] = []
            d[c].append(s)
        else:
            s = s[:-1]
            s += "\n"
            yield s

def write_features(colname,classify, fn, dataset):
    """
    Args:
        colname: 列名
        fn:      filename 结果文件名 
        d: 数据集，dict格式，k为文档id，v为写入的字符串
    """
    with codecs.open(fn,"w",encoding="utf-8") as f:
        i = 0
        s = "sample,"
        for l in colname:
            #print colname.index(l),l
            s += (l+",")
        if classify:
            s += "class"
        else:
            s = s[:-1]
        s += "\n"
        f.write(s)

        for l in dataset:
            f.write(l)

def record_left_label(s2l, labels, fn):
    """
    记录没有进入大表的label
    Args:
    -----------------------------------
      s2l: dict: key:sample id , value:对应的所有label的list
      labels：作为feature的label的列表
      fn：记录文件
    """
    f = codecs.open(fn,"w","utf-8")
    for s,l in s2l.items():
        line = s+"\t"
        for i in (set(l) - set(labels)):
            line += (i+",")
        line = line[:-1]+"\n"
        f.write(line)
    f.close()

def filter_doc(sample_block, section_label, block_label, hubfile=True, hub_output=None, attrfile=True, attribute_output=None):
    """
    获取link信息，依规则判断Hub和属性文档，从文档集合中过滤出去
    Args: 
        sample_block: list 所有样本id（路径+标题）
        label_block: dict (k:样本id v:对应section labels)
    Returns:
        sample_block:过滤掉Hub和属性文档后的文档集合
    """
    slabel_count = label_count(sample_block,section_label)
    blabel_count = label_count(sample_block,block_label)
    links,linknum = get_link(file_configs["outlink"])
    inlinks,inlinknum = get_link(file_configs["inlink"])

    class_sample = {}

    if hubfile:
        hubs = detect_hub(slabel_count, linknum)
        print "hub files:",len(hubs)
        class_sample["hub"] = hubs
        if hub_output:
            write_lines(hub_output, sorted(hubs))
        print "sample count:",len(sample_block)
        sample_block = [s for s in sample_block if s not in hubs] 

    if attrfile:
        attrfiles = detect_attributefile(slabel_count, blabel_count, inlinks, inlinknum, links) #判断属性文档
        attrfiles = list(set(attrfiles) & set(sample_block)) #只要属性list和文档list的重叠部分
        class_sample["attribute"] = attrfiles
        if attribute_output:
            write_lines(attribute_output, sorted(attrfiles))
        print "sample count:",len(sample_block)
        print "attrfiles:",len(attrfiles)
        sample_block = [s for s in sample_block if s not in attrfiles] 
        sample_block = delete_items(sample_block, attrfiles)
    print "sample count:",len(sample_block)

    return sample_block, class_sample 

def feature_fields(fields):
    """
    feature_fields(fields, ...) -> list

    feature列名的合并与冲突处理
    1. 将所有feature的列放入一个list中
    2. 对重复出现的feature名，视为不一样的feature，在原feature名上加上“\c”
    3. 最坏的情况，每个种类的feature都有冲突的词语，比如关键字特征中有A这个特征，section label中也有A，subsection label中也有。。。，只要冲突就认为是新的feature，在后面加上\c
    输入：
    fields：feature名称的列表，是一个list，每一个元素是一类feature（如section label）的label list

    但每一个fields都要是一个list,fields的顺序要与feature的顺序相同
    输出：所有fields的合并列表
    """
    num = 0
    fs = []
    for f in fields:
        num += 1
        print "feature"+str(num)+":",len(f)
        # f is a list
        for i in f: #对于每一个列名
            for j in range(len(fields)):
                if i in fs:
                    i += "\\c"
            fs.append(i)
    return fs

def read_feature_config(fn):
    """
    从配置文件读取feature相关配置参数
    """
    configs = {}
    con = ConfigParser.RawConfigParser()
    con.read(fn)
    for s in con.sections():
        d = dict((o, con.get(s,o)) for o in con.options(s))
        for k, v in d.items():
            if v.isdigit():
                d[k] = bool(int(v))

        configs[s] = d

    return sorted(configs.items(), key=lambda e:e[0],reverse=True)

def read_file_config(fn):
    """
    从配置文件读取输入输出文档相关配置参数
    """
    configs = {}
    con = ConfigParser.RawConfigParser()
    con.read(fn)
    configs = dict((o, con.get("file",o)) for o in con.options("file"))
    return configs

def run(path_cfg, file_cfg, feature_cfg, db_cfg):
    import time
    print "Begin to time!"
    time_start = time.time()

    global file_configs
    feature_configs = read_feature_config(feature_cfg)
    file_configs = read_file_config(file_cfg)
    path_configs = read_properties(path_cfg)
    CONF_PATH = path_configs['conf_path']
    RESULT_PATH = path_configs['output_path'] #总的输出文件夹
    OTHERS_PATH = os.path.join(RESULT_PATH, file_configs["others_output_path"]) #其他文件的存放目录
    FEATURE_PATH = os.path.join(RESULT_PATH, file_configs["feature_output_path"])

    if not os.path.isdir(RESULT_PATH):
        os.mkdir(RESULT_PATH)
    if not os.path.isdir(OTHERS_PATH):
        os.mkdir(OTHERS_PATH)
    if not os.path.isdir(FEATURE_PATH):
        os.mkdir(FEATURE_PATH)

    for section, fconfigs in feature_configs:

        ############### file name ################
        result_output = os.path.join(RESULT_PATH,file_configs["result_output"] + "_" + section + ".csv")
        delete_output = os.path.join(OTHERS_PATH,file_configs["delete_output"] + "_" + section + ".dat")
        hub_output = os.path.join(OTHERS_PATH,file_configs["hub_output"] + "_" + section + ".dat")
        attribute_output = os.path.join(OTHERS_PATH, file_configs["attribute_output"] + "_" + section + ".dat")
        no_feature_output = os.path.join(OTHERS_PATH, file_configs["no_feature_output"] + "_" + section + ".dat")
        file_statistics = os.path.join(OTHERS_PATH, file_configs["file_statistics"] + "_" + section + ".dat")
        left_section_file = os.path.join(OTHERS_PATH, file_configs["left_section_file"] + "_" + section + ".dat")
        left_block_file = os.path.join(OTHERS_PATH, file_configs["left_block_file"] + "_" + section + ".dat")
        file_col = os.path.join(CONF_PATH, file_configs["file_col"])

        if not fconfigs["run"]:
            continue

        log = {}

        db = DB(db_cfg)
        if len(fconfigs["sample_filter_str"]) > 0:
            db.filter(fconfigs["sample_filter_str"].split(","))
        if len(fconfigs["sample_filter_file"]) > 0:
            db.filter(fconfigs["sample_filter_file"],type="file")

        class_block = {}
        sample_block = db.all_samples #sample_block里是本次预处理涉及到的文档id列表
        all_sample = sample_block

        log["total"] = len(sample_block)

        #Delete samples whose name has ','
        sample_block = delete_sample(sample_block, u',')
        write_lines(delete_output, diff_items(all_sample, sample_block))
        log["delete_sample"] = len(diff_items(all_sample, sample_block))

        ##################### HUB ATTRIBUTE  ##################

        if fconfigs["hub"] or fconfigs["attribute"]:
            section_label = db.get_sample2section()
            block_label = db.get_sample2subsection()

            sample_block, filter_result = filter_doc(sample_block, section_label,block_label, hubfile = fconfigs["hub"], hub_output = hub_output, attrfile = fconfigs["attribute"], attribute_output = attribute_output)

            for k,v in filter_result.items():
                log[k] = len(v)
        
        #After delete all specific samples, reset allsample in db
        db.set_allsample(sample_block)

        features = [] #存储feature值，一个元素是一类feautre的值的列表
        fields = []   #存储feature 名称值，一个元素是一类feature的名称的列表

        if os.path.exists(result_output): #原来的result文件删除，重新创建一个
            os.remove(result_output)

        fields.append(["Class"])
        features.append(dict((k,"") for k in sample_block))

        ##################  section label  ####################
        if fconfigs["section_label"] and not fconfigs["merge_label"]: #如果配置里有section_label
            o_label_block = db.get_sample2section()

            label_block = filter_label(o_label_block)
  
            labels, label_features = section_label_feature(sample_block, label_block, fconfigs["label_common"], fconfigs["synonym_merge"])

            fields.append(labels)
            features.append(label_features)

            record_left_label(o_label_block, labels, left_section_file)

        ###################  block label  ####################
        if fconfigs["block_label"] and not fconfigs["merge_label"]: #如果配置里有block_label
            o_sample_bl = db.get_sample2subsection()

            sample_bl = filter_label(o_sample_bl)#过滤掉格式不符合要求的label

            sublabels, sublabel_feature = subsection_label_feature(sample_block, sample_bl, fconfigs["label_common"])
            fields.append(sublabels)
            features.append(sublabel_feature)

            record_left_label(o_sample_bl, sublabels, left_block_file)

        ################### merge section and block label ############
        if fconfigs["merge_label"]: #如果配置里有merge_label, 即同样文本的section和block label被看作是同一label
            sample_sl = db.get_sample2section()
            sample_bl = db.get_sample2subsection()

            labels, label_feature = merge_label_feature(sample_block, sample_sl, sample_bl, fconfigs["label_common"])
            fields.append(labels)
            features.append(label_feature)

        ################## title keyword tfidf  #####################
        if fconfigs["title_tfidf"]:
            sent_segs = read_segmentation(file_configs["title_word_segmentation"])
            #segmetation_result(sent_segs, "../etc/title_keywords.txt")
            title_keywords = get_title_keywords(sent_segs)
            #title_tfidf = tfidf(title_keywords, sent_segs)
            #record_tfidf(title_keywords, title_tfidf, "../etc/title_tfidf.txt")
            title_keywords, title_tfidf = tfidf_gensim(sent_segs)
            #title_tfidf = read_tfidf("../etc/title_tfidf.txt")

            fields.append(title_keywords)
            features.append(title_tfidf)

        ################### title keyword ####################
        if fconfigs["title_keyword"]:

            title_keywords2, title_kw_feature = title_keyword_feature(sample_block)

            fields.append(title_keywords2)
            features.append(title_kw_feature)

        ###################  content keyword  ###################
        if fconfigs["document_tfidf"]:
            #kws, kw_feature = db.keyword_feature()
            #kws = db.get_keywords()
            #doc_seg = db.read_segmentation()
            doc_seg = read_segmentation(file_configs["document_segmentation"])
            kws = get_title_keywords(doc_seg)
            #doc_seg = db.get_sample2keywords()
            kw_feature = tfidf(kws, doc_seg)
            #record_tfidf(kws, kw_feature, "../etc/keyword_tfidf.txt")
            #kw_feature = read_tfidf("../etc/keyword_tfidf.txt")

            #kws, kw_feature = tfidf_gensim(doc_seg)
            print "number of document keywords:",len(kws)

            fields.append(kws)
            features.append(kw_feature)

        ###################### Weight #################

        #set_weight([1,1000], label_features,title_tfidf)

        ########################  feature file output  #########################

        #outfile = os.path.join(FEATURE_PATH, section+".csv")

        #先写个原始的feature文件
        #write_dataset(sample_block, feature_fields(fields), features, class_block, fconfigs["split"], outfile)

        ############## record feature count ##############
        if fconfigs["section_label"] or fconfigs["block_label"] or fconfigs["merge_label"]:
            with codecs.open(file_col,"w") as f:
                if fconfigs["section_label"] and not fconfigs["merge_label"]:
                    f.write("section_count="+str(len(fields[1]))+"\n")
                if fconfigs["block_label"] and not fconfigs["merge_label"]:
                    f.write("block_count="+str(len(fields[2]))+"\n")
                f.write("feature_count="+str(len(feature_fields(fields))))

        fields.append(["sample2"])
        features.append(dict((k,k) for k in sample_block))

        if fconfigs["section_label"]:
            label_block = db.get_sample2section()
            fields.append(["section label"])
            features.append(dict((k,"#".join(label_block[k])) for k in sample_block ))
        
        if fconfigs["block_label"]:
            sample_sl = db.get_sample2subsection()
            fields.append(["block label"])
            features.append(dict((k,"#".join(sample_sl[k])) for k in sample_block ))

        if fconfigs["no_feature"]:
            print "Delete no feature samples"
            no_feature_samples = []
            for s in sample_block:
                if len(label_block[s]) == 0 and len(sample_sl[s]) == 0:
                    no_feature_samples.append(s)

            print "Num of no feature samples",len(no_feature_samples)
            write_lines(no_feature_output,sorted(no_feature_samples))
            log["no_feature_sample"] = len(no_feature_samples)
            sample_block = delete_items(sample_block,no_feature_samples)
            print "sample count:",len(sample_block)

        # 所有feature值都为0的样本列表，这类样本也进入迭代
        feature0_samples = []
        for s in sample_block:
            values = []
            for f in features:
                values += f[s]
            if values.count(1) == 0:
                feature0_samples.append(s)
        log["feature0_sample"] = len(feature0_samples)
        log["iteration_sample"] = len(sample_block)
        
        sorted(sample_block) #按id名称顺序输出

        print "Writing to",result_output
        write_dataset(sample_block, feature_fields(fields), features, class_block, result_output)

        record_log(file_statistics, log)

        print "Finish!"
        print "Time Consumming:",str(time.time()-time_start)

if __name__=="__main__":
    import sys
    if len(sys.argv) > 1:
        if not len(sys.argv) == 5:
            print "Wrong Argus. Need four config files"
            print "Format: python classify_preprocess.py path_config_file file_config_file feature_config_file db_config_file"
        else:
            run(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        run("../conf/path.properties","../conf/file.cfg","../conf/feature.cfg","../../conf/conf.properties")
