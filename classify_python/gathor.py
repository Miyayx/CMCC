#!/usr/bin/python
#encoding=utf-8

from csvio import *
import sys

def gather_one_file(fn):
    all_s_c = get_sample2class(fn)
    csv = CSVIO(fn)
    #csv.column("Class",all_s_c)
    csv.insert_column("Class", 1, all_s_c)
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
    for i in range(1,sys.maxint):
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

    return all_s_c

if __name__=="__main__":
    import sys
    import time
    start = time.time()

    if len(sys.argv) == 1:
        gather_one_file("../../data/Classify/result_features1.csv")
    if len(sys.argv) == 2:
        gather_one_file(sys.argv[1])

    if len(sys.argv) > 2:
        gather_multi_file(sys.argv[1:-1], sys.argv[-1])

    print "Time Consuming:",(time.time()-start)


    
