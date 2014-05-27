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
    with open("hubfiles") as f:
        lines = f.readlines()
        i = 3
        for line in lines[i*10:(i+1)*10]:
            line = line.strip("\n").decode("utf-8")
            line = line.replace("etc","/mnt/wind/tsinghua/CMCC")
            line = line[:-1]
            line = line.rstrip("/")
            open_file(line)


