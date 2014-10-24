
from db import *

db = DB("../../conf/conf.properties")
sample_seg = {}
coll = db.collection.find({"level":"section"})
for c in coll:
    sample = c["_id"]["path"]
    kws = ""
    if c.has_key("splitwords"):
        kws = c["splitwords"]
    sample_seg[sample] = sample_seg.get(sample,"")+kws

import codecs
with codecs.open("document_segmentation.txt", "w","utf-8") as f:
    for k,v in sample_seg.items():
        f.write(k+"\t"+v+"\n")

