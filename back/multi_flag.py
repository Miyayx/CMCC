#!/usr/bin/python2.7
#encoding=utf-8

import ConfigParser
from utils import *
import os
from global_config import *
from csvio import *

def read_config(cfg_file):
    configs = {}
    con = ConfigParser.RawConfigParser()
    con.read(cfg_file)
    configs = dict((o, con.get("multi_flag",o)) for o in con.options("multi_flag"))
    return configs

def multi_annotation(configs, a_file, iter_n):

    pos_c = configs["cluster"].split(",")
    pos_classes = configs["pos_class"].decode("utf-8").split(",")
    assert len(pos_c) == len(pos_classes)
    c_c = dict((pos_c[i], pos_classes[i]) for i in range(len(pos_c)) )

    csv = CSVIO(a_file)

    cluster_i = csv.fields.index("cluster"+str(iter_n))

    a_result = {}
    s_c = csv.read_one_to_one(0, cluster_i)
    for s, c in s_c.items():
        if c in pos_c:
            a_result[s] = c_c[c]
        elif len(c.strip()) == 0:
            continue
        else:
            a_result[s] = configs["neg_class"].decode("utf-8")

    csv.column("flag"+str(iter_n), a_result)
    csv.column("class"+str(iter_n), a_result)
    csv.write(a_file, sort_index = cluster_i)

if __name__=="__main__":
    import sys

    configs = read_properties(os.path.join(BASEDIR, PROP_FILE))
    configs.update(read_properties(os.path.join(BASEDIR, NAME_FILE)))
    configs.update(read_properties(os.path.join(BASEDIR, PATH_FILE)))
    configs.update(read_config(os.path.join(BASEDIR, MULTI_ANNOTATION_FILE)))
    configs.update(read_properties(os.path.join(BASEDIR, DB_FILE)))

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--iter", dest="iter", type="int", help="Iteration of Classify", default=-1)
    parser.add_option("-f", "--featureid", dest="featureid", type="int", help="Feature id", default=configs["featureid"])
    parser.add_option("-c", "--cluster", dest="cluster", type="string", help="Positive sample cluster ids, split by . Example:0,2,3", default=configs["cluster"])
    parser.add_option("-p", "--pos_class", dest="pos_class", type="string", help="Positive class name", default=configs["pos_class"])
    parser.add_option("-n", "--neg_class", dest="neg_class", type="string", help="Negative class name", default=configs["neg_class"])
    parser.add_option("-C", "--collection", dest="mongo.collection", type="string", help="DB collection which provides flag info", default=configs["mongo.collection"])

    (options, args) = parser.parse_args()

    if not options.iter or options.iter < 0:
        print "Need Iteration Num for Argument"
        exit()

    configs.update(vars(options))

    iter_n = str(configs['iter'])

    import time
    start = time.time()

    data_file = os.path.join(RESULT_PATH, configs["result"].replace('Y', str(configs["featureid"])))

    multi_annotation(configs, data_file, iter_n)

    print "Time Consuming:",(time.time()-start)
