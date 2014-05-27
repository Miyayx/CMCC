package classification_old;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBCursor;
import com.mongodb.DBObject;
import com.mongodb.Mongo;

import edu.thu.cmcc.basic.FileUtils;
import edu.thu.cmcc.classification.instances.ClassifyInstances;
import edu.thu.cmcc.classification.instances.InstancesGetter;
import weka.classifiers.Classifier;
import weka.classifiers.functions.LibSVM;
import weka.core.Instances;
import weka.core.converters.ArffLoader;
import weka.core.converters.ArffSaver;
import weka.core.converters.CSVLoader;
import weka.filters.Filter;
import weka.filters.unsupervised.attribute.NumericToNominal;

public class Classify {

	private List<String> suspicious = new ArrayList<String>();
	private Classifier m_classifier = null;
	private Instances instancesTrain = null;
	private Instances instancesTest = null;
	private InstancesGetter insGetter = null;

	public Classify() {
		insGetter = new ClassifyInstances();
	}

	public Classify(Classifier c) {
		this();
		this.m_classifier = c;
	}

	public void writeClassificationResult(Map map, Map map2, String file) {
		try {
			FileWriter fw = new FileWriter(file);
			BufferedWriter bw = new BufferedWriter(fw);
			Iterator it = map.entrySet().iterator();
			while (it.hasNext()) {
				Map.Entry pairs = (Map.Entry) it.next();
				String key = (String) pairs.getKey();
				bw.write(pairs.getKey() + "\t\t" + pairs.getValue() + "\t\t"
						+ map2.get(key) + "\r\n");
			}
			bw.close();
			fw.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	/**
	 * 
	 * @param file
	 *            filename
	 * @param classifer
	 *            classifer name
	 * @param pre
	 *            precision
	 * @param map
	 *            document to class
	 */
	public void writeToFile(String file, double pre, Map map) {
		try {
			FileWriter fw = new FileWriter(file);
			BufferedWriter bw = new BufferedWriter(fw);
			bw.write("Classifer:" + this.m_classifier.getClass().getName()
					+ "\r\n");
			bw.write("Classification precision:" + pre + "\r\n");
			Iterator it = map.entrySet().iterator();
			while (it.hasNext()) {
				Map.Entry pairs = (Map.Entry) it.next();
				bw.write(pairs.getKey() + "\t\t" + pairs.getValue() + "\r\n");
			}
			bw.close();
			fw.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public void writeSuspiciousToFile(String file) {
		try {
			FileWriter fw = new FileWriter(file);
			BufferedWriter bw = new BufferedWriter(fw);

			for (String s : suspicious)
				bw.write(s + "\r\n");

			bw.close();
			fw.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public String[] getIDs(Instances instances) {
		double sum = instances.numInstances(); // 测试语料实例数
		String[] names = new String[(int) (sum)];

		for (int i = 0; i < sum; i++)// 测试分类结果
		{
			names[i] = instances.instance(i).toString(0);
		}
		return names;
	}

	public Map<String, String> getClassMap(Instances instances) {
		Map classMap = new HashMap<Integer, String>();// 类别编号对应集
		// 因测试返回的结果是一个double类型的编号，而不是类别名称，遍历Test集获得类别集以及其对应的编号
		int class_id = 0;
		for (int i = 0; i < instances.numInstances(); i++) {
			String className = instances.instance(i).toString(
					instances.numAttributes() - 1);
			if (classMap.containsValue(className)) {
				continue;
			} else {
				System.out.println(className + "=" + class_id);
				classMap.put(class_id, className);
				class_id++;
			}
		}
		return classMap;
	}

	public void train() throws Exception {
		instancesTrain.deleteAttributeAt(0);// 第一列是文档名，删除
		m_classifier.buildClassifier(instancesTrain); // 训练
	}

	/**
	 * 分类过程
	 * 
	 * @param m_classifier
	 *            分类器
	 * @param classifer
	 *            分类器名称（字符串）
	 * @param instancesTrain
	 *            训练样本
	 * @param instancesTest
	 *            测试样本
	 * @param testLabels
	 *            训练样本的document名称
	 * @param resultFile
	 *            结果输出文件
	 * @return 以document名称为key，类别字符串为value的map
	 * @throws Exception
	 */
	public Map test(String testFile) throws Exception {

		double sum = instancesTest.numInstances(), // 实例数
		right = 0.0f;

		Map<String, String> classMap = getClassMap(instancesTest);
		String[] testLabels = getIDs(instancesTest);
		instancesTest.deleteAttributeAt(0);

		Map map = new LinkedHashMap<String, String>();// 分类结果map
		// label to result class
		double precision = 0;
		int wrong = 0;
		for (int i = 0; i < sum; i++)// 测试分类结果
		{
			double result = 0;
			try {
				result = m_classifier.classifyInstance(instancesTest
						.instance(i));

				// double[] d =
				// m_classifier.distributionForInstance(instancesTest
				// .instance(i));
				// System.out.println("d0=" + d[0] + "\td1=" + d[1] + "\t"
				// + testLabels[i]);
			} catch (Exception e) {

			} finally {
				map.put(testLabels[i], classMap.get(new Integer((int) result)));
				// map.put(testLabels[i], result);

				if (result == instancesTest.instance(i).classValue())// 如果预测值和答案值相等
				{
					right++;// 正确值加1
				} else {
					wrong++;
					// 输出分类错误样本
					System.out.println(testLabels[i]
							+ "\t"
							+ instancesTest.instance(i).toString(
									instancesTest.numAttributes() - 1)
							+ "\torigin"
							+ instancesTest.instance(i).classValue()
							+ "\tresult" + result);
				}
			}
		}

		precision = right / (sum - suspicious.size());
		System.out.println("Suspicious Number:" + suspicious.size());
		System.out.println("Classification precision:" + precision);
		System.out.println("Wrong number:" + wrong);

		writeToFile(testFile, precision, map);
		return map;
	}

	public void classification(String otherfile, String resultfile)
			throws Exception {
		Instances instancesOther = insGetter.getInstances(otherfile);
		this.classification(instancesOther, resultfile);
	}

	public void classification(Instances instances, String resultfile) {
		// Map<String,String> classMap = getClassMap(instances);
		String[] labels = getIDs(instances);
		instances.deleteAttributeAt(0);// 第一列是文档名，删除

		Map map = new LinkedHashMap<String, String>();// 分类结果map
		Map map2 = new LinkedHashMap<String, String>();// 人工标注结果map

		try {
			double result = 0;
			for (int i = 0; i < instances.numInstances(); i++) {

				try {
					result = this.m_classifier.classifyInstance(instances
							.instance(i));
					map.put(labels[i], result);
					map2.put(
							labels[i],
							instances.instance(i).toString(
									instances.numAttributes() - 1));

					double[] d = m_classifier.distributionForInstance(instances
							.instance(i));
					System.out.println("d0=" + d[0] + "\td1=" + d[1] + "\t"
							+ labels[i]);
					if (d[0] != 0 && d[0] != 1 && d[0] != 0 && d[1] != 1) {
						System.out.println(labels[i]
								+ "\t"
								+ result
								+ "\t"
								+ instances.instance(i).toString(
										instances.numAttributes() - 1));
						suspicious.add(labels[i]);
					}
				} catch (Exception e) {

					System.out.println(labels[i]
							+ "\t"
							+ result
							+ "\t"
							+ instances.instance(i).toString(
									instances.numAttributes() - 1));
					// map.put(labels[i], result);
					// map2.put(labels[i],instances.instance(i).toString(instances.numAttributes()
					// - 1));
					suspicious.add(labels[i]);
					// }
				}
				// map.put(labels[i], classMap.get(new Integer((int) result)));
			}

			writeClassificationResult(map, map2, resultfile);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public void run(String featureFile, String trainFile, String testFile,
			String testResultFile) throws Exception {

		this.instancesTrain = insGetter.getInstances(trainFile);
		this.instancesTest = insGetter.getInstances(testFile);

		this.train();
		Map map = this.test(testResultFile);
		// writeToMongo(map);
	}

	public void run(String featureFile, String dataFile, double ratio,
			String testResultFile) throws Exception {
		Instances instances = insGetter.getInstances(dataFile);
		int num = instances.numAttributes();
		int index = (int) (num * ratio);
		instancesTrain = new Instances(instances, 0, index);
		instancesTest = new Instances(instances, index, num);

		this.train();
		Map map = this.test(testResultFile);
	}

	public static void main(String[] args) throws Exception {
		Classify c = new Classify();
		Classifier m_classifier = new LibSVM();
		/*
		 * -S set type of SVM (default 0) 0 = C-SVC 1 = nu-SVC 2 = one-class SVM
		 * 3 = epsilon-SVR 4 = nu-SVR -K set type of kernel function (default 2)
		 * 0 = linear: u'*v 1 = polynomial: (gamma*u'*v + coef0)^degree 2 =
		 * radial basis function: exp(-gamma*|u-v|^2) 3 = sigmoid:
		 * tanh(gamma*u'*v + coef0) -D set degree in kernel function (default 3)
		 * -G set gamma in kernel function (default 1/k) -R set coef0 in kernel
		 * function (default 0) -C set the parameter C of C-SVC, epsilon-SVR,
		 * and nu-SVR (default 1) -N set the parameter nu of nu-SVC, one-class
		 * SVM, and nu-SVR (default 0.5) -Z whether to normalize input data, 0
		 * or 1 (default 0) -P set the epsilon in loss function of epsilon-SVR
		 * (default 0.1) -M set cache memory size in MB (default 40) -E set
		 * tolerance of termination criterion (default 0.001) -H whether to use
		 * the shrinking heuristics, 0 or 1 (default 1) -W set the parameters C
		 * of class i to weight[i]*C, for C-SVC (default 1)
		 */

		String[] options = {// SVM的参数配置
				// "-split-percentage","50",
				"-K", "0", "-S", "0", "-x", "10", "-N", "0", "-M", "100", "-W",
				"1.0 1.0", "-G", "0.5", "-P", "0.8", "-b", "1" };
		m_classifier.setOptions(options);
		c.run("etc/features1.csv", "etc/train1_f1.csv", "etc/test1_f1.csv",
				"etc/ClassifyResult1_f1.txt");
		c.writeSuspiciousToFile("etc/suspicious1_f1.txt");
		// c.run("etc/train2.csv","etc/test2.csv", "etc/feature2.csv",
		// m_classifier,
		// "etc/ClassifyResult2.txt");
		// c.run("etc/feature3.csv", "etc/feature3.csv", m_classifier,
		// "etc/ClassifyResult3.txt");
		// c.run("etc/feature4.csv", "etc/feature4.csv", m_classifier,
		// "etc/ClassifyResult4.txt");

	}

}
