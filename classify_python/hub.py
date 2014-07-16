#/usr/bin/python2.7
#-*-coding:utf-8-*-

from classify_preprocess import *

ATTR_MAX_LINK = 3
ATTR_MIN_INLINK = 0
HUB_MIN_LINK = 2

def detect_hub(slabel_count,linknum):
    """
    提取hub文档
    依据规则：
        1. section label数量为0
        2. 文档内链接数量大于HUB_MIN_LINK
    Args:
        slabel_count: dict, k:sample id, v: section label count
        linknum:     dict, k:sample id, v:link count
    Returns:
        files: list, hub samples id 
        sample_class: dict, k:sample id, v:class name,"目录"
    """
    files = []
    for k,v in slabel_count.items():
        if v == 0:
            if not linknum.has_key(k):
                continue
            if linknum[k] > HUB_MIN_LINK:
                files.append(k)
    files = set(files)
    sample_class = dict((f,"hub") for f in files)
    return files,sample_class


def detect_attributefile(slabel_count, blabel_count, inlinks, inlinknum, links):
    """
    提取属性文档
    依据规则：
        1. section label 数量为0
        2. 此文档被大于ATTR_MIN_INLINK个其他文档链接（有inlink）
        -3. inlink文档有section label 或 block label
        -4. link（链接）数量小于ATTR_MAX_LINK(去hub)
        -5. 若inlink数量大于1，则此文档的链接文件也是属性文件
    """

    files = []

    def inlink_has_label(k):
        for i in inlinks[k]:
            if slabel_count.has_key(i) and slabel_count[i] > 0 :
                return True
            if blabel_count.has_key(i) and blabel_count[i] > 0:
                return True
        #for i in inlinks[k]:
        #    print "inlink doc:",i
        return False

    for k,v in inlinknum.items():
        # 1,2,3
        #if not slabel_count.has_key(k) and v > ATTR_MIN_INLINK and not inlink_has_label(k):
        # 1,2
        if not slabel_count.has_key(k) and v > ATTR_MIN_INLINK:
            files.append(k)
        # 1,2,3
        #if slabel_count.has_key(k) and slabel_count[k] == 0 and v > ATTR_MIN_INLINK and not inlink_has_label(k):
        # 1,2
        if slabel_count.has_key(k) and slabel_count[k] == 0 and v > ATTR_MIN_INLINK:
            files.append(k)

            # Rule 4
            #if not links.has_key(k):
            #    files.append(k)
            #elif len(links[k]) < ATTR_MAX_LINK:
            #    files.append(k)

            # Rule 5
            #if links.has_key(k) and len(links[k]) > 0 and v > 1:
            #    print k,"has outlink"
            #    for l in links[k]:
            #        files.append(l)
    files = set(files) #去重
    sample_class = dict((f,u"属性") for f in files)

    return list(files), sample_class

def attribute_val(attrfiles, section_label, block_label, inlinks):
    for a in attrfiles:
        print ""
        print "Sample:",a.encode("utf-8")
        print "section label num:",(0 if not section_label.has_key(a) else len(section_label[a]))
        if section_label.has_key(a) and not len(section_label[a]) == 0:
            print "Error!",a.encode("utf-8")
        print "section label:"
        for s in section_label.get(a,[]):
            print s.encode("utf-8")
        print "block label num:",(0 if not block_label.has_key(a) else len(block_label[a]))
        print "block label:"
        for s in block_label.get(a,[]):
            print s.encode("utf-8")
        assert inlinks.has_key(a)
        print "Source links:"
        for i in inlinks[a]:
            print i.encode("utf-8")


def run():
    db = DB("../../conf/conf.properties")
    #sample_block,label_block,class_block = read_xls()
    sample_block = db.get_allid()
    section_label = db.get_sample2section()
    slabel_count = label_count(sample_block,section_label)
    block_label = db.get_sample2subsection()
    blabel_count = label_count(sample_block,block_label)
    
    links,linknum = get_link("../../data/docparse/outlink.txt")
    inlinks,inlinknum = get_link("../../data/docparse/inlink.txt")

    #print "hub_attributefile"
    #hubs,hub_class = detect_hub(slabel_count, linknum)
    #print "hub len:",len(hubs)
    #for i in hubs:
    #    print i.encode("utf-8")

    #write_class_to_file("hub_class.csv",hubs,hub_class)

    print "detect_attributefile"
    attrfiles,attr_class = detect_attributefile(slabel_count,blabel_count, inlinks, inlinknum, links)
    print "attr len:",len(attrfiles)
    for i in sorted(attrfiles):
        print i.encode("utf-8")

    #write_class_to_file("attr_class.csv",attrfiles,attr_class)
    attribute_val(attrfiles, section_label, block_label, inlinks)

if __name__=="__main__":
    run()
