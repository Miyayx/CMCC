#!/bin/usr/python
#-*-coding=UTF-8-*-
import sys
from pymongo import *

from db import *
from csvio import *

def extract_flag(fn):
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
    csv = CSVIO(fn)
    csv.column("sample", dict((s,s) for s in s_f.keys()))
    csv.column("Class",s_f)
    csv.write(fn)

def write_to_mongo(s_f):
    db = DB('../../conf/conf.properties')
    db.insert_flag(s_f)

if __name__ == "__main__":
    s_f = extract_flag("../../data/Classify/result_features1.csv")
    gather_flag("../../data/Classify/flag_record.csv", s_f)
    write_to_mongo(s_f)

