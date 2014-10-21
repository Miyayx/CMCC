#/usr/bin/env/python2.7
# -*- coding:utf-8 -*-

from utils import *
from fileio import *
from db import *
from filter import *
from feature_getter import *
from classify_preprocess import read_feature_config
from classify_preprocess import read_file_config

import re
import os
import codecs
import ConfigParser


def run(file_cfg, feature_cfg, db_cfg):
    import time
    print "Begin to time!"
    time_start = time.time()

    feature_configs = read_feature_config(feature_cfg)
    file_configs = read_file_config(file_cfg)

    import os
    if not os.path.isdir(file_configs["output_path"]):
        os.mkdir(file_configs["output_path"])
    if not os.path.isdir(file_configs["others_output_path"]):
        os.mkdir(file_configs["others_output_path"])

    for section, fconfigs in feature_configs:

        ############### file name ################
        result_output = file_configs["output_path"] + file_configs["result_output"] + "_" + section + ".csv"
        delete_output = file_configs["others_output_path"] + file_configs["delete_output"] + "_" + section + ".dat"
        no_feature_output = file_configs["others_output_path"] + file_configs["no_feature_output"] + "_" + section + ".dat"
        file_statistics = file_configs["others_output_path"] + file_configs["file_statistics"] + "_" + section + ".dat"
        left_block_file = file_configs["others_output_path"] + file_configs["left_block_file"] + "_" + section + ".dat"

        log = {}

        db = DB(db_cfg)
        if len(fconfigs["sample_filter_str"]) > 0:
            db.filter(fconfigs["sample_filter_str"].split(","))
        if len(fconfigs["sample_filter_file"]) > 0:
            db.filter(fconfigs["sample_filter_file"],type="file")

        class_block = {}
        sample_block = db.get_table2header().keys()
        all_sample = sample_block

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

        import os
        if os.path.exists(result_output):
            os.remove(result_output)

        fields.append(["Class"])
        features.append(dict((k,"") for k in sample_block))

        ###################  section label  ####################
        if fconfigs["section_label"]:
            o_sample_sl = db.get_table2section()

            sample_sl = filter_label(o_sample_sl)

            slabels, slabel_feature = subsection_label_feature(sample_block, sample_sl, fconfigs["label_common"])
            fields.append(slabels)
            features.append(slabel_feature)

        ###################  block label  ####################
        if fconfigs["block_label"]:
            o_sample_bl = db.get_table2block()

            sample_bl = filter_label(o_sample_bl)

            blabels, blabel_feature = subsection_label_feature(sample_block, sample_bl, fconfigs["label_common"])
            fields.append(blabels)
            features.append(blabel_feature)

        ################## title keyword tfidf  #####################
        if fconfigs["title_tfidf"]:
            sent_segs = read_segmentation(file_configs["title_word_segmentation"])
            sec_keywords = dict((k, sent_segs[k.rsplit("/",3)[0]]) for k in sample_block)

            title_keywords, title_tfidf = tfidf_gensim(sec_keywords)

            fields.append(title_keywords)
            features.append(title_tfidf)

        ###################  table header  ###################
        if fconfigs["table_header"]:
            table_header = db.get_table2header()

            headers, h_feature = table_header_feature(sample_block, table_header)
            fields.append(headers)
            features.append(h_feature)

    #####################################################  feature file output  ########################################

        outfile = file_configs["feature_output_path"]+section+".csv"

        #先写个原始的feature文件
        #write_dataset(sample_block, feature_fields(fields), features, class_block, fconfigs["split"], outfile)

        # 添加sample id在feature列之后
        fields.append(["sample2"])
        features.append(dict((k,k) for k in sample_block))

        # 添加表格对应的section label
        if fconfigs["section_label"]:
            t_sl = db.get_table2section()
            fields.append(["section label"])
            features.append(dict((k, "#".join(t_sl[k])) for k in sample_block ))

        # 添加表格对应的block label
        if fconfigs["block_label"]:
            s_b = db.get_table2block()
            fields.append(["block label"])
            features.append(dict((k,"#".join(s_b[k])) for k in sample_block ))

        # 添加表头
        if fconfigs["table_header"]:
            t_h = db.get_table2header()
            fields.append(["table header"])
            features.append(dict((k,"#".join(t_h[k])) for k in sample_block ))

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

        record_log(file_statistics, log)

        print "Finish!"
        print "Time Consumming:",str(time.time()-time_start)

if __name__=="__main__":
    import sys
    if len(sys.argv) > 1:
        if not len(sys.argv) == 4:
            print "Wrong Argus. Need three config files"
            print "Format: python classify_preprocess.py file_config_file feature_config_file db_config_file"
        else:
            run(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        run("../conf/table_file.cfg","../conf/table_feature.cfg","../../conf/conf.properties")
