#/usr/bin/python2.7
#-*-coding:utf-8-*-

from classify_preprocess import *

ATTR_MAX_LINK = 3
ATTR_MIN_INLINK = 0
HUB_MIN_LINK = 2

def detect_hub(label_count,linknum):
    """
    提取hub文档
    依据规则：
        1. section label数量为0
        2. 文档内链接数量大于HUB_MIN_LINK
    Args:
        label_count: dict, k:sample id, v: section label count
        linknum:     dict, k:sample id, v:link count
    Returns:
        files: list, hub samples id 
        sample_class: dict, k:sample id, v:class name,"目录"
    """
    files = []
    for k,v in label_count.items():
        if v == 0:
            if not linknum.has_key(k):
                continue
            if linknum[k] > HUB_MIN_LINK:
                files.append(k)
    files = set(files)
    sample_class = dict((f,"hub") for f in files)
    return files,sample_class


def detect_attributefile(label_count,inlink,links):
    files = []

    for k,v in inlink.items():
        if label_count.has_key(k) and label_count[k] == 0 and v > ATTR_MIN_INLINK:
            if not links.has_key(k):
                files.append(k)
            elif len(links[k]) < ATTR_MAX_LINK:
                files.append(k)

            if links.has_key(k) and len(links[k]) > 0 and v > 1:
                #print k,"has outlink"
                for l in links[k]:
                    files.append(l)
    files = set(files) #去重
    sample_class = dict((f,u"属性") for f in files)

    return files, sample_class

def run():
    db = DB("../../conf/conf.properties")
    #sample_block,label_block,class_block = read_xls()
    sample_block = db.get_allid()
    label_block = db.get_sample2section()
    label_count = section_label_count(sample_block,label_block)
    
    links,linknum = get_link("../../data/docparse/outlink.txt")
    inlinks,inlinknum = get_link("../../data/docparse/inlink.txt")

    print "hub_attributefile"
    hubs,hub_class = detect_hub(label_count, linknum)
    print "hub len:",len(hubs)
    for i in hubs:
        print i.encode("utf-8")

    #write_class_to_file("hub_class.csv",hubs,hub_class)

    print "detect_attributefile"
    attrfiles,attr_class = detect_attributefile(label_count,inlinknum,links)
    print "attr len:",len(attrfiles)
    for i in attrfiles:
        print i.encode("utf-8")

    #write_class_to_file("attr_class.csv",attrfiles,attr_class)

if __name__=="__main__":
    run()
