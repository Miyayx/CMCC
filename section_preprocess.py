#/usr/bin/env/python2.7
# -*- coding: utf-8 -*-

import re
import os
import time
import codecs
import ConfigParser

from utils import *
from fileio import *
from db import *
from filter import *
from feature_getter import *
from global_config import *
from classify_preprocess import read_feature_config
from classify_preprocess import read_file_config

def run(configs,file_cfg):
    """
    Args:
    ---------------------------------
    configs:
        input configs from command or config file. Value can be changed
    file_cfg:
        文件名与文件路径的配置文件，配置从这个文件里读取，不从命令行李读。通常不允许被修改，但是可以通过改这个文件里的内容达到修改的目的
    """
    print "Begin to time!"
    time_start = time.time()

    file_configs = read_file_config(file_cfg)
    configs.pop('output_path')

    OTHERS_PATH = os.path.join(RESULT_PATH, file_configs["others_output_path"])#其他文件的存放目录

    if not os.path.isdir(RESULT_PATH):
        os.mkdir(RESULT_PATH)#创建结果文件夹
    if not os.path.isdir(OTHERS_PATH):
        os.mkdir(OTHERS_PATH)#创建others文件夹，存储nofeature文件等
    if not os.path.isdir(LOG_PATH):
        os.mkdir(LOG_PATH)#创建log存储文件夹

    section = configs['section']
    configs.pop('section')

    fconfigs = configs

    ############### file name ################
    result_output = os.path.join(RESULT_PATH,file_configs["result_output"] + "_" + section + ".csv")
    delete_output = os.path.join(OTHERS_PATH,file_configs["delete_output"] + "_" + section + ".dat")
    no_feature_output = os.path.join(OTHERS_PATH, file_configs["no_feature_output"] + "_" + section + ".dat")
    left_section_file = os.path.join(OTHERS_PATH, file_configs["left_section_file"] + "_" + section + ".dat")
    left_block_file = os.path.join(OTHERS_PATH, file_configs["left_block_file"] + "_" + section + ".dat")
    left_tableheader_file = os.path.join(OTHERS_PATH, file_configs["left_tableheader_file"] + "_" + section + ".dat")
    file_statistics = os.path.join(LOG_PATH, file_configs["file_statistics"] + "_" + section + ".dat")
    file_col = os.path.join(RESULT_PATH, file_configs["file_col"])

    log = {}

    db = DB()
    if len(fconfigs["sample_filter_dir"]) > 0:
        db.filter(fconfigs["sample_filter_dir"].split(","))#选择指定文件夹下的样本进行预处理
    if len(fconfigs["sample_filter_file"]) > 0:
        db.filter(fconfigs["sample_filter_file"],type="file")#选择指定文件中的样本列表进行预处理

    class_block = {}
    sample_block = db.get_section2sectionlabel().keys()
    all_sample = sample_block

    log["total"] = len(sample_block)

    #Delete samples whose name has ','
    sample_block = delete_sample(sample_block, u',')
    write_lines(delete_output, diff_items(all_sample, sample_block))
    log["delete_sample"] = len(diff_items(all_sample, sample_block))

    #After delete all specific samples, reset allsample in db
    db.set_allsample(sample_block)#sample_block里是本次预处理涉及到的文档id列表

    features = []#存储feature值，一个元素是一类feautre的值的列表
    fields = []#存储feature值，一个元素是一类feautre的值的列表

    if os.path.exists(result_output):#原来的result文件删除，重新创建一个
        os.remove(result_output)

    fields.append(["Class"]) #保留第二列的Class汇总列
    features.append(dict((k,"") for k in sample_block))

    ###################  section label  ####################
    if fconfigs.get("section_label", 0):#如果配置里有section_label
        o_sample_sl = db.get_section2sectionlabel()
        sample_sl = filter_label(o_sample_sl)#过滤掉格式不符合要求的label
        slabels, slabel_feature = label_feature(sample_block, sample_sl, fconfigs["label_common"])
        fields.append(slabels)
        features.append(slabel_feature)
        record_left_label(o_sample_sl, slabels, left_section_file)

    ###################  block label  ####################

    if fconfigs.get("block_label", 0):
        o_sample_bl = db.get_section2block()#如果配置里有block_label
        sample_bl = filter_label(o_sample_bl)#过滤掉格式不符合要求的label
        blabels, blabel_feature = label_feature(sample_block, sample_bl, fconfigs["label_common"])
        fields.append(blabels)
        features.append(blabel_feature)
        record_left_label(o_sample_bl, blabels, left_block_file)

    ###################  table header  ###################
    if fconfigs.get("table_header", 0):#如果配置里有table_header
        o_table_header = db.get_section2header()#过滤掉格式不符合要求的label
        table_header = filter_label(o_table_header)
        headers, h_feature = table_header_feature(sample_block, table_header)
        fields.append(headers)
        features.append(h_feature)
        record_left_label(o_table_header, headers, left_tableheader_file)

    ################## title keyword tfidf  #####################
    if fconfigs.get("title_tfidf",0):
        sent_segs = read_segmentation(file_configs["title_word_segmentation"])
        sec_keywords = dict((k, sent_segs[k.rsplit("/",2)[0]]) for k in sample_block)
        title_keywords, title_tfidf = tfidf_gensim(sec_keywords)
        fields.append(title_keywords)
        features.append(title_tfidf)

    ###################  document tfidf  ###################
    if fconfigs.get("document_tfidf",0):
        if os.path.isfile(os.path.join(BASEDIR,file_configs["document_segmentation"])):
            doc_seg = read_segmentation(os.path.join(BASEDIR,file_configs["document_segmentation"]))
        else:
            print "No document segmentation file, use db"
            doc_seg = db.section_segmentation()
        kws, kw_feature = tfidf_gensim(doc_seg)
        print "number of section keywords:",len(kws)
        fields.append(kws)
        features.append(kw_feature)

    ############## record feature count ##############
    if fconfigs.get("block_label",0) or fconfigs.get('table_header',0) or fconfigs.get('title_tfidf',0) or fconfigs.get('document_tfidf',0):
        count = 1
        with codecs.open(file_col,"w") as f:
            if fconfigs.get("block_label",0):
                f.write("block_count="+str(len(fields[count]))+"\n")
                count += 1
            if fconfigs.get("table_header",0):
                f.write("table_header="+str(len(fields[count]))+"\n")
                count += 1
            if fconfigs.get("title_tfidf",0):
                f.write("title_tfidf_count="+str(len(fields[count]))+"\n")
                count += 1
            if fconfigs.get("document_tfidf",0):
                f.write("document_tfidf_count="+str(len(fields[count]))+"\n")
                count += 1
            f.write("feature_count="+str(len(feature_fields(fields))))

    fields.append(["sample2"])#再输出一列样本id到大表中
    features.append(dict((k,k) for k in sample_block))

    # 添加对应的section label
    s_sl = db.get_section2sectionlabel()
    fields.append(["section label"])
    features.append(dict((k,s_sl[k]) for k in sample_block ))

    s_b = db.get_section2block()
    t_h = db.get_section2header()

    # 添加对应的block label
    if fconfigs.get("block_label",0):
        fields.append(["block label"])
        features.append(dict((k,"#".join(s_b[k])) for k in sample_block ))

    # 添加表头列
    if fconfigs.get("table_header",0):
        fields.append(["table header"])
        features.append(dict((k,"#".join(t_h[k])) for k in sample_block ))

    # 没有block label和table header的section不参与分类
    if fconfigs.get("block_label", False) and fconfigs.get("table_header", False):
        no_b_t_samples = [s for s in sample_block if len(s_b[s]) == 0 and len(t_h[s]) == 0]
        print "Num of no block or table samples",len(no_b_t_samples)
        #write_lines(no_feature_output,sorted(no_feature_samples))
        log["no_block_or_table_sample"] = len(no_b_t_samples)
        sample_block = delete_items(sample_block,no_b_t_samples)
        print "sample count:",len(sample_block)

    # 没有feature的样本
    if fconfigs.get("no_feature", 0):
        print "Delete no feature samples"
        no_feature_samples = []
        for s in sample_block:
            pass

        print "Num of no feature samples",len(no_feature_samples)
        write_lines(no_feature_output,sorted(no_feature_samples))
        log["no_feature_sample"] = len(no_feature_samples)
        sample_block = delete_items(sample_block,no_feature_samples)
        print "sample count:",len(sample_block)

        # feature全为0的样本
        feature0_samples = []
        for s in sample_block:
            values = []
            for f in features:
                values += f[s]
            if values.count(1) == 0:
                feature0_samples.append(s)
        log["feature0_sample"] = len(feature0_samples)
        
        sample_block.sort()#按id名称顺序输出

        print "Writing to",result_output
        write_dataset(sample_block, feature_fields(fields), features, class_block, result_output)

        record_log(file_statistics, log)#记录各种样本的统计数量

        print "Finish!"
        print "Time Consumming:",str(time.time()-time_start)

if __name__=="__main__":

    import sys

    configs = read_feature_config(os.path.join(BASEDIR, SECTION_FEATURE_FILE))[0][1]
    configs = dict(configs)
    configs.update(read_properties(os.path.join(BASEDIR, PATH_FILE)))
    configs.update(read_properties(os.path.join(BASEDIR, DB_FILE)))

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-o", "--output_path", dest="output_path", help="Set output path", default=configs["output_path"])
    parser.add_option("-l", "--log_path", dest="log_path", help="Set log path", default=configs["log_path"])
    parser.add_option("-b", "--block_label", dest="block_label", type="int", help="If feature contains block label. 1(Yes), 0(No)", default=configs["block_label"])
    parser.add_option("-t", "--table_header", dest="table_header", type="int", help="If feature contains table header. 1(Yes), 0(No)", default=configs["table_header"])
    parser.add_option("-T", "--title_tfidf", dest="title_tfidf", type="int", help="If feature contains title tfidf, need title tfidf file. 1(Yes), 0(No)", default=configs["title_tfidf"])
    parser.add_option("-d", "--document_tfidf", dest="document_tfidf", type="int", help="If feature contains document tfidf, need document tfidf file. 1(Yes), 0(No)", default=configs["document_tfidf"])
    parser.add_option("-n", "--no_feature", dest="no_feature", type="int", help="If extract no feature files and save. 1(Yes), 0(No)", default=configs["no_feature"])
    parser.add_option("-c", "--label_common", dest="label_common", type="int", help="If only retain labels which occur twice. 1(Yes), 0(No)", default=configs["label_common"])
    parser.add_option("-D", "--sample_filter_dir", dest="sample_filter_dir", help="Use samples in specific dir", default=configs["sample_filter_dir"])
    parser.add_option("-f", "--sample_filter_file", dest="sample_filter_file",help="Use samples in specific list, the sample list is read from sample_filter_file", default=configs["sample_filter_file"])
    parser.add_option("-C", "--collection", dest="mongo.collection", type="string", help="DB collection", default=configs["mongo.collection"])

    (options, args) = parser.parse_args()
    options = vars(options)

    if len(options) > 1:
        configs.update(options)

    file_cfg = os.path.join(BASEDIR, FILE_FILE)

    run(configs, file_cfg)
