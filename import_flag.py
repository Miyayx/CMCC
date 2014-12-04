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
    csv = CSVIO(fn)
    all_s_f = {}
    for i in range(1, 1000000):
        try:
            flag_i = csv.fields.index("flag"+str(i))
        except Exception,e:
            print e
            break
        s_f = csv.read_one_to_one(0,flag_i)
        for k,v in s_f.items():
            if len(v.strip()) == 0 or v.strip() == "others":
                s_f.pop(k)
        all_s_f.update(s_f)

    return all_s_f

def gather_flag(fn, s_f):
    """
    把所有标注结果写入fn文件的Class列
    """
    csv = CSVIO(fn)
    csv.column("sample", dict((s,s) for s in s_f.keys()))
    csv.column("Class",s_f)
    csv.write(fn)

def write_to_mongo(s_f):
    """
    把所有标注信息写入数据库,写到document level的flag字段中
    """
    print "Flag Num:",len(s_f)
    print "Writing to mongo..."
    db = DB()
    db.insert_flag(s_f)

if __name__ == "__main__":
    import sys
    import os

    fn = sys.argv[1] if len(sys.argv) > 2 else DEFAULT_RESULT_NAME

    s_f = extract_flag(os.path.join(RESULT_PATH, fn))
    gather_flag(os.path.join(RESULT_PATH, "flag_record.csv"), s_f)
    write_to_mongo(s_f)

