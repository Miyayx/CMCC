#/usr/bin/python
#-*-coding:utf-8-*-

def cluster_feature(cluster_file, feature_file, result_file, cluster_num):
    _ids = [line.split(",")[0] for line in open(cluster_file) if int(line.strip("\n").split(",")[-1]) == cluster_num]
    title_feature = {}
    with open(feature_file) as f:
        with open(result_file,"w") as fout:
            fout.write(str(len(_ids))+"\n")
            head = f.readline().strip("\n").split(",")
            line = f.readline()
            while line:
                title = line.split(",",1)[0]
                if title in _ids:
                    fout.write("\n"+title+"\n")
                    items = line.strip("\n").split(",")
                    for i in range(len(items)):
                        if items[i] == "1":
                            fout.write(head[i]+"\n")
                line = f.readline()


def no_feature_file(feature_file):
    count = 0
    with open(feature_file) as f:
        head = f.readline().strip("\n").split(",")
        line = f.readline()
        while line:
            items = line.strip("\n").split(",")
            if items.count("1") == 0:
                count+=1
            line = f.readline()
    print "No Feature File Num:",count


if __name__=="__main__":

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-k", "--k", dest="k", type="int", help="Num of KMeans Cluster")
    parser.add_option("-s", "--seed", dest="seed", type="int", help="Seed of KMeans Cluster")
    parser.add_option("-e", "--eps", dest="eps", type = "float", help="Eps of DBSCAN Cluster")
    parser.add_option("-m", "--minp", dest="minp", type="int",help="Minp of DBSCAN Cluster")

    (options, args) = parser.parse_args()

    import sys,os
    if not options.k:
        print "Error:k is required"
    else:
        print options
        path = "cluster_result/"
        for kk,vv in options.__dict__.items():
            path += "%s=%s "%(kk,str(vv))
        path += "/"
        try:
            os.mkdir(path)
        except:
            pass

        for i in range(-1,options.k):
            cluster_feature("../../data/Classify/cluster1_f1_result.csv","../../data/Classify/result_features1.csv",path+"cluster"+str(i)+".dat",i)
    #no_feature_file("../../data/Classify/result_features1.csv")

        
