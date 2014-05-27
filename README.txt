**************  特征提取 *************
代码在classify_python里
需要安装第三方类库:
	pymongo（数据库）
	xlrd（读写xls）
	gensim（自然语言处理相关，计算tfidf时用）
	
输入:  
	mongodb
	部分文件中读取，文件在../data/中
输出:
	feature**.csv，目前在../data/feature/中
	result_featureYk.csv(Y为feature id),此为迭代器的最终输出文件。
		当有属性或hub文件被删除的时候，这部分文件被标为“属性”或“hub”类别，写入最终输出文件，最后由人工归类。
配置文件:
	../conf/conf.properties//公共文件，数据库相关
	file_col.properties    //最终结果大表列的信息（比如有多少feature列，哪一列是分类结果集合）
	filename.properties    //各种输入输出文件名的命名规范
	feature.cfg            //feature选择相关
	file.cfg               //输入输出文件相关
	
命令: python classify_preprocess.py(需要在classify_python路径下运行)

feature.cfg说明：
feature的选择在feature.cfg里设定
hub                   #输出是删除hub文件   0 保留hub， 1 删除hub
attribute             #输出是否删除attribute文件   0 保留attribute， 1 删除attribute
section_label         #特征是否包含section label, 0不包含， 1 包含
section_label_common  #是否删除只出现一次的section label，1 删除
synonym_merge         #有同义词出现时，合并同义词，用一个词代替其他所有词
synonym_expand        #对有同义词的词，所有同义词都标1
title_keyword         #特征是否包含自定义title关键字
title_tfidf           #特征是否包含 title tfidf特征
subsection_label      #特征是否包含subsection label:
document_tfidf        #特征是否包含文本tfidf值
split                 #是否将数据集切分成训练集与测试集

输入输出文件说明：
输入文件：
    ../etc/synonym_dict.csv               同义词表（以后用双婕的结果文件代替）
    ../../data/doc_parse/inlink.txt       内链关系信息
    ../../data/doc_parse/outlink.txt      链接关系信息
    ../etc/title_keywords.txt             title关键词（人为定义）
    ../etc/title_word_segmentation.txt    title分词结果（暂没用到）
    ../etc/document_segmentation.txt      全文本分词结果（暂没用到）
    
输出文件：
     ../../data/Classify/feature/featuresY.csv  (Y为特征id) 
     ../etc/samples1.txt                        进入迭代的文档id列表
     ../etc/not_sample.txt                      未进入迭代的文档id列表(一般是hub和attribute文档)
     ../etc/hub_files.txt                       hub文档id列表（现在hub文档进入迭代器进行分类，此文件为空）
     ../etc/attribute_files.txt                 attribute文档id列表
     ../data/Classify/ClassifyResult_fY.csv     最终结果文档，在预处理过程中，hub和attribute被做为hub或属性类别文档，写入此最终结果文档。统一在人工校验的时候进行处理
  
**************  特征验证 *************
代码在classify_python里

*************  聚类分类迭代 ************
程序的一部分外部参数在classify.properties里
参数说明：
file_path=../data/Classify             //文件输出路径
featureid=1                //特征文件id
samplefile=samples1.txt    //第一次迭代所需的样本文档
class_number = 1           //二分类（1），还是三分类（2）
neg_positive_ratio = 1     //负例数量与正例数量的比值（如果是人工标注，这个参数没用）
positive_all_ratio = 0.15  //正例与总数量的比值（如果是人工标注，这个参数没用）
max_cluster_num=4          //聚类个数，如果设成0的话程序内部会自动计算
process_output=1           //是否输出中间文件（相关的代码还没有写）
lowest_accuracy=0.85       //测试低于此准确率自动停止
other_class=others         //负类标注类名
stop_ratio = 0.1           //迭代停止时剩余样本与总样本的比例
stop_limitation=30         //迭代停止时剩余样本数量（比例与数量二选一）

***************  迭代部分 *********************
程序的每次迭代分为两步:

第一步:聚类
	需要运行的是Iteration.java，在linux中可以直接ant cluster -Diter=X（第X次迭代）运行程序。
	运行java文件时，传入的参数为-cluster X（第X次迭代）。
	这步的输出文件为ClusterResultX_fY.csv,(X是迭代次数，Y是feature文件id)，此结果文件第一列是文档名称，第二列是cluster。
	人工标注的时候需要在所有cluster里面选择一个聚类效果最好的cluster进行标注，标注的正例应为本次迭代的所有文件总数的15%，然后标注不属于这个类的其他文件，标注的负例应为本次迭代的所有文件总数的15%。
        标注在ClusterResultX_fY.csv中进行。在簇号列的后一列（第三列），标注后的文件格式应该为第一列是文档名称，第二列是分类名称，如果是正例则填写正确分类名称，如果是负例则填写“others”，既不标成正也不标成负分类的留空。

第二步：根据人工标注结果训练分类器分类
	需要运行的是Iteration.java，在linux中可以直接运行ant classify -Diter=X（第X次迭代）运行程序。
	运行java文件时，传入的参数为-classify X（第X次迭代）。
	分类的输出包括两部分，第一部分是对分类器进行测试的结果，结果存在ClassifyTestResultX_fY.txt(X是迭代次数，Y是feature文件id)中。
	第二部分是使用分类器对未知文档进行分类，结果存在ClassifyResult_fY.csv（Y是feature id）中。
	注:对同一特征的所有迭代分类结果都写在通一个文件中，即ClassifyResult_fY.csv  Y在classify.properties中设定

需要注意，在迭代停止后，需要人工对迭代停止后剩余的文件进行标注，最后将所有标注数据（包括最后一次）和分类结果进行整合，得到所有instanceOf关系。

以上输出文档都在../data/Classify中（不包括中间输出文档）

除此之外，不需要人工标注，程序自动迭代运行直到停止的参数为-iter X（第X次迭代）,仅供程序测试用。
在linux中可以直接ant run -Diter=X， X=0时，程序自动迭代直到下次迭代样本数量小于规定值停止

***********************  输出文件命名 ***********************
输入文件：
    featuresY.csv(Y为特征id) 
    注：feature文件的命名在conf/feature.cfg中，每个section的命名，即[]中的内容，即为此feature文件的命名
    sampleX.txt 进入本次迭代的文档列表
结果文件：
    X：第X次迭代；  Y：特征id
	ClassifyResult_fY.csv        分类结果文件，最终结果文件
	ClusterResultX_fY.csv        聚类结果文件，聚类后人工标注在此文件
	ClassifyTestResultX_fY.txt   分类测试结果
	attribute_files.txt          属性文档列表
	hub_files.txt                hub文档列表
	not_sample.txt               未进入迭代器的文档列表
	
中间文件：
	classifyX_fY_train.csv                测试时的训练数据
	classifyX_fY_test.csv                 测试时的测试数据
	classifyX_fY_predict.csv                 需要被分类的数据（本次迭代数据减去train和test）
	
***********  写入数据库 ************
配置文件:
	../conf/conf.properties//公共文件，数据库相关
读入文件：
    最终分类结果的csv文件，作为参数传入(传入参数：-file ../data/Classify/ClassifyResult_f1.csv)
ant命令：
ant db -Dfile=../data/Classify/ClassifyResult_f1.csv
