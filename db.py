#/usr/bin/python2.7
#-*-coding:UTF-8-*-

from utils import *
from pymongo import *
import os
from classify_preprocess import *
from global_config import BASEDIR,DB_FILE
from bs4 import BeautifulSoup
from bs4 import BeautifulStoneSoup

class DB():
    all_samples= []

    def __init__(self, c=None, h=None, p=None, d=None):
        configfile = os.path.join(BASEDIR, DB_FILE)

        #读取配置文件
        config = read_properties(configfile)
        ip = config["mongo.host"] if not h else h
        port = config["mongo.port"] if not p else p
        port = int(port)
        dbname = config["mongo.dbname"] if not d else d
        cname = config["mongo.collection"] if not c else c

        client = MongoClient(host=ip,port=port)
        db = client[dbname]
        self.collection = db[cname]
        self.all_samples = self.get_allid()

    def filter(self, regex, type="string"):
        """
        过滤接下来要进行操作的样本，分别有string和file两种类型
        string：配置文件中以逗号分割，id中包含有此regex的sample被留下来
        file:配置文件中给一个文件路径，此文件中没一行为一个sample id，此文件中的所有sample为之后要操作的sample
        """
        new_samples = []

        if type == "string":
            if isinstance(regex,str) or isinstance(regex,unicode):
                for s in self.all_samples:
                    if regex in s:
                        new_samples.append(s)
                        
            if isinstance(regex, list):#如果
                for s in self.all_samples:
                    for r in regex:
                        if r.decode('utf-8') in s:
                            new_samples.append(s)
                            break
        if type == "file":#读取文件中的样本列表做为要操作的文件
            new_samples = [line.strip("\n").decode("utf-8") for line in open(regex)]

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

    def doc_segmentation(self):
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

    def section_segmentation(self):
        """
        从mongodb中获取的section层次获取分词结果，返回每个样本的分词列表
        Returns:
            dict k:section id, v:词的列表
        """
        s2s = {}
        coll = self.collection.find({"level":"section"})
        for c in coll:
            sample = "/"+(c["_id"]["path"]+c["_id"]["name"]).strip("/")+"/"
            kws = ""
            kwlist = []
            if c.has_key("splitwords"):
                kws = c["splitwords"]
            for kw in kws.split():
                kw = kw.strip()
                kwlist.append(kw.split("/")[0])
            sample_words[sample] = kwlist

        return sample_words

    def get_sec2doc(self):
        """
        从mongodb中获取section对应的文档id
        Returns:
            dict k:section id, v:文档id
        """
        sec_doc = {}
        coll = self.collection.find({"level":"section"})
        for c in coll:
            sample = c["_id"]["path"]+c["_id"]["name"]
            doc = c["_id"]["path"]
            sec_doc[sample] = doc
        return sec_doc

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
            sample = "/"+(c["_id"]["path"]+c["_id"]["name"]).strip("/")+"/"
            kws = ""
            if c.has_key("keyword"):
                kws = c["keyword"]
            s2k[sample] = kws.split()
        return s2k

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
            s2s: dict k: document id, v:section label
        """
        s2s = {}
        coll = self.collection.find({"level":"section"})
        for c in coll:
            sample = c["_id"]["path"]
            if not s2s.has_key(sample):
                s2s[sample] = set()
            label = c["label"].strip()
            if label and len(label) > 1:
                s2s[sample].add(label)
        for s, s in s2s.items():
            s2s[sample] = list(s)
        for sample in diff_items(self.all_samples,s2s.keys()):
            s2s[sample] = []
        return s2s 

    def get_section_label(self, f):
        """
        从数据库获取某文档的section label
        Return:
            labels: list of section labels
        """
        labels = []
        sections = self.collection.find({"level":"section","_id.path":f })
        for s in sections:
            if s["label"]:
                l = s["label"].strip()
                if len(l) > 0:
                    labels.append(l)
        return labels

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
            label = c["label"].strip()
            if label and len(label) > 1:
                s2sub[sample].add(label)
        for s, sub in s2sub.items():
            s2sub[sample] = list(sub)
        for sample in diff_items(self.all_samples,s2sub.keys()):
            s2sub[sample] = []
        return s2sub 

    def get_section2block(self):
        """
        从数据库获取block label
        Return:
            s2b: dict k:section, v:block label
        """
        coll = self.collection.find({"level":"block"})
        s2b = {}
        for c in coll:
            sample = c["_id"]["path"]
            if not s2b.has_key(sample):
                s2b[sample] = set() 
            label = c["label"].strip()
            if label and len(label) > 1:
                s2b[sample].add(label)
        for s, b in s2b.items():
            s2b[sample] = list(b)
        for sample in diff_items(self.all_samples,s2b.keys()):
            s2b[sample] = []
        return s2b 

    def get_section2sectionlabel(self):
        """
        从数据库获取 section 与其对应的section label
        Return:
            s2l: dict k:section, v:section label
        """
        coll = self.collection.find({"level":"section"})
        s2l = {}
        for c in coll:
            sample = "/"+(c["_id"]["path"]+c["_id"]["name"]).strip("/")+"/"
            s2l[sample] = [c["label"]]
        return s2l 

    def get_section2header(self):
        """
        从数据库获取 section 与其对应的table header(如果有table)
        table 在paragraph级别中, 通过type:"Tab"识别出来
        Return:
            s2l: dict k:section id, v:table header
        """
        coll = self.collection.find({"level":"paragraph","tableSerial":{"$gt":-1}})
        s2h = {}
        for c in coll:
            sample = c["_id"]["path"].rsplit('/',2)[0]+'/'
            o_labels = c["rowtableLabel"] #提取header
            labels = []
            for l in o_labels:
                for ll in l.split(":"):
                    labels += ll.split("#")

            if labels:
                s2h[sample] = s2h.get(sample,[])+labels

        for sample in diff_items(self.all_samples,s2h.keys()):
            s2h[sample] = []
        return s2h 

    def get_table2header(self):
        """
        从数据库获取 table 与其对应的table header
        table 在paragraph级别中, 通过type:"Tab"识别出来
        Return:
            t2h: dict k:paragraph id, v:table header
        """
        coll = self.collection.find({"level":"paragraph","tableSerial":{"$gt":-1}})
        t2h = {}
        for c in coll:
            sample = "/"+os.path.join(c["_id"]["path"].rsplit("/",3)[0],"table:"+str(c["tableSerial"])).strip("/")+"/"
            o_labels = c["rowtableLabel"] #提取header
            labels = []
            for l in o_labels:
                for ll in l.split(":"):
                    labels += ll.split("#")

            if labels:
                t2h[sample] = labels
        return t2h 

    def get_table2section(self):
        """
        Table 和它所在的section的section label(如果有)
        Return:
            s2l: dict k:paragraph id, v:section label
        """
        coll = self.collection.find({"level":"paragraph","tableSerial":{"$gt":-1}})
        coll2 = self.collection.find({"level":"section"})
        s_label = dict((c["_id"]["path"]+c["_id"]["name"], c['label']) for c in coll2)
        t2s = {}
        for c in coll:
            sample = "/"+os.path.join(c["_id"]["path"].rsplit("/",3)[0],"table:"+str(c["tableSerial"])).strip("/")+"/"
            s_id, b_id, _ = c["_id"]["path"].rsplit("/",2)
            t2s[sample] = [s_label[s_id]] if len(s_label[s_id].strip()) > 0 else []
        return t2s 

    def get_table2block(self):
        """
        Table 和它所在的block的block label(如果有)
        Return:
            s2l: dict k:paragraph id, v:block label
        """
        coll = self.collection.find({"level":"paragraph","tableSerial":{"$gt":-1}})
        coll2 = self.collection.find({"level":"block"})
        b_label = dict((c["_id"]["path"]+c["_id"]["name"], c['label']) for c in coll2)
        t2b = {}
        for c in coll:
            sample = "/"+os.path.join(c["_id"]["path"].rsplit("/",3)[0],"table:"+str(c["tableSerial"])).strip("/")+"/"
            b_id = c["_id"]["path"].rstrip("/")
            t2b[sample] = [b_label[b_id]] if len(b_label[b_id].strip()) > 0 else []
        return t2b 

    def is_bad_label(self, label):
        """
        The label which has character that makes weka disable
        """
        ch = ['"',',',"'",'%']
        for c in ch:
            if c in label:
                print "Bad label:",label
                return True
        return False

    def is_word(self, f):
        """
        If the document is word doc
        """
        coll = self.collection.find({"level":"document"})
        f = f.strip("/")

        for c in coll:
            sample = (c["_id"]["path"]+c["_id"]["name"]).strip("/")
            if sample == f:
                if c.has_key("type") and c["type"] == "Doc":
                    return True
                else:
                    return False
        print f.encode("utf-8"),"is not found in mongo"

    def get_word_doc(self):
        """
        Get a list of all the word document
        """
        coll = self.collection.find({"level":"document","type":"Doc"})
        return [(c["_id"]["path"]+c["_id"]["name"]).rstrip("/")+"/" for c in coll]


    #################  for attrbute file  ###############
    def has_heading2(self, sections):
        """
        Has end 
        """
        for s in sections:
            html = s["html"]
            soup = BeautifulSoup(html, features="xml")
            if soup.find(class_ = "heading2"):
                return True
        return False

    def has_header(self, sections):
        """
        Has header
        """
        for s in sections:
            html = s["html"]
            soup = BeautifulSoup(html, features="xml")
            if soup.find(class_ = "title"):
                return True
        return False

    def no_meaning(self, f):
        """
        If the attribute file has no context
        """
        sections = self.collection.find({"level":"section","_id.path":f })
        return False if sections.count() > 0 else True

    def has_img(self, f):
        """
        If the attribute file has image
        """
        sections = self.collection.find({"level":"section","_id.path":f })
        for s in sections:
            html = s["html"]
            soup = BeautifulSoup(html)
            if soup.find("img"):
                return True
        return False

    def has_one_img(self, f):
        """
        If the attribute file has only one img element
        """
        sections = self.collection.find({"level":"section","_id.path":f })
        #if sections.count() == 3:
        #    if not self.has_heading2(sections.clone()):
        #        return False

        #if sections.count() > 1:
        #    if not self.has_header(sections.clone()):
        #        return False

        if sections.count() > 3:
            return False

        for s in sections:
            html = s["html"]
            soup = BeautifulSoup(html)
            if soup.find("img"):
                for p in soup.findAll("p"):
                    if not p.find("img"):
                        return False
                if len(soup.findAll("img")) == 1:
                    return True
        return False

    def has_table(self,f):
        """
        If the attribute file has table element
        """
        sections = self.collection.find({"level":"section","_id.path":f })
        for s in sections:
            html = s["html"]
            soup = BeautifulSoup(html)
            if soup.find("table"):
                return True
        return False

    def has_one_big_table(self,f):
        """
        If the attribute file has only one table element
        1. One section except header and end head
        2. A table at the beginning
        3. No paragraph
        """
        sections = self.collection.find({"level":"section","_id.path":f })
        #if sections.count() == 3:
        #    if not self.has_heading2(sections.clone()):
        #        return False

        if sections.count() > 3:
            return False

        for s in sections:
            html = s["html"]
            soup = BeautifulSoup(html)
            if soup.find("table"):
                if soup.tr.td.find("p", recursive = False):
                    return False
                if len(soup.findAll("table")) == 1:
                    try:
                        if soup.find("div").find("p",recursive=False):
                            return False
                        if soup.find("div").findChildren()[0].name == "table":
                            return True
                    except:
                        continue

        return False

    def pure_text(self,f):
        """
        1. Only one content section between heading and end head
        2. No block label in the content section
        3. No table
        4. No image
        """
        sections = self.collection.find({"level":"section","_id.path":f })
        sec_copy = sections.clone()

        if sections.count() == 3:
            if not self.has_heading2(sections.clone()):
                return False

        if sections.count() > 1:
            if not self.has_header(sections.clone()):
                return False

            for s in sections:
                html = s["html"]
                soup = BeautifulSoup(html, features="xml")
                if soup.find("table"):
                    return False
                if soup.find("img"):
                    return False
                #ps = soup.findAll("p")
                #if p and len(p) == 1:
                #    if not p.find("table")
                #        return True

        for s in sec_copy:
            for block in s["children"]:
                block_id = block.rsplit("/",1)[-1]
                b = self.collection.find({"level":"block","_id.name":block_id })[0]
                if b["label"] and len(b["label"]) > 0:
                    return False
        return True

    def is_hub(self, f):
        f = f.strip("/")
        path,name = f.rsplit("/",1)
        doc = self.collection.find({"level":"document","_id.path":path,"_id.name":name})[0]

    def has_block_label(self,f):
        """
        
        """
        sections = self.collection.find({"level":"section","_id.path":f })
        for s in sections:
            for block in s["children"]:
                block_id = block.rsplit("/",1)[-1]
                b = self.collection.find({"level":"block","_id.name":block_id })[0]
                if b["label"] and len(b["label"]) > 0:
                    return True
        return False

    def has_section_label(self, f):
        """
        If the section has a label
        """
        sections = self.collection.find({"level":"section","_id.path":f })
        for s in sections:
            if s["label"]:
                if len(s["label"].strip()) > 0:
                    return True
        return False

    def check_level(self, sample):
        """
        Check which level the sample belong to
        """
        if "table:" in sample:
            return "paragraph"
        elif "s:" in sample:
            return "section"
        else:
            return "document"

    def generate_query(self, sample):
        """
        Check which classify it is according to sample id. 
        Level:document,section,table
        Generate specific query string
        """
        sample = sample.strip("/")
        if "table:" in sample:
            path, t = sample.rsplit("/",1)
            path = '/'+path+'/'
            t = int(t.split(":")[-1])
            return {"level":"paragraph", "_id.path":{"$regex":path},"tableSerial":t}

        elif "s:" in sample:
            path, s = sample.rsplit("/",1)
            path = '/'+path+'/'
            return {"level":"section", "_id.path":path,"_id.name":s}
        else:
            path, d = sample.rsplit("/",1)
            path = '/'+path+'/'
            return {"level":"document", "_id.path":path,"_id.name":d}

    def insert_flag(self, s_f):
        """
        Insert annotation result into mongodb
        Field 'flag' in level document
        """

        for k,v in s_f.items():
            query = self.generate_query(k)
            doc = self.collection.find(query)
            self.collection.update(query, {"$set":{"flag":v}})

    def insert_class(self, s_c):
        """
        Insert classify result into mongodb
        Field 'abstype' in level document
        """
        for k,v in s_c.items():
            query =self.generate_query(k)
            self.collection.update(query, {"$set":{"abstype":v}})

    def get_flag(self, s):
        """
        Get annotation flag according to sample id
        """
        path, name = s.strip("/").rsplit("/",1)
        sample = self.collection.find({"_id.path":"/"+path+"/", "_id.name":name })
        for a in sample:
            if a.has_key('flag') and a['flag'] and len(a['flag']) > 0:
                return a['flag']
            else:
                return ""

    def get_samples_from_flag(self, flag):
        """
        Get sample id list according to given flag
        """
        samples = self.collection.find({"flag": flag})
        return ['/'+os.path.join(s['_id']['path'], s['_id']['name']).strip('/')+'/' for s in samples]
        
    def get_all_flag_samples(self, level=None):
        """
        Get all flaged sample id list 
        Returns:
            s_f: dict. key:sampleid, value:flag

        """
        if level:
            samples = self.collection.find({"level":level, "flag": {"$exists":1}})
        else:
            samples = self.collection.find({"flag": {"$exists":1}})

        s_f = {}
        for s in samples:
            if len(s['flag']) < 1:
                continue
            if s['level'] == 'document':
                sample = '/'+os.path.join(s['_id']['path'], s['_id']['name']).strip('/')+'/'
            elif s['level'] == 'section':
                sample = c["_id"]["path"].rsplit('/',2)[0]+'/'
            elif s['level'] == 'paragraph':
                sample = "/"+os.path.join(c["_id"]["path"].rsplit("/",3)[0],"table:"+str(c["tableSerial"])).strip("/")+"/"
            s_f[sample] = s['flag']

        return s_f

    #################  For validation  ##############################

    def section_validation(self):
        """
        从数据库读取的label是否正确，通过验证循环读取的label集合的数量与用api 中的count函数的统计结果进行对比
        """
        import random
        s2s = self.get_sample2section()
        s2s = s2s.items()
        random.shuffle(s2s)
        for k,v in s2s[0:max(10,int(0.01*len(s2s)))]:
            c1 = self.collection.find({"level":"section", "_id.path":k, "label":{"$ne":""}}).count() #通过api获得的section label数量
            c2 = len(v) #通过函数计算出的section label数量
            print k.encode("utf-8"),c1,c2
            try:
                assert c1 == c2
            except:
                print "WARNING"
                for c in self.collection.find({"level":"section", "_id.path":k, "label":{"$ne":""}}):
                    print c["label"].encode("utf-8")
                print "*********************"
                for l in v:
                    print l.encode("utf-8")

    def block_validation(self):
        """
        从数据库读取的label是否正确，通过验证循环读取的label集合的数量与用api 中的count函数的统计结果进行对比
        """
        import random
        s2b = self.get_sample2subsection()
        s2b = s2b.items()
        random.shuffle(s2b)
        for k,v in s2b[0:max(10,int(0.01*len(s2b)))]:
            c1 = 0
            for c in self.collection.find({"level":"section", "_id.path":k},{"_id":1}):
                s = c["_id"]["path"]+c["_id"]["name"]+"/"
                c1 += self.collection.find({"level":"block", "_id.path":s, "label":{"$ne":""}}).count()#通过api获得的section label数量
            print k.encode("utf-8"),c1,len(v)
            try:
                assert c1 == len(v)
            except:
                print "WARNING"
                for c in self.collection.find({"level":"section", "_id.path":k},{"_id":1}):
                    s = c["_id"]["path"]+c["_id"]["name"]+"/"
                    for c in self.collection.find({"level":"block", "_id.path":s, "label":{"$ne":""}}):
                        print c["label"].encode("utf-8")
                print "*********************"
                for l in v:
                    print l.encode("utf-8")


if __name__ == "__main__":
    db = DB()
    all_ = db.all_samples
    s2s = db.get_sample2section()
    s2s = dict((k,":::".join(v)) for k,v in s2s.items())
    print len(s2s)
    s2b = db.get_sample2subsection()
    s2b = dict((k,":::".join(v)) for k,v in s2b.items())
    print len(s2b)
    s2k = db.get_sample2keywords()
    s2k = dict((k,":::".join(v)) for k,v in s2k.items())
    print len(s2k)

    from csvio import *
    csv = CSVIO("labels.csv",append=False)
    csv.column("sample",dict((s,s) for s in all_))
    csv.column("section label",s2s)
    csv.column("block label",s2b)
    csv.column("keyword",s2k)
    csv.write("labels.csv",separator="\t",header = True)

