#!/usr/bin/python2.7
#-*-coding:UTF-8-*-

from db import *


def read_keywords(fn):
    return [l.strip("\n").decode("utf-8") for l in open(fn)]

def has_keyword(keywords,s):
    for k in keywords:
        if k in s:
            return True
    return False

def extract_keyword():
    keywords = read_keywords("keywords")
    db = DB("../../conf/conf.properties")
    _ids = db.get_allid()
    for i in _ids:
        i = i.strip(".htm/")
        i = i.split("/")[-1]

        if has_keyword(keywords,i):
            continue

        if i[-1] == u'）':
            i = i[:i.index(u'（')]
        if i[-1] == ')':
            i = i[:i.index('(')]
        print i[:]


if __name__=="__main__":
    extract_keyword()

