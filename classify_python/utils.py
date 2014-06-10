#/usr/bin/python2.7
#encoding=utf-8

import codecs

def write_lines(fn,lines):
    with codecs.open(fn,'w','utf-8') as f:
        for l in lines:
            f.write(l+"\n")

def read_lines(fn):
    with open(fn) as f:
        lines = [l.strip("\n") for l in f.readlines()]
        return lines

def common_items(a,b):
    """
    Find the common element of the two lists
    Will change the sequence
    """
    return list(set(a) & set(b))

def diff_items(a,b):
    """
    Find the different element between the two lists
    Will change the sequence
    """
    return list(set(a)^ set(b))

def delete_sample(samples, regex):
    """
    用正则表达式过滤掉指定的sample
    """
    print "delete sample with str:",regex
    del_s = []
    for s in samples:
        if regex in s:
            del_s.append(s)
    print "delete sample number:",len(del_s)
    return diff_items(samples, del_s)

def filter_sample(samples, regex):
    """
    """
    print "leave samples with str:",regex
    left_s = []
    for s in samples:
        if regex in s:
            left_s.append(s)
    print "leave sample number:",len(left_s)
    return left_s
    
def read_properties(fn):
    prop = {}
    for line in open(fn):
        if line.startswith("#") or (not "=" in line):
            continue
        else:
            k,v = line.strip("\n").split("=")
            prop[k.strip()] = v.strip().lstrip()

    return prop
