package edu.thu.cmcc.classification;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.net.UnknownHostException;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBObject;
import com.mongodb.Mongo;

import edu.thu.cmcc.basic.CSVFileIO;
import edu.thu.cmcc.classification.instances.ClusterInstances;
import edu.thu.cmcc.classification.instances.InstancesGetter;
import weka.clusterers.SimpleKMeans;
import weka.core.EuclideanDistance;
import weka.core.Instance;
import weka.core.Instances;

public class Cluster {
	HashMap<String, Integer> docClassifyMap = new HashMap<String, Integer>();// <文档名,簇号>
	Map<Integer, LinkedList<String>> result = new LinkedHashMap<Integer, LinkedList<String>>();// 相应簇号
	InstancesGetter insGetter;
	int clusterNum = 0;
	SimpleKMeans cluster = null;

	public Cluster() {
		insGetter = new ClusterInstances();
		cluster = new SimpleKMeans();
		cluster = (SimpleKMeans) cluster;
		try {
			cluster.setMaxIterations(500);// 设置迭代次数
			cluster.setSeed(50);
			cluster.setPreserveInstancesOrder(true);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public void setMaxClusterNum(int num) {
		this.clusterNum = num;
	}

	public static void main(String[] args) {
		// iter 0 n=4
		// iter1 n = 5 因n=5的时候可以把品牌分出来
		Cluster c = new Cluster();
		String[] files = { "etc/sample1.txt" };
		c.run(5, "etc/features1.csv", "etc/sample1.txt",
				"etc/ClusterResult1_f1.txt");
	}

	public void writeToFile(String file) {
		try {
			FileWriter fw = new FileWriter(file);
			BufferedWriter out = new BufferedWriter(fw);

			for (int w = 0; w < clusterNum; w++) {

				List<String> docs = result.get(w);
				for (String d : docs)
					out.write(d + "," + w + "\n");
			}
			out.close();
			fw.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public void appendToResultFile(String resultfile){
		String colname = "cluster"+ClassifyProperties.Iteration_ID;
		Map<String, String> sample2cluster = new HashMap<String, String>();
		for(Entry<Integer, LinkedList<String>> e : result.entrySet()){
			for(String s:e.getValue())
				sample2cluster.put(s, String.valueOf(e.getKey()));
		}
		try {
			CSVFileIO csv = new CSVFileIO();
			csv.load(resultfile, true);
			csv.column(colname, sample2cluster);
		//	csv.addEmptyColumn("flag"+ClassifyProperties.Iteration_ID);
			csv.write(resultfile, ",",true,true,ClassifyProperties.CLUSTER_INDEX);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	/**
	 * KMeans
	 * 
	 * @param clusterNum
	 *            聚类簇数
	 * @param path
	 *            arff文件
	 * @param path1
	 *            文档名列表文件（顺序）
	 * @param path2
	 *            聚类结果文件（顺序）
	 * @throws Exception
	 */
	public void run(int clusterNum, String featureFile, String dataFile,
			String resultFile) {
		Instances ins;
		this.clusterNum = clusterNum;
		try {
			ins = insGetter.getInstances(featureFile);
			this.run(ins, resultFile);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}

	public void run(int clusterNum, String resultFile) {
		Instances ins;
		this.clusterNum = clusterNum;
		try {
			ins = insGetter
					.getInstances(
							resultFile,
							0,
							1,
							ClassifyProperties.FEATURE_COUNT,
							ClassifyProperties.FILTER_INDEX);
			this.run(ins, resultFile);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public void run(Instances ins, String resultFile) throws Exception {
		// 1.读入样本
		Instances tempIns = null;

		// 2. 获得文档名
		String[] labelAttr = InstancesGetter.getIDs(ins);
		ins.deleteAttributeAt(0); //删不删第一列sample结果都是一样的

		// 3.初始化聚类器
		cluster.setNumClusters(clusterNum);// 设置类别数量～～～～～

		// 4.使用聚类算法对样本进行聚类
		cluster.buildClusterer(ins);
		// 5.打印聚类结果
		tempIns = cluster.getClusterCentroids();// 得到质心
		
		// 将簇号按顺序写入list
		for (int i = 0; i < ins.numInstances(); i++) {
			Instance instance = ins.instance(i);
			int c = cluster.clusterInstance(instance);
			LinkedList list = null;
			if (result.containsKey(c)) {
				list = result.get(c);
			} else {
				list = new LinkedList<String>();
			}
			list.add(labelAttr[i]);
			result.put(c, list);
		}

		Iterator it = result.entrySet().iterator();
		while (it.hasNext()) {
			Map.Entry pairs = (Map.Entry) it.next();
			LinkedList<String> v = (LinkedList<String>) pairs.getValue();
			Collections.sort(v);
			result.put((Integer) pairs.getKey(), v);
		}
	}

	/**
	 * 获得分类簇数 取类间比类内最大值
	 * @param featureFile
	 * @return
	 */
	public static int getMaxClusterNum(String featureFile) {
		SimpleKMeans KM = new SimpleKMeans();
		Instances ins = null;
		Instances tempIns = null;
		int clusterNum = 0;
		double maxRatio = 0;

		for (int i = 3; i < 11; i++) {
			// 1.读入样本
			try {
				ins = new ClusterInstances()
						.getInstances(
								featureFile,
								0,
								1,
								ClassifyProperties.FEATURE_COUNT,
								ClassifyProperties.FILTER_INDEX);
			//	ins = new ClusterInstances().getInstances(featureFile);

				KM.setNumClusters(i);

				// 4.使用聚类算法对样本进行聚类
				KM.buildClusterer(ins);
				// 5.打印聚类结果
				tempIns = KM.getClusterCentroids();// 得到质心

				double intra = 0;
				EuclideanDistance distance = new EuclideanDistance();
				distance.setInstances(ins);
				System.out.println(tempIns.numInstances());

				// 计算类内距离
				for (int j = 0; j < ins.numInstances(); j++) {
					Instance instance = ins.instance(j);
					int c = KM.clusterInstance(instance);
					double d = distance.distance(instance, tempIns.instance(c));
					intra += d;
				}

				System.out.println("Intra-Cluster Similarity:" + intra);
				System.out.println("Inter-Cluster Similarity:"
						+ KM.getSquaredError());
				double ratio = (KM.getSquaredError() / intra);
				System.out.println("Ratio:" + ratio);
				if (ratio > maxRatio) {
					clusterNum = i;
					maxRatio = ratio;
				}
			} catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}

		System.out.println("FINAL CLUSTER NUM: " + clusterNum);
		return clusterNum;
	}
}
