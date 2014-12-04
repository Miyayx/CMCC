#!/usr/bin/env python
#-*-coding:utf-8-*-

from classify_preprocess import *
from utils import *
from synonym import *
from global_config import *

def exist_val(data, origin, fn = None):
    """
    判断样本都有哪些特征存在非0特征值
    Args:
    --------------------------------------
        data:二维数组，list of list，从features文件中读取的数据
        origin: 作为验证标准的元数据
                dict，k：样本id， v：label或关键词。
    Return:
    """
    print "data len:",len(data)
    print "origin len:",len(origin)
    fields = [d.strip("\c") for d in data[0]]
    index_list = []

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

        print "feature count:", f_count
        print "label count:", label_count
        print "db count: ", len(ls)
        if not (label_count == len(ls)):
            print "WARNING: Length not equal"
        print "+++++++  feature  +++++++++++++"
        for i in mine_index:
            print "    "+fields[i].encode("utf-8")
        print "++++++++  origin  +++++++++++++"
        for l in ls:
            print "    "+l.encode("utf-8")
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
        "block":{
            "begin":1,
            "end"  :56,
            "left_file":file path
        },
        "table_header":{
            "begin":238,
            "end"  :268,
            "left_file":file path
        }
    }

    特征验证
    block label: exist_val
    table header:exist_val
    """
    db = DB()
    with open(featurefile) as f:
        data = [l.strip("\n").decode("utf-8").split(",") for l in f.readlines()]
        fields = data[0]

        if options.has_key("block"):
            #验证block label
            print "=============== block label validation ================="
            f_d = split_feature(data, options["block"]["begin"], options["block"]["end"])
            print "block feature length:",len(f_d[0])-1

            block_i = fields.index("block label")
            sample_bl = dict((d[0], d[block_i].split("#") if len(d[block_i].strip()) > 0 else []) for d in data[1:])
            
            exist_val(f_d, sample_bl, options['block']['left_file'] )

        if options.has_key("table_header"):
            #验证table header
            print "=============== table header validation ================="
            f_d = split_feature(data, options["table_header"]["begin"], options["table_header"]["end"])
            print "table header feature length:",len(f_d[0])-1

            header_i = fields.index("table header")
            sample_th = dict((d[0], d[header_i].split("#") if len(d[header_i].strip()) > 0 else []) for d in data[1:])
            
            exist_val(f_d, sample_th, options['table_header']['left_file'] )


def run(props, Y):

    file_col = os.path.join(RESULT_PATH, props['file_col'])
    feature_file = os.path.join(RESULT_PATH, props['result_output']+'_'+'features'+str(Y)+'.csv')
    OTHERS_PATH = os.path.join(RESULT_PATH, props['others_output_path'])

    prop = read_properties(file_col) #get feature count from file_col file

    options = {
        "block":{
            "begin":2,
            "end":2+int(prop["block_count"]),
            "left_file":os.path.join(OTHERS_PATH, props['left_block_file']+'_features'+str(Y)+'.dat')
        },
        "table_header":{
            "begin":2+int(prop["block_count"]),
            "end":  2+int(prop["block_count"])+int(prop["table_header"]),
            "left_file":os.path.join(OTHERS_PATH, props['left_tableheader_file']+'_features'+str(Y)+'.dat')
            }
        }

    validation(feature_file,options)

if __name__=="__main__":
    props = read_properties(os.path.join(BASEDIR, PATH_FILE))
    props.update(read_properties(os.path.join(BASEDIR, FILE_FILE)))
    import sys
    Y = 1
    if len(sys.argv) == 2:
        Y = sys.argv[1]
    run(props, Y)

