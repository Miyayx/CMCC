#/usr/bin/env/python2.7
#encoding=utf-8

from validation import *
from synonym import *

class FeatureValidation(Validation):

    def exist_val(self, data, origin, fn = None):
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
        syns = []
        synd = os.path.join(BASEDIR, self.props['synonym_dict'])
        if os.path.isfile(synd):
            syns = get_synonym_words()
    
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
                print "WARNING: Label count and db count: length not equal"
            print "++++++++  feature  +++++++++++++"
            for i in mine_index:
                if (not fields[i] in ls) and (fields[i] in syns):
                    print "    "+fields[i].encode("utf-8")+"(同)"
                else:
                    print "    "+fields[i].encode("utf-8")
            print "++++++++  origin  +++++++++++++"
            for l in sorted(ls):
                #if (l not in fields) and (l in syns):
                #    print "    "+l.encode("utf-8")+"(同)"
                print "    "+l.encode("utf-8")
            index_list.append(mine_index)
        return index_list
    
    
    def run(self, props, Y):

        self.props = props
    
        file_col = os.path.join(RESULT_PATH, props['file_col'])
        feature_file = os.path.join(RESULT_PATH, props['result_output']+'_'+'features'+str(Y)+'.csv')
        OTHERS_PATH = os.path.join(RESULT_PATH, props['others_output_path'])
    
        prop = read_properties(file_col) #get feature count from file_col file
    
        options = {
            "section":{
                "begin":2,
                "end":2+int(prop["section_count"]),
                "left_file":os.path.join(OTHERS_PATH, props['left_section_file']+'_features'+str(Y)+'.dat')
            },
            "block":{
                "begin":2+int(prop["section_count"]),
                "end":  2+int(prop["section_count"])+int(prop["block_count"]),
                "left_file":os.path.join(OTHERS_PATH, props['left_block_file']+'_features'+str(Y)+'.dat')
                }
        }
        self.validation(feature_file, options)

if __name__=="__main__":
    props = read_properties(os.path.join(BASEDIR, PATH_FILE))
    props.update(read_properties(os.path.join(BASEDIR, FILE_FILE)))
    import sys
    Y = 1
    if len(sys.argv) == 2:
        Y = sys.argv[1]
    v = FeatureValidation()
    v.run(props, Y)

