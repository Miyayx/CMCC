package edu.thu.cmcc.classification;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.TreeMap;
import java.util.Map.Entry;

import weka.clusterers.XMeans;
import weka.core.EuclideanDistance;
import weka.core.Instance;
import weka.core.Instances;
import edu.thu.cmcc.basic.CSVFileIO;
import edu.thu.cmcc.classification.instances.ClusterInstances;
import edu.thu.cmcc.classification.instances.InstancesGetter;

public class XMEANS {
	HashMap<String, Integer> docClusterMap = new HashMap<String, Integer>();// <文档名,簇号>
	Map<Integer, LinkedList<String>> result = new LinkedHashMap<Integer, LinkedList<String>>();// 相应簇号
	InstancesGetter insGetter;
	int clusterNum = 0;
	XMeans cluster = null;

	public HashMap<String, Integer> getDocClusterMap() {
		return docClusterMap;
	}

	public void setDocClusterMap(HashMap<String, Integer> docClusterMap) {
		this.docClusterMap = docClusterMap;
	}

	public XMEANS() {
		insGetter = new ClusterInstances();
		cluster = new XMeans();
		cluster = (XMeans) cluster;
		try {
			cluster.setMaxIterations(500);// 设置迭代次数
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
		try {
			c.run(5, "etc/features1.csv", "etc/sample1.txt",
					"etc/ClusterResult1_f1.txt");
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
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

	public void appendToResultFile(String resultfile) {
		String colname = "cluster" + ClassifyProperties.Iteration_ID;
		Map<String, String> sample2cluster = new HashMap<String, String>();
		for (Entry<Integer, LinkedList<String>> e : result.entrySet()) {
			for (String s : e.getValue())
				sample2cluster.put(s, String.valueOf(e.getKey()));
		}
		try {
			CSVFileIO csv = new CSVFileIO();
			csv.load(resultfile, true);
			csv.column(colname, sample2cluster);
			// csv.addEmptyColumn("flag"+ClassifyProperties.Iteration_ID);
			// csv.write(resultfile, ",", true, true,
			// ClassifyProperties.CLUSTER_INDEX);
			csv.write(resultfile, ",", true, true, 0);
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
			String resultFile) throws Exception {
		Instances ins;
		this.clusterNum = clusterNum;

		ins = insGetter.getInstances(featureFile);
		this.run(ins, resultFile);

	}

	public void run(int clusterNum, String resultFile) throws Exception {
		Instances ins;
		this.clusterNum = clusterNum;

		ins = insGetter.getInstances(resultFile, 0, 1,
				ClassifyProperties.FEATURE_COUNT,
				ClassifyProperties.FILTER_INDEX);
		this.run(ins, resultFile);

	}

	public void run(Instances ins, String resultFile) throws Exception {
		// 1.读入样本
		Instances tempIns = null;

		// 2. 获得文档名
		String[] labelAttr = InstancesGetter.getIDs(ins);
		ins.deleteAttributeAt(0); // 删不删第一列sample结果都是一样的

		cluster.setSeed(ClassifyProperties.BEST_SEED);

		// 4.使用聚类算法对样本进行聚类
		cluster.buildClusterer(ins);

		tempIns = cluster.getClusterCenters();

		// 将簇号按顺序写入list
		for (int i = 0; i < ins.numInstances(); i++) {
			Instance instance = ins.instance(i);
			int c = cluster.clusterInstance(instance);
			LinkedList list = null;
			docClusterMap.put(labelAttr[i], c);
			if (result.containsKey(c)) {
				list = result.get(c);
			} else {
				list = new LinkedList<String>();
			}
			list.add(labelAttr[i]);
			result.put(c, list);
		}

		Iterator it = result.entrySet().iterator();
		Map<Integer, Integer> sortedResult = new TreeMap<Integer, Integer>();
		while (it.hasNext()) {
			Map.Entry pairs = (Map.Entry) it.next();
			LinkedList<String> v = (LinkedList<String>) pairs.getValue();
			Collections.sort(v);
			result.put((Integer) pairs.getKey(), v);
			sortedResult.put((Integer) pairs.getKey(), v.size());
		}

		for (Entry entry : sortedResult.entrySet()) {
			System.out.println("Cluster " + entry.getKey() + ":"
					+ entry.getValue());
		}
	}

}
