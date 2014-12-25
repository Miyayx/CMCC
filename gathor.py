#!/usr/bin/python
#encoding=utf-8

from db import *
from csvio import *
from global_config import *
import sys

"""
本文件主要负责集合所有迭代的分类结果，写入到大表中
"""

def gather_one_file(fn, all_s_c):
    """
    将所有classX列的结果集合到第二列Class中
    """
    csv = CSVIO(fn)
    csv.column("Class",all_s_c)
    #csv.insert_column("Class", 1, all_s_c)
    csv.write(fn)

def get_sample2class(fn):
    """
    从大表抽取所有分类数据到dict中，根据classX列名标志
    Returns
    ----------------------
      all_s_c:所有分类的信息，dict key：sampleid， value：分类结果
    
    """
    print "Extracting classes from %s"%fn
    csv = CSVIO(fn)
    all_s_c = {}
    for i in xrange(1,sys.maxint):
        try: #遍历所有classX直到没有这个class，证明已经遍历完了，抛出异常，遍历停止
            class_i = csv.fields.index("class"+str(i))
        except Exception,e:
            print e
            break
        s_c = csv.read_one_to_one(0,class_i)
        for k,v in s_c.items():
            if len(v.strip()) == 0 or v.strip() == "others":
                s_c.pop(k) #删除负例
        all_s_c.update(s_c)
    print "Class Num:",len(all_s_c)

    return all_s_c

def get_sample2class2(fn):
    """
    从文件中抽取所有人工标注的分类结果到dict中
    Returns
    ----------------------
      s_c:所有分类的信息，dict key：sampleid， value：分类结果
    
    """
    print "Extracting classes from %s"%fn
    csv = CSVIO(fn, header=False)
    s_c = csv.read_one_to_one(0,1)
    return s_c

def write_to_mongo(s_c, collection=None):
    """
    把所有标注信息写入数据库,写到document level的absConcept字段中
    """
    print "Writing to mongo collection:",collection
    db = DB(c=collection)
    db.insert_class(s_c)

if __name__=="__main__":
    import time
    import os
    from utils import *
    start = time.time()

    configs = read_properties(os.path.join(BASEDIR, DB_FILE))

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-C", "--collection", dest="collection", type="string", help="DB collection", default=configs["mongo.collection"])
    parser.add_option("-o", "--output_path", dest="output_path", help="Set output path where result file exists", default=RESULT_PATH)
    parser.add_option("-f", "--filename", dest="filename", help="Set filename", default=DEFAULT_RESULT_NAME)
    parser.add_option("-n", "--no_feature", dest="no_feature", help="No feature filenames, split by ,", default="")

    (options, args) = parser.parse_args()

    fn = os.path.join(options.output_path, options.filename)
    all_s_c = get_sample2class(fn)
    gather_one_file(fn, all_s_c) #结果都汇总到Class列中

    if len(options.no_feature) > 0: #如果有其他的标注结果需要写入
        print "Add no_feature file samples"
        for n in options.no_feature.split(','):
            fn2 = os.path.join(options.output_path, n)
            all_s_c.update(get_sample2class2(fn2))
    write_to_mongo(all_s_c, options.collection)

    print "Time Consuming:",(time.time()-start)


