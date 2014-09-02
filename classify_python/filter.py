#!/usr/bin/python2.7
#encoding=utf-8

def is_bad_label(label):
    """
    The label which has character that makes weka disable
    """
    ch = ['"',',',"'",'%']
    for c in ch:
        if c in label:
            print "Bad label:",label
            return True
    return False

def filter_label(s2l):

    s2l = dict(s2l)

    del_pattens = [u'相关文档',ur'.*年.+月.+日',ur'.*-.+-.+-']
    
    for k,v in s2l.items():
        new_v = list(v)
        for i in v:
            if is_bad_label(i):
                new_v.remove(i)
                continue
            for p in del_pattens:
                if re.match(p, i):
                    print "Delete label:",i
                    new_v.remove(i)
                    break
        s2l[k] = new_v

    return s2l

def filter_keyword(doc_segs):

    del_pattens = [ur'\d{4}\.\d{1,2}\.\d{1,2}',ur'\d{4}\.\d{1,2}\.\d{1,2}-\d{4}\.\d{1,2}\.\d{1,2}']
    
    for k,v in doc_segs.items():
        new_v = list(v)
        for i in v:
            if is_bad_label(i):
                new_v.remove(i)
                continue
            for p in del_pattens:
                if re.match(p, i):
                    print "Delete label:",i
                    new_v.remove(i)
                    break
        doc_segs[k] = new_v

    return doc_segs

