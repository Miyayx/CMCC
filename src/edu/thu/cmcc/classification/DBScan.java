package edu.thu.cmcc.classification;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.Map.Entry;

import edu.thu.cmcc.basic.CSVFileIO;
import edu.thu.cmcc.basic.FileUtils;
import edu.thu.cmcc.classification.ClassifyProperties;
import edu.thu.cmcc.classification.instances.ClusterInstances;
import edu.thu.cmcc.classification.instances.InstancesGetter;
import weka.clusterers.ClusterEvaluation;
import weka.clusterers.Clusterer;
import weka.clusterers.DBSCAN;
import weka.clusterers.SimpleKMeans;
import weka.core.Instance;
import weka.core.Instances;
import weka.core.converters.ArffLoader;

public class DBScan {

	static private double eps = 2;
	static private int minp = 3;
	HashMap<String, Integer> docClusterMap = new HashMap<String, Integer>();// <文档名,簇号>
	Map<Integer, LinkedList<String>> result = new LinkedHashMap<Integer, LinkedList<String>>();// 相应簇号
	private double eps_delta = 0.1;
	private int minInstanceNum = 40;
	private int minClusterNum = 4;
	private int maxClusterNum = 6;
	private int clusterNum = 0;
	weka.clusterers.DBSCAN cluster = null;
	private InstancesGetter insGetter;

	public DBScan() {
		insGetter = new ClusterInstances();
		cluster = new DBSCAN();
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

	public void run(double eps, int minp, String featureFile,
			String sampleFile, String resultFile) throws Exception {
		Instances ins;
		this.minp = minp;
		this.eps = eps;

		ins = insGetter.getInstances(featureFile);
		this.run(ins, resultFile);
	}

	public void run(double eps, int minp, String resultFile) throws Exception {
		Instances ins;
		this.minp = minp;
		this.eps = eps;

		ins = insGetter.getInstances(resultFile, 0, 1,
				ClassifyProperties.FEATURE_COUNT,
				ClassifyProperties.FILTER_INDEX);
		this.run(ins, resultFile);
	}

	public void run(Instances ins, String resultFile) throws Exception {

		// 2. 获得文档名

		String[] labelAttr = InstancesGetter.getIDs(ins);
		ins.deleteAttributeAt(0); // 删不删第一列sample结果都是一样的

		cluster.setEpsilon(eps);// 邻域大小
		cluster.setMinPoints(minp);// 邻域中最小点数
		cluster.buildClusterer(ins);

		ClusterEvaluation eval = new ClusterEvaluation();
		eval.setClusterer(cluster);
		eval.evaluateClusterer(ins);

		double[] num = eval.getClusterAssignments();
		this.clusterNum = eval.getNumClusters();

		// 将簇号按顺序写入list
		for (int i = 0; i < num.length; i++) {
			//Instance instance = ins.instance(i);
			//int c = cluster.clusterInstance(instance);
			int c= (int)num[i];
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
