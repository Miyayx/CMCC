#!/usr/bin/python2.7
#encoding=utf-8

from annotation import auto_annotaion

def run():
    pass

if __name__=="__main__":
    import sys
    if len(sys.argv) < 2:
        print "Need Iteration Num for Argument"
         
    iter_n = sys.argv[1]
    import time
    start = time.time()

    props = read_properties(PROP_FILE)
    props.update(read_properties(NAME_FILE))
    props["file_path"] = "../"+props["file_path"].strip("/")+"/"

    data_file = props["file_path"]+props["result"].replace('Y',props["featureid"])

################ Cluster #############
    cluster_result = props["file_path"]+props["cluster_result"].replace('Y',props["featureid"]).replace('X',iter_n)
    km = KMEANS(data_file)
    km.run(cluster_result,iter_n)

    print "Time Consuming:",(time.time()-start)

    auto_annotaion("annotation.cfg", data_file, iter_n )



