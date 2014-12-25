#!/usr/bin/python
#-*-coding-UTF-8-*-

import os

import csvio 
from global_config import *

c = csvio.CSVIO(os.path.join(RESULT_PATH, DEFAULT_RESULT_NAME))
for s,d in c.content.items():
    si = c.fields.index('section label')
    sl = d[si]
    bi = c.fields.index('block label')
    bl = d[bi]
    if len(sl) > 0 or len(bl) > 0:
        print s.encode('utf-8')
        print "section label:"
        for l in sl.split("#"):
            print "    "+l.encode('utf-8')
        print "block label:"
        for l in bl.split("#"):
            print "    "+l.encode('utf-8')
        print ""

