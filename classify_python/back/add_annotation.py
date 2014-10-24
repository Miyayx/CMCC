#!/usr/bin/python
#encoding=utf-8

from csvio import *


a_file = "../../data/Classify/cluster20_f1_result_annotation.csv"
a_csv  = CSVIO(a_file, separator="\t")
print a_csv.fields
a_result = a_csv.read_one_to_one(0,a_csv.fields.index("class20"))

result = "../../data/Classify/result_features1.csv"
csv = CSVIO(result)
csv.column("class20", a_result)
csv.write(result)
