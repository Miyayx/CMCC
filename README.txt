﻿**************  特征提取 *************
代码在module/classify里
需要安装第三方类库:
	pymongo（数据库）
	gensim（自然语言处理相关，计算tfidf时用）
	
输入:  
	mongodb
	部分文件中读取，文件在data/*中
输出:
	result_featureY.csv(Y为feature id),此为迭代器的最终输出文件。目前在data/Classify/中
配置文件:
	conf/conf.properties    //公共文件，项目绝对路径,数据库相关
    conf/classify/path.properties         //结果文件输出路径,聚类分类结果输出路径与log输出路径两种
	conf/classify/filename.properties     //各种输入输出文件名的命名规范
	conf/classify/feature.cfg             //feature选择相关
	conf/classify/file.cfg                //输入输出文件相关
	
命令: python classify_preprocess.py (需要在classify路径下运行)

conf/classify/feature.cfg说明：
feature的选择在conf/classify/feature.cfg里设定,另外，此文件中的所有配置都可在命令行中进行配置，格式：
python classify_preprocess.py --hub 0 --attribute 1 --no_feature 1 ...
python classify_preprocess.py -H 0 -a 1 -n 1 ...
具体参数配置输入 python classify_preprocess.py -h 查看

    hub                   #输出是删除hub文件   0 保留hub， 1 删除hub
    attribute             #输出是否删除attribute文件   0 保留attribute， 1 删除attribute
    no_feature            #是否输出没有label的文档名称
    section_label         #特征是否包含section label, 0不包含， 1 包含
    block_label           #特征是否包含block label
    label_common          #是否删除只出现一次的section label，1 删除
    synonym_merge         #有同义词出现时，合并同义词，用一个词代替其他所有词
    sample_filter_dir     #名称具有此子字符串的文档保留,多个字符串以逗号分隔
    sample_filter_file    #只对此文件中列出的文档列表进行操作

conf/classify/file.cfg 输入输出文件说明：
输入文件：
    synonym_dict=data/spm/classifyingResult.csv        相似属性合并结果
    inlink=data/docparse/inlink.txt        内链关系信息
    outlink=data/docparse/outlink.txt      链接关系信息
    
输出文件路径：
    others_output_path         其他输出文档存放路径

输出文件:
    delete_output             因特殊字符等原因删除的文件列表
    hub_output                hub文档id列表（现在hub文档进入迭代器进行分类，此文件为空）
    attribute_output          attribute文档id列表
    no_feature_output         没有label的，未进入迭代的文档列表
    result_output             最终结果文档命名
    left_section_file         删除的只出现的一次的section label与其对应文档的记录
    left_block_file           删除的只出现的一次的block label与其对应文档的记录
    file_statistics           程序总体的统计记录,如进入迭代的文档数量，属性文档数量等,在log文件夹里
	file_col                  最终结果大表列的信息（比如有多少feature列，哪一列是分类结果集合）
  
**************  数据库读取验证 *************
代码在module/classify里
python db_validation.py > outputfile

**************  特征验证 *************
代码在module/classify里
python feature_validation.py > outputfile

**************  属性文档验证 *************
代码在module/classify里
python attribute.py > outputfile

************** 特征提取+相关验证 **********
sh start.sh
默认验证输出 指定结果文件夹下的val子文件夹

*********************************  聚类分类迭代 *********************************
*********************************************************************************

聚类分类部分使用的python的机器学习库scikit-learn

在CentOS上的安装：
安装pip
sudo yum install python-devel
sudo yum install gcc gcc-gfortran gcc-c++ make automake kernel-devel
sudo yum install lapack lapack-devel blas blas-devel
sudo pip install numpy scipy scikit-learn

conf/classify/path.properties:
    output_path                //结果输出文件夹
    log_path                   //log结果输出文件夹

conf/classify/classify.properties里
参数说明：
    featureid=1                //特征文件id
    flag_ratio = 0.3           //标注比例
    min_cluster_num=3          //自动计算时的最小簇数
    max_cluster_num=15         //自动计算时的最大簇数
    lowest_accuracy=0.85       //测试低于此准确率自动停止
    stop_ratio = 0.1           //迭代停止时剩余样本与总样本的比例

***************  迭代部分 *********************
程序的每次迭代分为三步:

第一步:聚类
	需要运行的是cluster.py，
    在linux中运行命令：
    python cluster.py -i X 
    python cluster.py -i X -k 4 
    python cluster.py -i X -init density 
    python cluster.py -i X -k 4 -init density
    X:    第X次迭代
    k:    指定聚类簇数
    init: 指定计算初始聚类中心的方法，默认k-means++,另外还有:
        even: 每隔N/k选取一个点
        spss: 算法来自Single Pass Seed Selection Algorithm for k-Means, 号称kmeans++改进版，可获得确定的中心点
        density: 算法来自Clustering by fast search and find of density peaks,根据点周围的密度来确定，运行较快
        nbc :    算法来自Neighborhood Density Method for Selecting Initial Cluster Centers in K-Means Clustering, 根据点的邻居个数确定，运行较慢

    其他参数配置输入 python cluster.py -h 查看

	这步的输出文件为clusterX_fY_result.csv,(X是迭代次数，Y是feature文件id)，此结果文件第一列是文档名称，第二列是簇号。

第二步：人工标注
	人工标注的时候需要在所有cluster里面选择一个聚类效果最好的cluster,抽象成概念，进行标注。标注的正例应为正例簇的样本数量的30%，标注的负例应为其他簇的样本总数的30%。应保证每个簇都有样本标注，标注数量与次簇数量成正比
    标注在resultX_featureY.csv中进行。在flagX列中进行。如果是正例则填写正确分类名称，如果是负例则填写“others”，既不标成正也不标成负分类的留空。
    人工标注有辅助程序 flag.py
    配置文件在conf/classify/flag.cfg中，
        cluster 正簇的簇号,可以是多个，以逗号隔开
        pos_class 正例类别名称
        neg_class 负例类别名称
    程序将所有正簇中的所有样本作为正例，自动统计数量，选择30%标注成正例，其他簇选择总数的30%随机标记成负例。每个簇的标记数量与簇内样本数量成正比，并保证每个簇至少有一个样本被标记
    运行python flag.py -i X 或 python flag.py -i X -m auto   X是迭代次数,m是标注方法
    method: auto,按照上述思想自动标注
            db  ,正例从数据库中已记录的人工标注信息中获取（flag字段）

    其他参数配置输入 python flag.py -h 查看


第三步：根据人工标注结果训练分类器分类
	需要运行的是classify.py，在linux中可以直接运行python classify.py -i X（第X次迭代）运行程序。
    其他参数配置输入 python classify.py -h 查看

    分类的输出包括部分，第一部分是中间结果记录文件：
    classifyX_fY_train.csv 记录训练数据集
    classifyX_fY_test.csv  记录测试数据集

	第二部分是对分类得到的结果
    classifyX_fY_test_result.csv 记录测试结果，第一列是文档名称，第二列是标注类别，第三列是分类器计算出的类别
    classifyX_fY_test_statistic.txt 记录测试结果，包括准确率，分类结果统计
    classifyX_fY_predict.csv     记录对为标注的文档的分类结果
    result_featureY.csv          大表结果，本次迭代分类结果汇总在classY一列

    分类要求准确率到达85%，若某次分类准确率过低，则分类停止


当剩下的文档类别过多，对应类别的数量过少时，不再进行迭代。

***********************  输出文件命名 ***********************
输入文件：
    result_featuresY.csv(Y为特征id) 
    注：feature文件的命名在conf/classify/feature.cfg中，每个section的命名，即[]中的内容，即为此feature文件的命名
结果文件：
    X：第X次迭代；  Y：特征id
	result_featuresY.csv           分类结果文件，最终结果文件
	attribute_files.dat            属性文档列表
	no_feature_files.dat           没有label的文档列表 
    delete_files.dat               其他未进入迭代器的文档列表
	
中间文件：
	clusterX_fY_result.csv                聚类结果输出文档
	classifyX_fY_train.csv                分类时的训练数据
	classifyX_fY_test.csv                 分类时的测试数据
	classifyX_fY_predict.csv              需要被分类的数据（本次迭代数据减去train和test）
    classifyX_fY_test_result.csv          记录测试结果，第一列是文档名称，第二列是标注类别，第三列是分类器计算出的类别
    classifyX_fY_test_statistic.txt       记录测试结果，包括准确率，分类结果统计
    classify_fY_log.csv                   记录所有迭代的文档数量统计

以上输出文档都在指定的conf/classify/path.properties中

*********** 人工标注 *************
迭代停止后，需要人工对迭代停止后剩余的文件进行标注，标注结果在大表最后两列，列名flagX, classX, X为迭代号

*********** 结果汇总 *************
所有迭代跑完以及人工标注后，将所有分类结果汇总到第二列
最后将所有标注数据（包括最后一次）和分类结果进行整合
    导入flag结果：python import_flag.py (可指定要导入的数据库collection，运行python import_flag.py -h查看参数)
        同时输出结果汇总文件 flag_record.csv 在指定路径下
    导入class结果：python gathor.py (可指定要导入的数据库collection，运行python gathor.py -h查看参数)
        同时进行汇总结果在第二列与导入数据库两个操作
	

########################################  Section 聚类分类  ######################################

**************  特征提取 *************
代码在modules/classify里
	
输入:  
	mongodb
	部分文件中读取，文件在data/*中
输出:
	result_featureY.csv(Y为feature id),此为迭代器的最终输出文件。目前在data/SectionClassify/中
配置文件:
	conf/conf.properties                  //公共文件，数据库相关
    conf/classify/path.properties         //所有结果文件输出路径，默认data/SectionClassify/,各种输入输出操作都与此路径有关
	conf/classify/filename.properties     //各种输入输出文件名的命名规范
 ** conf/classify/sec_feature.cfg         //feature选择相关
	conf/classify/file.cfg                //输入输出文件相关
	
命令: python section_preprocess.py(需要在classify路径下运行)

conf/classify/sec_feature.cfg说明：
feature的选择在conf/classify/sec_feature.cfg里设定,此文件中的所有配置都可在命令行中进行配置，格式：
    python section_preprocess.py --block_label 1 --table_header 1 --no_feature 1 ...
    python section_preprocess.py -b 1 -t 1 -n 1 ...
具体参数配置输入 python section_preprocess.py -h 查看

    no_feature            #是否输出没有label的文档名称
    block_label           #特征是否包含block label
    table_header
    label_common          #是否删除只出现一次的section label，1 删除
    sample_filter_dir     #名称具有此子字符串的文档保留,多个字符串以逗号分隔
    sample_filter_file    #只对此文件中列出的文档列表进行操作

输出文件：
    同文档级别

*************  聚类分类迭代 ************

聚类分类部分使用的python的机器学习库scikit-learn

conf/classify/path.properties
    output_path = ./data/SectionClassify(默认)
    log_path    = ./log/SectionClassify(默认)

conf/classify/classify.properties里
    同文档级别

***************  迭代部分 *********************
与文档分类相同

**************  人工标注与结果汇总  **************
与文档分类相同

注：主要是改conf/classify/sec_feature.cfg, conf/classify/classify.properties, conf/classify/path.properties里的路径


########################################  Table 聚类分类  ######################################

**************  特征提取 *************
代码在modules/classify里
	
输入:  
	mongodb
	部分文件中读取，文件在data/*中
输出:
	result_featureY.csv(Y为feature id),此为迭代器的最终输出文件。默认在data/TableClassify/中
配置文件:
	conf/conf.properties                  //公共文件，数据库相关
    conf/classify/path.properties         //所有结果文件输出路径，默认data/TableClassify/,各种输入输出操作都与此路径有关
	conf/classify/filename.properties     //各种输入输出文件名的命名规范
 ** conf/classify/table_feature.cfg       //feature选择相关
	conf/classify/file.cfg                //输入输出文件相关
	
命令: python table_preprocess.py(需要在classify路径下运行)

conf/classify/table_feature.cfg说明：
feature的选择在conf/classify/table_feature.cfg里设定,此文件中的所有配置都可在命令行中进行配置，格式：
    python table_preprocess.py --block_label 1 --table_header 1 --no_feature 1 ...
    python table_preprocess.py -b 1 -t 1 -n 1 ...
具体参数配置输入 python table_preprocess.py -h 查看

    no_feature            #是否输出没有label的文档名称
    section_label         #特征是否包含section label
    block_label           #特征是否包含block label
    table_header          #特征是否包含table header
    label_common          #是否删除只出现一次的label，1 删除
    sample_filter_dir     #名称具有此子字符串的文档保留,多个字符串以逗号分隔
    sample_filter_file    #只对此文件中列出的文档列表进行操作

输出文件：
    同文档级别

*************  聚类分类迭代 ************

聚类分类部分使用的python的机器学习库scikit-learn

conf/classify/path.properties
    output_path = ./data/TableClassify(默认)
    log_path    = ./log/TableClassify(默认)

conf/classify/classify.properties里
    同文档级别

***************  迭代部分 *********************
与文档分类相同

**************  人工标注与结果汇总  **************
与文档分类相同

注：主要是改conf/classify/table_feature.cfg, conf/classify/classify.properties, conf/classify/path.properties里的路径


########################################  其他：人工标注辅助工具  ######################################

因后期样本个数少，类别多，导致一些有明显特征的样本因为训练数量少而不能进行进一步的分类，因此迭代会停止。
但聚类结果有助于人工标注，因此可以进行迭代的聚类与人工标注来尽可能减少人力

具体步骤：
    人工标注辅助程序，用于最后的人工标注
    1. 对剩下的sample进行大k值的聚类
       python cluster.py -i X -k 100 X为迭代次数，在原迭代次数的基础上继续叠加
    2. 在clusterX_f1_result.csv(X为迭代次数)中添加一列flagX进行标注(参考聚类结果，可标多类，把能标出来的尽可能标出来,不用标负例)
    3. 运行python add_flag.py -i X
       程序说明：
       1) 在result_features1里找到上一个迭代的classify result, 找出里面的others, 生成标注字典，value为others
       2) 程序自动找到clusterY_f1_result.csv
       3) 读取最后一列标注结果,更新标注字典
       4) 写入到result_features1的flagX列与classX列
