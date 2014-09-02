#!/usr/bin/python
#encoding=utf-8

from csvio import *

fn = "../../data/Classify/result_features1.csv"
csv = CSVIO(fn)
all_s_c = {}
for i in range(1,1000):
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

csv.column("Class",1,all_s_c)
csv.write(fn)
    
