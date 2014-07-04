#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
读取文件里的htm文件列表，在默认浏览器中批量打开
"""

def open_file(filepath):
    print "file:",filepath
    import sys
    import subprocess, os
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', filepath))
    elif os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', filepath))

if __name__=="__main__":
    import os
    #with open("../../data/Classify/attribute_files.txt") as f:
    with open("./attr/attr_pure_text.dat") as f:
        lines = f.readlines()
        i = 0
        for line in lines[i*10:(i+1)*10]:
            line = line.strip("\n").decode("utf-8")
            #line = line.replace("etc","/mnt/wind/tsinghua/CMCC/移动/")
            line = u"/mnt/wind/tsinghua/CMCC/移动"+line
            line = line[:-1]
            line = line.rstrip("/")
            open_file(line)


