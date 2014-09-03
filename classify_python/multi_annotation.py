#!/usr/bin/python2.7
#encoding=utf-8

import ConfigParser

def read_config(cfg_file):
    configs = {}
    con = ConfigParser.RawConfigParser()
    con.read(cfg_file)
    configs = dict((o, con.get("multi_annotation",o)) for o in con.options("multi_annotation"))
    return configs

def multi_annotation(cfg_file, a_file, iter_n):
    configs = read_config(cfg_file)
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
            a_result[s] = c_c(c)
        else:
            a_result[s] = configs["neg_class"].decode("utf-8")

    csv.column("flag"+str(iter_n), a_result)
    csv.column("class"+str(iter_n), a_result)
    csv.write(a_file, sort_index = cluster_i)

if __name__=="__main__":
    import sys
    if len(sys.argv) < 2:
        print "Need Iteration Num for Argument"
         
    iter_n = sys.argv[1]
    import time
    start = time.time()

    from utils import *
    from cluster import *

    props = read_properties(PROP_FILE)
    props.update(read_properties(NAME_FILE))
    props["file_path"] = "../"+props["file_path"].strip("/")+"/"

    data_file = props["file_path"]+props["result"].replace('Y',props["featureid"])

    multi_annotaion("../conf/multi_annotation.cfg", data_file, iter_n)

    print "Time Consuming:",(time.time()-start)
