#/usr/bin/env/python2.7
#encoding=utf-8

from classify_preprocess import *
from utils import *
from synonym import *

def exist_val(data, origin, fn = None):
    """
    判断样本都有哪些特征存在非0特征值
    Args:
        data:二维数组，list of list，从features文件中读取的数据
        origin: 作为验证标准的元数据
                dict，k：样本id， v：label或关键词。
    Return:
    """
    print "data len:",len(data)
    print "origin len:",len(origin)
    fields = [d.strip("\c") for d in data[0]]
    index_list = []
    syns = get_synonym_words("../etc/synonym_dict.csv")

    left_dict = {}
    if fn:
        for l in open(fn):
            l = l.decode("utf-8")
            items =l.strip("\n").split("\t") 
            if len(items) == 1:
                left_dict[items[0]] = []
            else:
                s,ls = items
                left_dict[s] = ls.split(",")
            
    for d in data[1:]:
        print "\n==================="
        items = d
        sample = items[0]
        try:
            ls = set(origin[sample])
        except Exception,e:
            print "WARNING:",sample.encode("utf-8"),"has no labels"
            continue
        print u'sample:',sample.encode("utf-8")
        mine_index = [i for i in range(1,len(items)) if float(items[i]) > 0]
        f_count = len(mine_index)
        label_count = f_count+len(left_dict[sample])

        print "feature count:",f_count
        print "label count:",label_count
        print "db count: ",len(ls)
        if not (label_count == len(ls)):
            print "WARNING: Length not equal"
        print "+++++++  feature  +++++++++++++"
        for i in mine_index:
            print "    "+fields[i].encode("utf-8")
            if (not fields[i] in ls) and (fields[i] in syns):
                print "同义词：",fields[i].encode("utf-8")
        print "++++++++  origin  +++++++++++++"
        for l in ls:
            print "    "+l.encode("utf-8")
            if (l not in fields) and (l in syns):
                print "同义词：",l.encode("utf-8")
        index_list.append(mine_index)
    return index_list

def split_feature(data, begin, end):
    """
    根据feature分割特征数据集
    结果包含样本id（第1列）和指定feature值
    """
    return [d[0:1]+d[begin:end] for d in data]
    
def validation(featurefile, options):
    """
    featurefile: 特征文件名
    options格式：
    options = {
        "section":{
            "begin":1,
            "end"  :56
        },
        "block":{
            "begin":238
            "end"  :268
        }
    }

    特征验证
    section label:    exist_val
    block label: exist_val
    """
    db = DB("../../conf/conf.properties")
    with open(featurefile) as f:
        data = [l.strip("\n").decode("utf-8").split(",") for l in f.readlines()]
        print data[0]
        fields = data[0]
        if options.has_key("section"):
            #验证section label
            print "=============== section label validation ================="
            f_d = split_feature(data,options["section"]["begin"], options["section"]["end"])
            print "section feature length:",len(f_d[0])-1
            section_i = fields.index("section label")
            sample_sl = dict((d[0], d[section_i].split("#") if len(d[section_i].strip()) > 0 else []) for d in data[1:])
            exist_val(f_d, sample_sl, "../../data/Classify/others/left_section_features1.dat")

        if options.has_key("block"):
            print "=============== block label validation ================="
            f_d = split_feature(data,options["block"]["begin"], options["block"]["end"])
            print "block feature length:",len(f_d[0])-1

            block_i = fields.index("block label")
            sample_bl = dict((d[0], d[block_i].split("#") if len(d[block_i].strip()) > 0 else []) for d in data[1:])
            
            exist_val(f_d, sample_bl, "../../data/Classify/others/left_block_features1.dat" )


def run(prop_file, feature_file):

    prop = read_properties(prop_file)

    options = {
        "section":{
            "begin":2,
            "end":2+int(prop["section_count"])
        },
        "block":{
            "begin":2+int(prop["section_count"]),
            "end":  2+int(prop["section_count"])+int(prop["block_count"])
            }
    }
    validation(feature_file,options)

if __name__=="__main__":
    run("../conf/file_col.properties", "../../data/Classify/result_features1.csv")

