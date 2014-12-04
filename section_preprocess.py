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

    OTHERS_PATH = os.path.join(RESULT_PATH, file_configs["others_output_path"])
    FEATURE_PATH = os.path.join(RESULT_PATH, file_configs["feature_output_path"])

    if not os.path.isdir(RESULT_PATH):
        os.mkdir(RESULT_PATH)
    if not os.path.isdir(OTHERS_PATH):
        os.mkdir(OTHERS_PATH)
    if not os.path.isdir(FEATURE_PATH):
        os.mkdir(FEATURE_PATH)
    if not os.path.isdir(LOG_PATH):
        os.mkdir(LOG_PATH)

    section = configs['section']
    configs.pop('section')

    fconfigs = configs

    ############### file name ################
    result_output = os.path.join(RESULT_PATH,file_configs["result_output"] + "_" + section + ".csv")
    delete_output = os.path.join(OTHERS_PATH,file_configs["delete_output"] + "_" + section + ".dat")
    no_feature_output = os.path.join(OTHERS_PATH, file_configs["no_feature_output"] + "_" + section + ".dat")
    file_statistics = os.path.join(OTHERS_PATH, file_configs["file_statistics"] + "_" + section + ".dat")
    left_block_file = os.path.join(OTHERS_PATH, file_configs["left_block_file"] + "_" + section + ".dat")
    left_tableheader_file = os.path.join(OTHERS_PATH, file_configs["left_tableheader_file"] + "_" + section + ".dat")
    file_col = os.path.join(RESULT_PATH, file_configs["file_col"])

    log = {}

    db = DB()
    if len(fconfigs["sample_filter_str"]) > 0:
        db.filter(fconfigs["sample_filter_str"].split(","))
    if len(fconfigs["sample_filter_file"]) > 0:
        db.filter(fconfigs["sample_filter_file"],type="file")

    class_block = {}
    sample_block = db.get_section2sectionlabel().keys()
    all_sample = sample_block

    log["total"] = len(sample_block)

    #Delete samples whose name has ','
    sample_block = delete_sample(sample_block, u',')
    write_lines(delete_output, diff_items(all_sample, sample_block))
    log["delete_sample"] = len(diff_items(all_sample, sample_block))

    #Leave samples with str
    #sample_block = filter_sample(sample_block, u'04-资费')

    #After delete all specific samples, reset allsample in db
    db.set_allsample(sample_block)

    features = []
    fields = []

    if os.path.exists(result_output):
        os.remove(result_output)

    fields.append(["Class"])
    features.append(dict((k,"") for k in sample_block))

    ###################  block label  ####################

    if fconfigs.has_key("block_label") and fconfigs["block_label"]:
        o_sample_bl = db.get_section2block()

        sample_bl = filter_label(o_sample_bl)

        blabels, blabel_feature = subsection_label_feature(sample_block, sample_bl, fconfigs["label_common"])
        fields.append(blabels)
        features.append(blabel_feature)

        record_left_label(o_sample_bl, blabels, left_block_file)

    ###################  table header  ###################
    if fconfigs.has_key("table_header") and fconfigs["table_header"]:
        o_table_header = db.get_section2header()
        table_header = filter_label(o_table_header)

        headers, h_feature = table_header_feature(sample_block, table_header)
        fields.append(headers)
        features.append(h_feature)

        record_left_label(o_table_header, headers, left_tableheader_file)

    ################## title keyword tfidf  #####################
    if fconfigs.has_key("title_tfidf") and fconfigs["title_tfidf"]:
        sent_segs = read_segmentation(file_configs["title_word_segmentation"])
        sec_keywords = dict((k, sent_segs[k.rsplit("/",2)[0]]) for k in sample_block)

        title_keywords, title_tfidf = tfidf_gensim(sec_keywords)

        fields.append(title_keywords)
        features.append(title_tfidf)

    ###################  content keyword  ###################
    if fconfigs.has_key("content_tfidf") and fconfigs["content_tfidf"]:
        sec_segs = db.section_segmentation()

        kws, kw_feature = tfidf_gensim(sec_segs)
        print "number of content keywords:",len(kws)

        fields.append(kws)
        features.append(kw_feature)

   ##################################################  feature file output  ########################################

    #outfile = os.path.join(FEATURE_PATH, section+".csv")

    #先写个原始的feature文件
    #write_dataset(sample_block, feature_fields(fields), features, class_block, fconfigs["split"], outfile)

    ############## record feature count ##############
    if fconfigs["block_label"] or fconfigs['title_tfidf'] or fconfigs['content_tfidf']:
        count = 1
        with codecs.open(file_col,"w") as f:
            if fconfigs["block_label"]:
                f.write("block_count="+str(len(fields[count]))+"\n")
                count += 1
            if fconfigs["table_header"]:
                f.write("table_header="+str(len(fields[count]))+"\n")
                count += 1
            if fconfigs["title_tfidf"]:
                f.write("title_tfidf_count="+str(len(fields[count]))+"\n")
                count += 1
            if fconfigs["content_tfidf"]:
                f.write("content_tfidf_count="+str(len(fields[count]))+"\n")
                count += 1
            f.write("feature_count="+str(len(feature_fields(fields))))

    fields.append(["sample2"])
    features.append(dict((k,k) for k in sample_block))

    # 添加对应的section label
    s_sl = db.get_section2sectionlabel()
    fields.append(["section label"])
    features.append(dict((k,s_sl[k]) for k in sample_block ))

    s_b = db.get_section2block()
    t_h = db.get_section2header()

    # 添加对应的block label
    if fconfigs["block_label"]:
        fields.append(["block label"])
        features.append(dict((k,"#".join(s_b[k])) for k in sample_block ))

    # 添加表头列
    if fconfigs["table_header"]:
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
    if fconfigs["no_feature"]:
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
        
        sorted(sample_block)

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
    file_cfg = os.path.join(BASEDIR, FILE_FILE)

    if len(sys.argv) > 1:
        configs.update(parse_argv(sys.argv))

    run(configs, file_cfg)