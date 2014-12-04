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
    csv = CSVIO(fn)
    csv.column("Class",all_s_c)
    #csv.insert_column("Class", 1, all_s_c)
    csv.write(fn)

def gather_multi_file(infiles, outfile):
    all_s_c = {}
    for i in infiles:
        all_s_c.update(get_sample2class(i))
    csv = CSVIO(outfile)
    csv.column("Class",all_s_c)
    csv.write(outfile)

def get_sample2class(fn):
    csv = CSVIO(fn)
    all_s_c = {}
    for i in xrange(1,sys.maxint):
        try:
            class_i = csv.fields.index("class"+str(i))
        except Exception,e:
            print e
            break
        s_c = csv.read_one_to_one(0,class_i)
        for k,v in s_c.items():
            if len(v.strip()) == 0 or v.strip() == "others":
                s_c.pop(k)
        all_s_c.update(s_c)
    print "Class Num:",len(all_s_c)

    return all_s_c

def write_to_mongo(s_c):
    """
    把所有标注信息写入数据库,写到document level的flag字段中
    """
    print "Writing to mongo..."
    db = DB()
    db.insert_class(s_c)

if __name__=="__main__":
    import time
    import os
    start = time.time()

    if len(sys.argv) == 1:
        fn = os.path.join(RESULT_PATH, DEFAULT_RESULT_NAME)
        all_s_c = get_sample2class(fn)
        gather_one_file(fn, all_s_c)
        write_to_mongo(all_s_c)
    if len(sys.argv) == 2:
        fn = sys.argv[1]
        all_s_c = get_sample2class(fn)
        gather_one_file(fn, all_s_c)
        write_to_mongo(all_s_c)

    if len(sys.argv) > 2:
        gather_multi_file(sys.argv[1:-1], sys.argv[-1])

    print "Time Consuming:",(time.time()-start)


    
