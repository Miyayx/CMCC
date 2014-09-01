#/usr/bin/env/python2.7
#encoding=utf-8

"""
这段程序用来对特征进行验证。
四种特征：section label， title keyword， block label， content keyword
验证主要分两部分：
1. 对一个样本，是否存在某特征，通过判断此特征值是否大于0
    验证输出有：1）某种特征实际特征数量与计算特征数量对比
                2）某种特征实际存在特征与计算特征对比
2. 对于以tfidf为特征值的特征，用第三方类库gensim判断其tfidf是否正确
    验证输出有：1）关键词列表
                2）关键词计算出的tfidf值与第三方gensim的tfidf值的对比
验证结果可直接输出到文件中, python validation > filename
"""

from classify_preprocess import *
from db import *
from utils import *
from synonym import *

TITLE_SPLIT = "../etc/title_word_segmentation.txt"
KEYWORD_SPLIT = "../etc/document_segmentation.txt"

def title_keyword_val(data):
    """
    
    """
    fields = data[0]
    for d in data[1:]:
        print "\n======================="
        items = d
        sample = items[0]
        mine_index = [i for i in range(1,len(items)) if float(items[i]) > 0]
        if len(mine_index) == 0:
            print "WARNING:",sample.encode("utf-8"),"has no title keywords"
        print u'sample:',sample.encode("utf-8")
        print "feature count:", len(mine_index)
        for i in mine_index:
            print "    "+fields[i].encode("utf-8")

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

def tfidf_reverse(featurefile, kws, doc_segs):
    import math
    with open(featurefile) as f:
        line = f.readline().strip("\n").decode("utf-8")
        line = f.readline().strip("\n").decode("utf-8")
        n = len(doc_segs) 
        while line:
            doc = line.split(",")[0]
            seg = doc_segs[doc]
            print doc
            all_count = 0 #所有词出现的总数
            for kw in kws:
                all_count += seg.count(kw)
            print "all_count",all_count
            for i in range(len(kws)):
                kw = kws[i]
                #if seg.count(kw) == 0:
                #    continue
                tf = seg.count(kw)/float(all_count)
                kw_in_doc = len([d for d,s in doc_segs.items() if kw in s]) #kw出现在多少个文档中
                if kw_in_doc == 0:
                    continue
                r = n/float(kw_in_doc)
                idf = math.log(r) 
                tfidf = float(line.split(",")[i+1])
                tf2 = tfidf/idf
                count = tf2*all_count
                print kw+":origin count = "+str(seg.count(kw))
                print kw+":calculate count = "+str(count)

            line = f.readline().strip("\n").decode("utf-8")


def tfidf_val(data, seg_file):
    """
    tfidf验证过程
    Args:
        data:二维数组，list of list，从features文件中读取的数据
        seg_file: 存有分词结果的文件名
    """
    print "\n\n==================  TFIDF CHECK  ===================="
    doc_segs = read_segmentation(seg_file) #读取分词结果，在classify_pre_process.py中
    words = data[0][1:] #关键词列表
    id2word = dict((i,words[i]) for i in range(len(words)))

    fields = data[0]
    segs = []
    docs = []
    for d in data[1:]:
        sample = d[0]
        docs.append(sample)
        segs.append(doc_segs[sample])

    ############### 使用第三方类库gensim 计算tfidf ##################
    from gensim import corpora, models
    dictionary = corpora.Dictionary()

    corpus = [dictionary.doc2bow(seg,allow_update=True) for seg in segs]
    
    tfidf = models.TfidfModel(corpus, id2word=id2word, normalize=True)
    corpus_tfidf = tfidf[corpus]
    c = tfidf[corpus[0]]
    i = 0
    for c in corpus_tfidf:
        print "=============================================="
        items = data[i+1]
        print items[0].encode("utf-8")+"\n"
        ks = "特征词:  "
        for k,v in c:
            ks += dictionary[k]
            ks += " "
        print ks+"\n"
        print "第三方tfidf:" 
        print sorted(c, key=lambda x:x[1])
        #print [data[i][j] for j in index_list[i]]
        #print [j for j in range(1,len(items)) if float(items[j]) > 0]
        from gensim import matutils
        print "\n自己的tfidf:" 
        print sorted(matutils.unitvec([(j,float(items[j])) for j in range(1,len(items)) if float(items[j]) > 0]), key=lambda x:x[1])
        i += 1

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
        "title":{
            "begin":57,
            "end"  :237
        },
        "block":{
            "begin":238
            "end"  :268
        },
        "keyword":{
            "begin":269,
            "end":None
        }
    }

    特征验证
    section label:    exist_val
    title:            exist_val, tfidf_val
    block label: exist_val
    keyword:          exist_val, tfidf_val

    """
    db = DB("../../conf/conf.properties")
    with open(featurefile) as f:
        data = [l.strip("\n").decode("utf-8").split(",") for l in f.readlines()]
        if options.has_key("section"):
            #验证section label
            print "=============== section label validation ================="
            d = split_feature(data,options["section"]["begin"], options["section"]["end"])
            print "section feature length:",len(d[0])-1
            label_block = db.get_sample2section()
            exist_val(d, label_block, "left_section.dat")

        if options.has_key("title"):
            d = split_feature(data,options["title"]["begin"], options["title"]["end"])
            print "title feature length:",len(d[0])-1
            title_keyword_val(d)

        if options.has_key("title_itfdf"):
            d = split_feature(data,options["title"]["begin"], options["title"]["end"])
            print "title feature length:",len(d[0])-1
            s2title = read_segmentation(TITLE_SPLIT)
            exist_val(d, s2title)
            tfidf_val(d, TITLE_SPLIT)

        if options.has_key("block"):
            print "=============== block label validation ================="
            d = split_feature(data,options["block"]["begin"], options["block"]["end"])
            print "block feature length:",len(d[0])-1

            sample_sl = db.get_sample2subsection()
            
            exist_val(d, sample_sl, "left_block.dat" )

        if options.has_key("keyword"):
            d = split_feature(data,options["keyword"]["begin"], options["keyword"]["end"])
            print "keyword feature length:",len(d[0])-1
            #db = DB()
            #s2k = db.get_sample2keywords()
            s2k = read_segmentation(KEYWORD_SPLIT)
            exist_val(d, s2k)
            tfidf_val(d, KEYWORD_SPLIT)

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


