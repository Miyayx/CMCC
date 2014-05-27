#/usr/bin/env/python2.7
#encoding=utf-8

"""
从文件读取数据的相关代码
"""
from utils import *

import codecs

def read_xls():
    """
    read_xls() -> (list, dict, dict)
    文档分类表中含有文档id（路径+标题），文档section label和人为分类的类别
    Returns：
        1. 所有样本id（路径+标题） list
        2. dict (k:样本id v:对应section labels)
        3. dict (k:样本id v:对应类别)
    """
    import xlrd
    data = xlrd.open_workbook('../etc/文档分类表.xls')
    table = data.sheets()[0]
    samples = table.col_values(0)[1:]
    classes = table.col_values(2)[1:]
    labels = table.col_values(3)[1:]
    sample_class = {}
    sample_labels = {}
    for i in range(2,len(samples)):
        sample_class[samples[i]] = classes[i]
        sample_labels[samples[i]] = [l.strip().rstrip() for l in labels[i].split() if len(l) > 1] # >1 delete space
       
    samples = [s for s in samples if u'4G数据集' not in s]
    return samples[2:],sample_labels,sample_class

def read_all_class(fn):
    sample_class = {}
    class_samples = {}
    with open(fn) as f:
        line = f.readline().strip("\n").decode("utf-8")
        while line:
            c,samples = line.split("\t\t")
            class_samples[c] = samples.split(";;;")
            for s in samples.split(";;;"):
                sample_class[s] = c
            line = f.readline().strip("\n").decode("utf-8")
        return sample_class, class_samples     

def write_class_to_file(fn,s2c):
    """
    以 文档id，类别为格式的文件
    """
    with codecs.open(fn,"a","utf-8") as f:
        for s,c in s2c.items():
            f.write(s+","+c+"\n")

def read_segmentation(fn):
    """
    Returns:
        sent_segs: k:sentence, v:list of words
    """
    with open(fn) as f:
        sent_segs = {}
        line = f.readline().strip("\n").strip("\r").decode("utf-8")
        while line:
            sentence,segs = line.split("\t\t")
            ws = []
            for s in segs.split():
                ws.append(s.split("/")[0])
            if not sentence.endswith("/"):
                sentence += "/"
            sent_segs[sentence] = ws
            line = f.readline().strip("\n").strip("\r").decode("utf-8")
        return sent_segs

def segmetation_result(sent_segs, filename = ""):
    """
    Args:
        filename: title keyword file name, if there is a filename, write result to the file
    """
    word_freq = {}
    for v in sent_segs.values():
        for w in v:
            word_freq[w] = word_freq.get(w,0) + 1
    sorted_word_freq = sorted(word_freq.items(),key = lambda x:x[1],reverse=True)

    if len(filename) > 0:
        with open(filename, "w") as f:
            for k,v in sorted_word_freq:
                f.write(k.encode("utf-8")+" "+str(v)+"\n")

def record_tfidf(kws, doc_tfidf, fw):
    """
    因为之前求tfidf值很慢，所以把算出来的中间值写入文档
    format: sampleid\t\tkeyword1/value1 keyword2/value2 ...
    """
    with codecs.open(fw,"w","utf-8") as f:
        for k,v in doc_tfidf.items():
            s = ""
            s += k
            s += "\t\t"
            for i in range(len(kws)):
                s += kws[i]
                s += "/"
                s += str(v[i])
                s += " "
            s = s[:-1]
            s += "\n"
            f.write(s)

def read_tfidf(fn):
    """
    读取tfidf值
    """
    doc_tfidf = {}
    with open(fn) as f:
        line = f.readline().strip("\n").decode("utf-8")
        while line:
            s = line.split("\t\t")[0]
            doc_tfidf[s] = []
            items = line.split("\t\t")[1].split()
            for i in items:
                doc_tfidf[s].append(i.split("/")[1])
            line = f.readline().strip("\n").decode("utf-8")

    return doc_tfidf

def read_subsection(fn):
    """
    从文件中读取block label(目前是从数据库读取)
    """
    with open(fn) as f:
        sample_sl = {}

        line = f.readline()
        while line:
            sample,sublabel = line.strip("\n").strip("\r").decode("utf-8").split("\t")
            sample = sample.rsplit("/",2)[0]+"/"
            if not sample_sl.has_key(sample):
                sample_sl[sample] = []
            sample_sl[sample].append(sublabel)
            
            line = f.readline()

        return sample_sl
