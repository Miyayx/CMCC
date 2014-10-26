#!/usr/bin/python2.7
#encoding=utf-8

from csvio import *
from utils import *
from db import *
from random import Random
import ConfigParser
from config_global import *

"""
标注操作，目前有两种可选方法：
1. 自动标注 auto_annotaion
   通过配置文件选择的正例簇与负例簇，自动从每个簇中随机挑选指定比例的样本并进行标注
2. 使用数据库存储的人工标注信息进行标注 db_annotaion
   通过配置文件指定的正例类别，从数据库中已标注为此类别的样本作为标注正例，从其他簇中随机挑选指定比例的样本并标注成负例
"""

def read_config(cfg_file):
    """
    读取annotation配置文件
    """
    configs = {}
    con = ConfigParser.RawConfigParser()
    con.read(cfg_file)
    configs = dict((o, con.get("annotation",o)) for o in con.options("annotation"))
    return configs

def auto_annotation(cfg_file, a_file, iter_n):
    """
    根据指定的正簇号和它的类别，认为指定簇都是正例，选取其中的30%标注成指定类别
    选取其他簇的样本总数的30%为负例。应保证每个簇都有样本标注，标注数量与次簇数量成正比
    如果指定标注样本有标注记录，则从标注记录中读取原标注记录
    Args:
    ---------------------------------
      cfg_file:annotation 配置文件
      a_file  :标注结果要写入的文件
      iter_n  :第几次迭代
    """

    def choose_annotation(c_sl):
        """
        随机抽取每个簇的30%的样本作为标注数据
        Args
        c_sl:dict
            key: cluster id, value: sample list
        Returns
            被选定为标注数据的sample list
        """
        chosen = []

        total = sum(len(v) for v in c_sl.values())
        print "Total:",total
        a_total = 0.3 * total #选总数的30%
        print "Annotation:",a_total

        for c, sl in c_sl.items():
            a_num = a_total * (len(sl)*1.0/total) #根据此簇所占总样本数的比例，计算此簇应该标记的样本数量
            a_num = int(a_num)
            if a_num == 0:
                a_num = 1 #每个簇至少标记一个样本
            print "Annotate",str(a_num),"in cluster",str(c)
            r = Random()
            chosen += r.sample(sl, a_num)

        return chosen

    configs = read_config(cfg_file)
    pos_c = configs["cluster"].split(",") #正例簇号

    csv = CSVIO(a_file)

    cluster_i = csv.fields.index("cluster"+str(iter_n))

    s_c = csv.read_one_to_one(0,cluster_i)#读取聚类结果
    s_c = dict((s,c) for s,c in s_c.items() if len(c.strip()) > 0)

    pos = dict((c,[s for s in s_c.keys() if s_c[s] == c ]) for c in pos_c) #正例簇
    neg = dict((c,[s for s in s_c.keys() if s_c[s] == c ]) for c in set(s_c.values()) - set(pos_c)) #负例簇

    print "Positive Cluster:",pos.keys()
    print "Negative Cluster:",neg.keys()

    a_result = {}
    for c in choose_annotation(pos): 
        #标记正例（类别名称来源于配置文件）
        a_result[c] = configs["pos_class"].decode("utf-8")
    for c in choose_annotation(neg): 
        #标记负例（类别名称来源于配置文件）
        a_result[c] = configs["neg_class"].decode("utf-8")

    csv.column("flag"+str(iter_n), a_result)
    csv.write(a_file, sort_index = cluster_i)

def db_annotation(db_config, cfg_file, a_file, iter_n):
    """
    根据指定的正簇号和它的类别，认为指定簇都是正例，选取其中的30%标注成指定类别
    选取其他簇的样本总数的30%为负例。应保证每个簇都有样本标注，标注数量与次簇数量成正比
    如果指定标注样本有标注记录，则从标注记录中读取原标注记录
    Args:
    ---------------------------------
      db_config: db配置文件
      cfg_file:annotation 配置文件
      a_file  :标注结果要写入的文件
      iter_n  :第几次迭代
    """

    def choose_annotation(c_sl):
        """
        随机抽取每个簇的30%的样本作为标注数据
        Args
        -----------------------------------
        c_sl:dict
            key: cluster id, value: sample list
        Returns
            被选定为标注数据的sample list
        """
        chosen = []

        total = sum(len(v) for v in c_sl.values())
        print "Total:",total
        a_total = 0.3 * total #选总数的30%
        print "Annotation:",a_total

        for c, sl in c_sl.items():
            a_num = a_total * (len(sl)*1.0/total) #根据此簇所占总样本数的比例，计算此簇应该标记的样本数量
            a_num = int(a_num)
            if a_num == 0:
                a_num = 1 #每个簇至少标记一个样本
            print "Annotate",str(a_num),"in cluster",str(c)
            r = Random()
            chosen += r.sample(sl, a_num)

        return chosen

    db = DB(db_config)

    configs = read_config(cfg_file)
    pos_flag = configs["pos_class"].decode("utf-8")
    print "Pos Flag:", pos_flag

    csv = CSVIO(a_file)

    cluster_i = csv.fields.index("cluster"+str(iter_n))

    s_c = csv.read_one_to_one(0, cluster_i)#读取聚类结果
    s_c = dict((s,c) for s,c in s_c.items() if len(c.strip()) > 0)

    pos_samples = db.get_samples_from_flag(pos_flag) #获得数据库中flag=pos_flag的样本
    pos_samples = common_items(s_c.keys(), pos_samples)#保证所有正例id都在当前处理的样本id范围内
    pos_c = set([s_c[s] for s in pos_samples]) #正例簇号，所有包含正例的簇都认为是正例簇

    neg = dict((c,[s for s in s_c.keys() if s_c[s] == c ]) for c in set(s_c.values()) - set(pos_c)) #负例簇, key:簇号， value：属于此簇的样本list

    print "Positive Cluster:",pos_c
    print "Negative Cluster:",neg.keys()

    a_result = {}
    for c in pos_samples: 
        #标记正例（类别名称来源于配置文件）
        a_result[c] = pos_flag
    for c in choose_annotation(neg): 
        #标记负例（类别名称来源于配置文件）
        a_result[c] = configs["neg_class"].decode("utf-8")

    csv.column("flag"+str(iter_n), a_result)
    csv.write(a_file, sort_index = cluster_i)


if __name__=="__main__":
    import sys
    if len(sys.argv) < 2:
        print "Need Iteration Num for Argument"

    a_type = "auto" # set annotation method, default is auto_annotation
    if len(sys.argv) == 3:
        a_type = sys.argv[2]
         
    iter_n = sys.argv[1]
    import time
    start = time.time()

    from utils import *
    from cluster import *

    props = read_properties(PROP_FILE)
    props.update(read_properties(NAME_FILE))
    props.update(read_properties(PATH_FILE))

    data_file = os.path.join(props["output_path"], props["result"].replace('Y',props["featureid"]))

    if a_type == "auto":
        auto_annotation(ANNOTATION_FILE, data_file, iter_n)
    elif a_type == "db":
        db_annotation(DB_FILE, ANNOTATION_FILE, data_file, iter_n)
    else:
        print "Wrong annotation method selected."
        print "Input: auto, db"

    print "Time Consuming:",(time.time()-start)


