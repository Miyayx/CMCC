
#/usr/bin/python2.7
#encoding="utf-8"

from db import *

import codecs

db = DB()
keywords = db.get_keywords()
print len(keywords)
s2kw = db.get_sample2keywords()
lines = []
with open("../etc/title_word_segmentation.txt") as f:
    lines = f.readlines()
    
with codecs.open("../etc/title_word_segmentation2.txt","w") as fw:
    for line in lines:
        #line = line.strip("\n").strip("\r").decode("utf-8")
        line = line.replace("::;"," ")
        line = line.split("\t")[0]+"\t\t"+line.split("\t")[1]
        fw.write(line)
        
    
    

