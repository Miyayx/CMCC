package classification_dbscan;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Collections;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;

import edu.thu.cmcc.basic.FileUtils;
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
	static private final int minp = 3;
	Map<Integer, LinkedList<String>> result = new LinkedHashMap<Integer, LinkedList<String>>();// 相应簇号
	String[] docName = null;
	String[] iterFiles = null;
	private double eps_delta = 0.1;
	private int minInstanceNum = 40;
	private int minClusterNum = 4;
	private int maxClusterNum = 6;
	
	private InstancesGetter insGetter = new ClusterInstances();

	// Clusterer dbscan = (Clusterer) new DBSCAN();

	public void setIterFilter(String[] files) {
		this.iterFiles = files;
	}

	public String[] getDocName(Instances ins) {
		double sum = ins.numInstances();
		String[] names = new String[(int) (sum)];

		for (int i = 0; i < sum; i++)
			names[i] = ins.instance(i).toString(0);
		return names;
	}

	public boolean run(String featureFile, String sampleFile, String resultFile) {
		Instances ins = null;

		try {
			
			weka.clusterers.DBSCAN dbs = new DBSCAN();
			
			ins = insGetter.getInstances(featureFile);
			ins = FileUtils.getFilterDataset(sampleFile, ins);

			docName = getDocName(ins);

			if (docName.length < minInstanceNum)
				minClusterNum = 3;

			dbs.setEpsilon(eps);// 邻域大小
			dbs.setMinPoints(minp);// 邻域中最小点数
			dbs.buildClusterer(ins);
			ClusterEvaluation eval = new ClusterEvaluation();
			eval.setClusterer(dbs);
			eval.evaluateClusterer(ins);

			double[] num = eval.getClusterAssignments();

			// for (int i = 0; i < num.length; i++) {
			// System.out.println(String.valueOf(num[i]));
			// }
			// System.out.println(eval.clusterResultsToString());
			// System.out.println(eval.getNumClusters());

			Map<Integer, HashSet<String>> resultSet = new LinkedHashMap<Integer, HashSet<String>>();// 相应簇号

			for (int i = 0; i < num.length; i++) {
				int c = (int) num[i];
				if (resultSet.containsKey(c)) {
					HashSet<String> list = resultSet.get(c);
					list.add(docName[i]);
					resultSet.put(c, list);
				} else {
					HashSet<String> list = new HashSet<String>();
					list.add(docName[i]);
					resultSet.put(c, list);
				}
			}

			// 判断本次聚类结果是否符合条件
			// 判断标准：
			// 1.
			// 2.
			System.out.println(" Eps:" + eps);
			if (resultSet.size() < minClusterNum) {
				eps -= eps_delta;
				return false;
			}
			if (resultSet.size() > maxClusterNum) {
				eps += eps_delta;
				return false;
			}

			System.out.println("Final Eps is" + eps);

			Iterator it = resultSet.entrySet().iterator();
			while (it.hasNext()) {
				Map.Entry pairs = (Map.Entry) it.next();
				HashSet<String> v = (HashSet<String>) pairs
						.getValue();
				LinkedList<String> l = new LinkedList<String>(v);
				Collections.sort(l);
				result.put((Integer) pairs.getKey(), l);
			}

			writeToFile(resultFile, eval);
			// writeToMongo(result);

		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return true;
	}

	public void writeToFile(String file, ClusterEvaluation eval) {
		try {
			FileWriter fw = new FileWriter(file);
			BufferedWriter out = new BufferedWriter(fw);

			// out.write(eval.clusterResultsToString());

			for (int w = -1; w < result.size() - 1; w++) {

				List<String> docs = result.get(w);
				for (String d : docs)
					out.write(d + "\t\t" + w + "\n");
			}
			out.close();
			fw.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public static void main(String[] args) throws Exception {
		DBScan dbs = new DBScan();
		Boolean dbscanOK = dbs.run("etc/features9.csv", "etc/samples1.txt",
				"etc/DBSCANClusterResult.txt");
		while (!dbscanOK) {
			dbscanOK = dbs.run("etc/features9.csv", "etc/samples1.txt",
					"etc/DBSCANClusterResult.txt");
		}
	}
}
