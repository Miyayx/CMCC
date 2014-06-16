#/usr/bin/python2.7
#encoding=utf-8

from utils import *
from pymongo import *
from classify_preprocess import *

class DB():
    all_samples= []

    def __init__(self, configfile):
        import ConfigParser

        #读取配置文件
        #config = ConfigParser.RawConfigParser()
        #config.read(configfile)
        #ip = config.get('mongo','ip')
        #dbname = config.get('mongo','dbname')
        #cname = config.get('mongo','collection')
        config = read_properties(configfile)
        ip = config["mongo.host"]
        dbname = config["mongo.dbname"]
        cname = config["mongo.collection"]

        client = MongoClient(ip)
        db = client[dbname]
        self.collection = db[cname]

        self.all_samples = self.get_allid()

    def filter(self, regex):
        new_samples = []

        if type(regex) == str or type(regex) == unicode:
            for s in self.all_samples:
                if regex in s:
                    new_samples.append(s)
                    
        if type(regex) == list:
            for s in self.all_samples:
                for r in regex:
                    if r.decode('utf-8') in s:
                        new_samples.append(s)
                        break

        self.all_samples = new_samples


    def set_allsample(self, samples):
        self.all_samples = samples

    def get_inlink_count(self):
        """
        从数据库获取inlink信息(暂没用上)
        Returns:
            sample_inlink: dict (k:样本id v: list of link)
        """
        sample_inlink = {}
        coll = self.collection.find({"level":"document"})
        for c in coll:
            sample = (c["_id"]["path"].replace("../data","etc")+c["_id"]["name"]).strip("/")+"/"
            sample_inlink[sample] = len(c["inLink"]) if c.has_key("inLink") else 0
        return sample_inlink

    def get_link(self):
        """
        从数据库获取link(outlink)信息
        link信息在paragraph层，一个document可能有多个paragraph,因此要统计一个document中所有paragraph的link作为一个document的link信息
        Returns:
            sample_links: dict (k:样本id v: list of link)
            sample_linknum: dict (k:样本id v:link 数量)
        """
        sample_links = {}
        sample_linknum = {}
        coll = self.collection.find({"level":"paragraph"})
        for c in coll:
            sample = c["_id"]["path"].replace("../data","etc").rsplit("/",3)[0].strip("/")+"/"
            count = 0
            links = []
            if c.has_key("links"):
                links = c["links"]
                count = len(c["links"])
            else:
                continue
            if sample_links.has_key(sample):
                sample_links[sample] += links
            else:
                sample_links[sample] = links

            sample_linknum[sample] = sample_linknum.get(sample,0) + count

        return sample_links, sample_linknum

    def get_samples_in_level(self, level):
        """
        获得某一层次的文档列表
        Args:
            level:层级id
        """
        coll = self.collection.find({"level":"document","linklevel":str(level)})
        
        samples = [(c["_id"]["path"].replace("../data","etc")+c["_id"]["name"]).strip("/")+"/" for c in coll]
        return samples

    def get_keywords(self):
        """
        从mongodb中获取所有文档关键字
        Returns:
            list: 关键字列表
        """
        kw_set = set() 
        coll = self.collection.find({"level":"document"})
        for c in coll:
            if c.has_key("keyword"):
                kws = c["keyword"]
                for kw in kws.split():
                    kw = kw.strip(" ")
                    kw_set.add(kw)
        return list(kw_set)

    def read_segmentation(self):
        """
        从mongodb中获取的section层次获取分词结果，返回每个样本的分词列表
        Returns:
            dict k:文档id, v:词的列表
        """
        sample_words = {}
        coll = self.collection.find({"level":"section"})
        for c in coll:
            sample = c["_id"]["path"]
            kws = ""
            kwlist = []
            if c.has_key("splitwords"):
                kws = c["splitwords"]
            for kw in kws.split():
                kw = kw.strip()
                kwlist.append(kw.split("/")[0])
            sample_words[sample] = kwlist

        return sample_words

    def get_common_keywords(self):
        """
        统计出现次数大于1的keyword
        Returns: 
            出现次数大于1的keyword列表（所有文档范围内）
        """
        kw_count = {}
        coll = self.collection.find({"level":"document"})
        for c in coll:
            kws = ""
            if c.has_key("keyword"):
                kws = c["keyword"]
            for kw in kws.split():
                #fw = fw.strip(" ").strip("\\c")
                kw = kw.strip(" ")
                if kw_count.has_key(kw):
                    kw_count[kw] += 1
                else:
                    kw_count[kw] = 1

        return [kw for kw in kw_count.keys() if kw_count[kw] > 1]

    def get_sample2keywords(self):
        """
        返回每个文档的关键词列表
        Returns:
            s2k: dict k:sample, v: list of keywords
        """
        s2k = {}
        coll = self.collection.find({"level":"document"})
        for c in coll:
            sample = (c["_id"]["path"].replace("../data","etc")+c["_id"]["name"]).strip("/")+"/"
            kws = ""
            if c.has_key("keyword"):
                kws = c["keyword"]
            s2k[sample] = kws.split()
        return s2k

    def keyword_feature(self):
        """
        关键词特征
        Returns: 
            common_kws:出现次数大于1的keyword列表（所有文档范围内）
            kw_feature: dict(k:样本id v: keyword特征值，因keyword不止一个，因此v是个list，每个元素对应一个keyword)
        """
        kw_feature = {}
        common_kws = self.get_common_keywords()
        coll = self.collection.find({"level":"document"})
        for c in coll:
            sample = (c["_id"]["path"].replace("../data","etc")+c["_id"]["name"]).strip("/")+"/"
            kws = ""
            if c.has_key("keyword"):
                kws = c["keyword"]
            fs = []
            kws = [w.strip(" ").strip("\\c") for w in kws.split()]
            for kw in common_kws:
                if kw in kws:
                    ks.append(1)
                else:
                    ks.append(0)
            kw_feature[sample] = fs

        return common_kws, kw_feature

    def get_allid(self):
        """
        从数据库获得所有文档id(路径+标题)
        """
        coll = self.collection.find({"level":"document"})
        samples = [(c["_id"]["path"]+c["_id"]["name"]).rstrip("/")+"/" for c in coll]
        return samples

    def get_sample2section(self):
        """
        从数据库获取section label
        Return:
            s2s: dict k:sampleid, v:section label
        """
        s2s = {}
        coll = self.collection.find({"level":"section"})
        for c in coll:
            sample = c["_id"]["path"].replace("../data","etc")
            if not s2s.has_key(sample):
                s2s[sample] = set()
            label = c["label"].strip()
            #label = c["label"]
            if label and len(label) > 1 and (not self.is_bad_label(label)):
                s2s[sample].add(label)
        for s, s in s2s.items():
            s2s[sample] = list(s)
        for sample in diff_items(self.all_samples,s2s.keys()):
            s2s[sample] = []
        return s2s 

    def get_sample2subsection(self):
        """
        从数据库获取subsection label
        Return:
            s2sub: dict k:sampleid, v:subsection label
        """
        coll = self.collection.find({"level":"block"})
        s2sub = {}
        for c in coll:
            sample = c["_id"]["path"].rsplit("/",2)[-3].replace("../data","etc")+"/"
            if not s2sub.has_key(sample):
                s2sub[sample] = set() 
            if c["label"] and len(c["label"]) > 1:
                s2sub[sample].add(c["label"].strip() )
        for s, sub in s2sub.items():
            s2sub[sample] = list(sub)
        for sample in diff_items(self.all_samples,s2sub.keys()):
            s2sub[sample] = []
        return s2sub 

    def is_bad_label(self, label):
        """
        The label which has character that makes weka disable
        """
        ch = ['"',',',"'",'%','/','\']
        for c in ch:
            if c in label:
                print "Bad label:",label
                return True
        return False

    def is_word(self, f):
        """
        If the document is word
        """
        coll = self.collection.find({"level":"document"})
        f = f.strip("/").rstrip("/")

        for c in coll:
            sample = (c["_id"]["path"]+c["_id"]["name"]).strip("/").rstrip("/")
            if sample == f:
                if c.has_key("type") and c["type"] == "doc":
                    return True
                else:
                    return False
        print f.encode("utf-8"),"is not found in mongo"


if __name__ == "__main__":
    db = DB('db.config')

