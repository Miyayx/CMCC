
python部分一定在classify_python里运行 
##############  文档 ###############
**************  特征提取 *************

python classify_preprocess.py(需要在classify_python路径下运行)

**************  数据库读取验证 *************
代码在classify_python里
python db_validation.py > outputfile

**************  特征验证 *************
代码在classify_python里
python feature_validation.py > outputfile

**************  属性文档验证 *************
python attribute.py > outputfile

************** 特征提取+相关验证 **********
sh start.sh
默认验证输出 ../../data/Classify/val

*************  聚类分类迭代 ************
第一步:聚类
	需要运行的是cluster.py，
    在linux中运行命令：
    python cluster.py Y 
    python cluster.py Y k 
    python cluster.py Y init 
    python cluster.py Y k init
    Y:    第Y次迭代
    k:    指定聚类簇数
    init: 指定计算初始聚类中心的方法，默认k-means++,另外还有:
        even: 每隔N/k选取一个点
        spss: 算法来自Single Pass Seed Selection Algorithm for k-Means, 号称kmeans++改进版，可获得确定的中心点
        density: 算法来自Clustering by fast search and find of density peaks,根据点周围的密度来确定，运行较快
        nbc :    算法来自Neighborhood Density Method for Selecting Initial Cluster Centers in K-Means Clustering, 根据点的邻居个数确定，运行较慢

第二步：人工标注
    配置文件在conf/annotation.cfg中，
    运行python annotation.py X X是迭代次数

第三步：根据人工标注结果训练分类器分类
	需要运行的是classify.py，在linux中可以直接运行python classify.py X（第X次迭代）运行程序。

