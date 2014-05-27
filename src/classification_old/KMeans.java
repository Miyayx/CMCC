package classification_old;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.net.UnknownHostException;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBObject;
import com.mongodb.Mongo;

import edu.thu.cmcc.basic.FileUtils;
import edu.thu.cmcc.classification.instances.ClusterInstances;
import edu.thu.cmcc.classification.instances.InstancesGetter;
import weka.clusterers.SimpleKMeans;
import weka.core.Instance;
import weka.core.Instances;
import weka.core.converters.*;
import weka.core.*;
import weka.filters.Filter;
import weka.filters.unsupervised.attribute.NumericToNominal;

public class KMeans {
	HashMap<String, Integer> docClassifyMap = new HashMap<String, Integer>();// <文档名,簇号>
	Map<Integer, LinkedList<String>> result = new LinkedHashMap<Integer, LinkedList<String>>();// 相应簇号
	String[] docName = null;
	String[] iterFiles = new String[1];
	int iter = 0;
	SimpleKMeans KM = null;

	private InstancesGetter insGetter = new ClusterInstances();

	public void setIterFilter(String[] files) {
		this.iterFiles = files;
	}

	public void setIterNum(int iter) {
		this.iter = iter;
	}

	public SimpleKMeans getKM() {
		return KM;
	}

	public static void main(String[] args) {
		// iter 0 n=4
		// iter1 n = 5 因n=5的时候可以把品牌分出来

		KMeans km = new KMeans();
		for (int i = 3; i < 11; i++)
			km.run(i, "etc/features1.csv", "etc/samples1.txt",
					"etc/KMeansClusterResult.txt");

	}

	public String[] getDocName(Instances ins) {
		double sum = ins.numInstances();
		String[] names = new String[(int) (sum)];

		for (int i = 0; i < sum; i++)
			names[i] = ins.instance(i).toString(0);
		return names;
	}

	public void writeToFile(String file, int clusterNum, double error) {
		try {
			FileWriter fw = new FileWriter(file);
			BufferedWriter out = new BufferedWriter(fw);
			// out.write("\t簇数:" + clusterNum + "\tSquaredError:" + error +
			// "\n");
			// // 两个list相互对应
			// for (int w = 0; w < clusterNum; w++) {
			// out.write("----------------------------------------" + w
			// + "----------------------------------------" + "\n");
			//
			// List<String> docs = result.get(w);
			// out.write("数量:" + docs.size() + "\n");
			// for (String d : docs)
			// out.write(d + "\n");
			// out.write("\n");
			// }
			for (int w = 0; w < clusterNum; w++) {

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
		Instances ins = null;
		Instances tempIns = null;

		// 1.读入样本
		try {
			ins = insGetter.getInstances(featureFile);

			// ins = FileUtils.getFilterDataset(this.iterFiles, ins);

			// 2. 获得文档名
			docName = getDocName(ins);
			ins.deleteAttributeAt(0);

			// 3.初始化聚类器
			KM = new SimpleKMeans();
			KM.setMaxIterations(500);// 设置迭代次数
			// System.out.println("迭代次数："+KM.getMaxIterations());
			KM.setNumClusters(clusterNum);// 设置类别数量～～～～～
			KM.setSeed(50);
			KM.setPreserveInstancesOrder(true);
			// KM.setDistanceFunction(new ManhattanDistance());//更差

			// 4.使用聚类算法对样本进行聚类
			KM.buildClusterer(ins);
			// 5.打印聚类结果
			tempIns = KM.getClusterCentroids();// 得到质心

			// 评估
			// ClusterEvaluation eval = new ClusterEvaluation();
			// eval.setClusterer(KM);
			// eval.evaluateClusterer(new Instances(ins));
			// System.out.println("打印评估结果："+eval.clusterResultsToString());

			// System.out.println("CentroIds: " + tempIns);
			// System.out.println(" tempIns.numInstances():"+
			// tempIns.numInstances());
			// 对于每个个类
			// for (int i = 0; i < tempIns.numInstances(); i++) {
			// Instance temp = tempIns.instance(i);//每一个类
			//
			// Instances ins2=temp.dataset();//分类下面的实例
			// System.out.println("ins2.numInstances():"+ins2.numInstances());
			//
			// for(int j=0;j<ins2.numInstances();j++){
			// System.out.println("每个文档的分类："+KM.clusterInstance(ins2.instance(j)));
			// }
			// // int indexOfCluster =KM.clusterInstance(temp);
			// // System.out.println("indexOfCluster:"+indexOfCluster);
			// }
			// KM.setPreserveInstancesOrder(true);
			// System.out.println("打印ID:"+KM.getAssignments());

			// 将簇号按顺序写入list
			for (int i = 0; i < ins.numInstances(); i++) {
				Instance instance = ins.instance(i);
				int c = KM.clusterInstance(instance);
				if (result.containsKey(c)) {
					LinkedList list = result.get(c);
					list.add(docName[i]);
					result.put(c, list);
				} else {
					LinkedList list = new LinkedList<String>();
					list.add(docName[i]);
					result.put(c, list);
				}
			}

			Iterator it = result.entrySet().iterator();
			while (it.hasNext()) {
				Map.Entry pairs = (Map.Entry) it.next();
				LinkedList<String> v = (LinkedList<String>) pairs.getValue();
				Collections.sort(v);
				result.put((Integer) pairs.getKey(), v);
			}

			double intra = 0;
			EuclideanDistance distance = new EuclideanDistance();
			distance.setInstances(ins);
			System.out.println(tempIns.numInstances());
			for (int i = 0; i < ins.numInstances(); i++) {
				Instance instance = ins.instance(i);
				int c = KM.clusterInstance(instance);
				double d = distance.distance(instance, tempIns.instance(c));
				// System.out.println(d);
				intra += d;
			}

			System.out.println("Intra-Cluster Similarity:" + intra);
			System.out.println("Inter-Cluster Similarity:"
					+ KM.getSquaredError());
			System.out.println("Ratio:" + (KM.getSquaredError() / intra));

			writeToFile(resultFile, clusterNum, KM.getSquaredError());
			// writeToMongo(result);

		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public void writeToMongo(Map map) throws UnknownHostException {
		System.out.println("writeToMongo");
		Mongo mongo = new Mongo();
		DB db = mongo.getDB("mobile");
		DBCollection collection = db.getCollection("doc_parse");

		Iterator it = map.entrySet().iterator();
		while (it.hasNext()) {
			Map.Entry pairs = (Map.Entry) it.next();
			int k = ((Integer) pairs.getKey()).intValue(); // cluster
			List<String> list = (List<String>) pairs.getValue(); // docs for
																	// cluster k
			for (String l : list) {
				String[] ks = l.split("/");
				int len = ks.length;
				String path = "";
				for (int i = 0; i < len - 1; i++) {
					path += ks[i];
					path += "/";
				}
				path = path.replaceFirst("etc", "../data");
				String name = ks[len - 1];

				DBObject updateCondition = new BasicDBObject();
				updateCondition.put("_id.name", name);
				updateCondition.put("_id.path", path);

				DBObject updatedValue = new BasicDBObject();
				updatedValue.put("cluster", k);

				DBObject updateSetValue = new BasicDBObject("$set",
						updatedValue);

				collection.update(updateCondition, updateSetValue);
			}
			it.remove(); // avoids a ConcurrentModificationException
		}
	}
}
