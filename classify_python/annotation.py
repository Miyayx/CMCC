#!/usr/bin/python2.7
#encoding=utf-8

from csvio import *

from random import Random
import ConfigParser

def read_config(cfg_file):
    configs = {}
    con = ConfigParser.RawConfigParser()
    con.read(cfg_file)
    configs = dict((o, con.get("annotation",o)) for o in con.options("annotation"))
    return configs

def auto_annotaion(cfg_file, a_file, iter_n):

    def choose_annotation(c_sl):
        chosen = []

        total = sum(len(v) for v in c_sl.values())
        print "Total:",total
        a_total = 0.3 * total
        print "Annotation:",a_total

        for c, sl in c_sl.items():
            a_num = a_total * (len(sl)*1.0/total)
            a_num = int(a_num)
            print "Annotate",str(a_num),"in cluster",str(c)
            r = Random()
            chosen += r.sample(sl, a_num)

        return chosen

    configs = read_config(cfg_file)
    pos_c = configs["cluster"].split(",")

    csv = CSVIO(a_file)
    csv.load(a_file)

    cluster_i = csv.fields.index("cluster"+str(iter_n))

    s_c = csv.read_one_to_one(0,cluster_i)
    s_c = dict((s,c) for s,c in s_c.items() if len(c.strip()) > 0)

    pos = dict((c,[s for s in s_c.keys() if s_c[s] == c ]) for c in pos_c)
    neg = dict((c,[s for s in s_c.keys() if s_c[s] == c ]) for c in set(s_c.values()) - set(pos_c))

    print "Positive Cluster:",pos.keys()
    print "Negative Cluster:",neg.keys()

    a_result = {}
    for c in choose_annotation(pos):
        a_result[c] = configs["pos_class"]
    for c in choose_annotation(neg):
        a_result[c] = configs["neg_class"]

    csv.column("flag"+str(iter_n), a_result)
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

    auto_annotaion("../conf/annotation.cfg", data_file, iter_n)

    print "Time Consuming:",(time.time()-start)




