#!/usr/bin/python
#encoding=utf-8

"""
人工标注辅助程序，用于最后的人工标注
1. 对剩下的sample进行大k值的聚类
2. 在clusterY_f1_result.csv(Y为迭代次数)中添加一列进行标注(参考聚类结果，可标多类，把能标出来的尽可能标出来,不用标负例)
3. 运行python add_annotation.py Y
   1) 在result_features1里找到上一个迭代的classify result, 找出里面的others, 生成标注字典，value为others
   2) 程序自动找到clusterY_f1_result.csv
   3) 读取最后一列标注结果,更新标注字典
   4) 写入到result_features1的flagY列与classY列
"""
from csvio import *
from global_config import *
from utils import *

if __name__=="__main__":
    import sys

    props = read_properties(os.path.join(BASEDIR, PROP_FILE))#总配置
    props.update(read_properties(os.path.join(BASEDIR, NAME_FILE)))#文件名配置
    props.update(read_properties(os.path.join(BASEDIR, PATH_FILE)))#路径配置

    #命令行参数第一个要求必须是本次迭代次数，通过是否是数字来判断参数是否输入正确
    if len(sys.argv) < 2:
        print "Need Iteration Num for Argument"
        exit()
    else:
        if sys.argv[1].isdigit() or sys.argv[1]=='-iter':
            if sys.argv[1].isdigit():
                sys.argv.insert(1, '-iter')
            props.update(parse_argv(sys.argv))
        else:
            print "Need Iteration Num for Argument"
            exit()
         
    iter_n = str(props['iter'])

    data_file = os.path.join(RESULT_PATH, props["result"].replace('Y',str(props["featureid"]))) #大表
    print data_file

    cluster_result = os.path.join(RESULT_PATH, props["cluster_result"].replace('Y',str(props["featureid"])).replace('X',str(iter_n)))
    print cluster_result

    data = CSVIO(data_file, separator=",")

    class_res = data.read_one_to_one(0,data.fields.index("class"+str(int(iter_n)-1)))# 读取上一迭代的分类结果
    class_res = dict((k ,v) for k,v in class_res.items() if v == "others") #只保留others样本
    print "Total others:",len(class_res)

    cluster_csv = CSVIO(cluster_result)
    a_result = cluster_csv.read_one_to_one(0, cluster_csv.fields.index("flag"+str(iter_n)))
    a_result = dict((k ,v) for k,v in a_result.items() if len(v) > 0 ) #只保留有标注的样本
    print "Annotation Num:",len(a_result)
    class_res.update(a_result) #用标注结果更新标注字典，则已标注的更新成标注结果，未标注的还是others

    #标注结果写入大表，同时写入flag和class两个列
    data.column("flag"+str(iter_n), class_res)
    data.column("class"+str(iter_n), class_res)
    data.write(data_file)
