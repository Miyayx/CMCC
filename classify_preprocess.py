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

def get_common_section_labels(label_block, synonym_merge = False):
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

    synonym_dict = {}
    synonym_list = []
    if synonym_merge:
        synonym_dict, synonym_list = get_synonym_dict(os.path.join(BASEDIR, file_configs["synonym_dict"]))
    for s, labels in label_block.items():
        if synonym_merge:
            labels = filter_use_synonym(labels, synonym_dict)
        for l in labels:
            labels_num[l] = labels_num.get(l,0) + 1
    return [k for k in labels_num.keys() if labels_num[k] > 1]    
def section_label_feature(samples, label_block, common = False, synonym_merge = False):
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
    synonym_dict = {}
    synonym_list = []
    if synonym_merge:
        synonym_dict, synonym_list = get_synonym_dict(os.path.join(BASEDIR, file_configs["synonym_dict"]))
    if synonym_merge:
        labels = filter_use_synonym(labels, synonym_dict)
    #else:
    #    labels = expand_all_synonym(labels, synonym_list)
    print "Have",len(labels),"labels"
    
    for s in label_block.keys():
        if synonym_merge:
            label_block[s] = filter_use_synonym(label_block[s],synonym_dict)
    #    else:
    #        label_block[s] = expand_use_synonym(label_block[s],synonym_list)

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
    print "feature column:",len(colname)
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
    try:
        links,linknum = get_link(os.path.join(BASEDIR,file_configs["outlink"]))
        inlinks,inlinknum = get_link(os.path.join(BASEDIR,file_configs["inlink"]))
    except:
        return sample_block,{}

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
                d[k] = int(v)

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

def run(configs, file_cfg):
    """
    Args:
    ---------------------------------
    configs:
        input configs from command or config file. Value can be changed
    file_cfg:
        文件名与文件路径的配置文件，配置从这个文件里读取，不从命令行李读。通常不允许被修改，但是可以通过改这个文件里的内容达到修改的目的
    """
    import time
    print "Begin to time!"
    time_start = time.time()

    global file_configs
    file_configs = read_file_config(file_cfg)
    configs.pop('output_path')

    OTHERS_PATH = os.path.join(RESULT_PATH, file_configs["others_output_path"]) #其他文件的存放目录

    if not os.path.isdir(RESULT_PATH):
        os.mkdir(RESULT_PATH)
    if not os.path.isdir(OTHERS_PATH):
        os.mkdir(OTHERS_PATH)
    if not os.path.isdir(LOG_PATH):
        os.mkdir(LOG_PATH)

    section = configs['section']
    configs.pop('section')

    fconfigs = configs

    ############### file name ################
    result_output = os.path.join(RESULT_PATH,file_configs["result_output"] + "_" + section + ".csv")
    delete_output = os.path.join(OTHERS_PATH,file_configs["delete_output"] + "_" + section + ".dat")
    hub_output = os.path.join(OTHERS_PATH,file_configs["hub_output"] + "_" + section + ".dat")
    attribute_output = os.path.join(OTHERS_PATH, file_configs["attribute_output"] + "_" + section + ".dat")
    no_feature_output = os.path.join(OTHERS_PATH, file_configs["no_feature_output"] + "_" + section + ".dat")
    file_statistics = os.path.join(LOG_PATH, file_configs["file_statistics"] + "_" + section + ".dat")
    left_section_file = os.path.join(OTHERS_PATH, file_configs["left_section_file"] + "_" + section + ".dat")
    left_block_file = os.path.join(OTHERS_PATH, file_configs["left_block_file"] + "_" + section + ".dat")
    file_col = os.path.join(RESULT_PATH, file_configs["file_col"])

    log = {}

    db = DB()
    if fconfigs["sample_filter_dir"] and len(fconfigs["sample_filter_dir"]) > 0:
        db.filter(fconfigs["sample_filter_dir"].split(","))
    if fconfigs["sample_filter_file"] and len(fconfigs["sample_filter_file"]) > 0:
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
    if fconfigs.get("section_label",0): #如果配置里有section_label
        o_label_block = db.get_sample2section()

        label_block = filter_label(o_label_block)

        labels, label_features = section_label_feature(sample_block, label_block, fconfigs["label_common"], fconfigs["synonym_merge"])

        fields.append(labels)
        features.append(label_features)

        record_left_label(o_label_block, labels, left_section_file)

    ###################  block label  ####################
    if fconfigs.get("block_label",0): #如果配置里有block_label
        o_sample_bl = db.get_sample2subsection()

        sample_bl = filter_label(o_sample_bl)#过滤掉格式不符合要求的label

        sublabels, sublabel_feature = label_feature(sample_block, sample_bl, fconfigs["label_common"])
        fields.append(sublabels)
        features.append(sublabel_feature)

        record_left_label(o_sample_bl, sublabels, left_block_file)

    ################## title keyword tfidf  #####################
    if fconfigs.get("title_tfidf",0):
        sent_segs = read_segmentation(file_configs["title_word_segmentation"])
        #title_keywords = get_title_keywords(sent_segs)
        title_keywords, title_tfidf = tfidf_gensim(sent_segs)

        fields.append(title_keywords)
        features.append(title_tfidf)

    ###################  document tfidf  ###################
    if fconfigs.get("document_tfidf",0):
        if os.path.isfile(os.path.join(BASEDIR,file_configs["document_segmentation"])):
            doc_seg = read_segmentation(os.path.join(BASEDIR,file_configs["document_segmentation"]))
        else:
            print "No document segmentation file, use db"
            doc_seg = db.doc_segmentation()

        kws, kw_feature = tfidf_gensim(doc_seg)
        print "number of document keywords:",len(kws)

        fields.append(kws)
        features.append(kw_feature)

    ############## record feature count ##############
    if fconfigs.get("section_label",0) or fconfigs.get("block_label",0):
        count = 1
        with codecs.open(file_col,"w") as f:
            if fconfigs.get("section_label",0):
                f.write("section_count="+str(len(fields[count]))+"\n")
                count += 1
            if fconfigs.get("block_label",0):
                f.write("block_count="+str(len(fields[count]))+"\n")
                count += 1
            f.write("feature_count="+str(len(feature_fields(fields))))

    fields.append(["sample2"])
    features.append(dict((k,k) for k in sample_block))

    label_block = db.get_sample2section()
    if fconfigs.get("section_label",0):
        fields.append(["section label"])
        features.append(dict((k,"#".join(label_block[k])) for k in sample_block ))
    
    sample_sl = db.get_sample2subsection()
    if fconfigs.get("block_label",0):
        fields.append(["block label"])
        features.append(dict((k,"#".join(sample_sl[k])) for k in sample_block ))

    if fconfigs.get("no_feature",0):
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

    configs = read_feature_config(os.path.join(BASEDIR, DOC_FEATURE_FILE))[0][1]
    configs = dict(configs)
    configs.update(read_properties(os.path.join(BASEDIR, PATH_FILE)))
    configs.update(read_properties(os.path.join(BASEDIR, DB_FILE)))

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-o", "--output_path", dest="output_path", help="Set output path", default=configs["output_path"])
    parser.add_option("-l", "--log_path", dest="log_path", help="Set log path", default=configs["log_path"])
    parser.add_option("-s", "--section_label", dest="section_label", type="int", help="If feature contains section label. 1(Yes), 0(No)", default=configs["section_label"])
    parser.add_option("-b", "--block_label", dest="block_label", type="int", help="If feature contains block label. 1(Yes), 0(No)", default=configs["block_label"])
    parser.add_option("-t", "--title_tfidf", dest="title_tfidf", type="int", help="If feature contains title tfidf, need title tfidf file. 1(Yes), 0(No)", default=configs["title_tfidf"])
    parser.add_option("-d", "--document_tfidf", dest="document_tfidf", type="int", help="If feature contains document tfidf, need document tfidf file. 1(Yes), 0(No)", default=configs["document_tfidf"])
    parser.add_option("-k", "--document_keyword", dest="document_keyword", type="int", help="If feature contains document keyword, need document keyword file. 1(Yes), 0(No)", default=configs["document_keyword"])
    parser.add_option("-H", "--hub", dest="hub", type="int", help="If extract hub files and save. 1(Yes), 0(No)", default=configs["hub"])
    parser.add_option("-a", "--attribute", dest="attribute", type="int", help="If extract attribute files and save. 1(Yes), 0(No)", default=configs["attribute"])
    parser.add_option("-n", "--no_feature", dest="no_feature", type="int", help="If extract no feature files and save. 1(Yes), 0(No)", default=configs["no_feature"])
    parser.add_option("-c", "--label_common", dest="label_common", type="int", help="If only retain labels which occur twice. 1(Yes), 0(No)", default=configs["label_common"])
    parser.add_option("-S", "--synonym_merge", dest="synonym_merge", type="int", help="If use synonyms and merge synonyms as one word. 1(Yes), 0(No)", default=configs["synonym_merge"])
    parser.add_option("-D", "--sample_filter_dir", dest="sample_filter_dir", help="Use samples in specific dir", default=configs["sample_filter_dir"])
    parser.add_option("-F", "--sample_filter_file", dest="sample_filter_file",help="Use samples in specific list, the sample list is read from sample_filter_file", default=configs["sample_filter_file"])
    parser.add_option("-C", "--collection", dest="mongo.collection", type="string", help="DB collection", default=configs["mongo.collection"])

    (options, args) = parser.parse_args()
    options = vars(options)

    if len(options) > 1:
        configs.update(options)

    file_cfg = os.path.join(BASEDIR, FILE_FILE)

    run(configs, file_cfg)
