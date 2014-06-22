#/usr/bin/python
#-*-coding:utf-8-*-

def cluster_feature(cluster_file, feature_file, cluster_num):
    _ids = [line.split(",")[0] for line in open(cluster_file)]
    title_feature = {}
    with open(feature_file) as f:
        head = f.readline().strip("\n").split(",")
        line = f.readline()
        while line:
            title = line.split(",",1)[0]
            if title in _ids:
                print ""
                print title
                items = line.strip("\n").split(",")
                for i in range(len(items)):
                    if items[i] == "1":
                        print head[i]
            line = f.readline()


if __name__=="__main__":
    cluster_feature("../../data/Classify/cluster1_f1_result.csv","../../data/Classify/result_features1.csv",2)

        
