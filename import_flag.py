#!/bin/usr/python
#-*-coding=UTF-8-*-
import sys
from pymongo import *

from db import *
from csvio import *
from global_config import *

def extract_flag(fn):
    """
    从大表抽取所有标注数据到dict中，根据flagX列名标志
    Returns
    ----------------------
      all_s_f:所有标注的信息，dict key：sampleid， value：标注结果
    """
    print "Extracting flags from %s"%fn
    csv = CSVIO(fn)
    all_s_f = {}
    for i in range(1, 1000000):
        try:#遍历所有classX直到没有这个class，证明已经遍历完了，抛出异常，遍历停止
            flag_i = csv.fields.index("flag"+str(i))
        except Exception,e:
            print e
            break
        s_f = csv.read_one_to_one(0,flag_i)
        for k,v in s_f.items():
            if len(v.strip()) == 0 or v.strip() == "others":
                s_f.pop(k)#删除负例
        all_s_f.update(s_f)

    return all_s_f

def extract_flag2(fn):
    """
    从指定文件(两列)中抽取标注数据到dict中
    Returns
    ----------------------
      s_f:所有标注的信息，dict key：sampleid， value：标注结果
    """
    print "Extracting flags from %s"%fn
    csv = CSVIO(fn, header=False)
    s_f = csv.read_one_to_one(0,1)
    return s_f

def gather_flag(fn, s_f):
    """
    把所有标注结果写入fn文件的Class列
    """
    csv = CSVIO(fn,append=False)
    csv.column("sample", dict((s,s) for s in s_f.keys()))
    csv.column("Class",s_f)
    csv.write(fn)

def write_to_mongo(s_f, collection):
    """
    把所有标注信息写入数据库,写到document level的flag字段中
    """
    print "Flag Num:",len(s_f)
    print "Writing to mongo collection:",collection
    db = DB(c=collection)
    db.insert_flag(s_f)

if __name__ == "__main__":
    import sys
    import os
    from utils import *

    configs = read_properties(os.path.join(BASEDIR, DB_FILE))

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-C", "--collection", dest="collection", type="string", help="DB collection", default=configs["mongo.collection"])
    parser.add_option("-o", "--output_path", dest="output_path", help="Set output path where result file exists", default=PATH_CONFIG['output_path'])
    parser.add_option("-f", "--filename", dest="filename", help="Set filename", default=DEFAULT_RESULT_NAME)
    parser.add_option("-n", "--no_feature", dest="no_feature", help="No feature filenames, split by ,", default="")

    (options, args) = parser.parse_args()

    output_path = os.path.join(BASEDIR, options.output_path)
   
    fn = os.path.join(output_path, options.filename)

    s_f = extract_flag(fn)
    if len(options.no_feature) > 0:
        print "Add no_feature file samples"
        for n in options.no_feature.split(','):
            fn2 = os.path.join(output_path, n)
            s_f.update(extract_flag2(fn2))

    gather_flag(os.path.join(output_path, "flag_record.csv"), s_f)
    write_to_mongo(s_f, options.collection)

