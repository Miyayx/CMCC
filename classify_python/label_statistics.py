#!/usr/bin/python
#encoding=utf-8

import codecs

iter_n = 16

f = codecs.open("../../data/Classify/result_features1.csv",'r','utf-8');
header = f.readline().strip("\n").split(",")
class_i = header.index("class"+str(iter_n))
end = header.index("sample2")

label_num = {}

line = f.readline()
count = 1
while line:
    line = line.strip("\n").split(",")
    if line[class_i] == "others":
        for i in range(1,end):
            label_num[header[i]] = label_num.get(header[i],0)+int(line[i])
    line = f.readline()

#for k,v in label_num.items():
#    print k,v

print "label num:",len(label_num)

for i in set(label_num.values()):
    print i,label_num.values().count(i)
