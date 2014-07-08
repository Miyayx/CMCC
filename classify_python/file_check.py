#!/usr/bin/python2.7
#-*-coding:utf-8-*-

from db import DB

def file_check(files, path):
    import os
    try:
        os.mkdir(path)
    except:
        pass

    db = DB("../../conf/conf.properties")
    from utils import *
    left = files
    print "Left Num:",len(left)
    #print "WordDoc Num:",[db.is_word(i) for i in attrfiles].count(True)
    items = []
    items = common_items(files,db.get_word_doc())
    write_lines(path+"doc.dat", items)
    print "WordDoc Num:",len(items)
    left = delete_items(left, items)
    print "Left Num:",len(left)

    items = [i for i in files if db.no_meaning(i)]
    write_lines(path+"no_meaning.dat", items)
    print "Has No Meaning Num:",len(items)
    left = delete_items(left, items)
    print "Left Num:",len(left)

    items = [i for i in files if db.has_one_img(i)]
    write_lines(path+"one_img.dat", items)
    print "Has One Img Num:",len(items)
    left = delete_items(left, items)
    print "Left Num:",len(left)

    items = [i for i in files if db.has_img(i)]
    write_lines(path+"img.dat", items)
    print "Has Img Num:",len(items)
    left = delete_items(left, items)
    print "Left Num:",len(left)

    items = [i for i in files if db.has_one_big_table(i)]
    write_lines(path+"one_table.dat", items)
    print "Has One Table Num:",len(items)
    left = delete_items(left, items)
    print "Left Num:",len(left)

    items = [i for i in files if db.has_table(i)]
    write_lines(path+"_table.dat", items)
    print "Has Table Num:",len(items)
    left = delete_items(left, items)
    print "Left Num:",len(left)

    items = [i for i in files if db.pure_text(i)]
    write_lines(path+"pure_text.dat", items)
    print "Pure Text Num:",len(items)
    left = delete_items(left, items)

    items = [i for i in files if db.has_block_label(i)]
    write_lines(path+"block_label.dat", items)
    print "Has Block Label Num:",len(items)
    left = delete_items(left, items)

    #items = common_items(files,hubs)
    #write_lines(path+"hub.dat", items)
    #print "Hub Num:",len(items)
    #left = delete_items(left, items)

    print "Others Num:",len(left)
    write_lines(path+"other.dat",left)

if __name__=="__main__":
    files = [line.strip("\n").decode("utf-8") for line in open("../../data/Classify/others/feature0_files.dat")]
    file_check(files, "feature0_check/")
    files = [line.strip("\n").decode("utf-8") for line in open("../../data/Classify/others/attribute_files.dat")]
    file_check(files, "attr/")

