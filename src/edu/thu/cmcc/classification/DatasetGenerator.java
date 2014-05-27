package edu.thu.cmcc.classification;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;

import edu.thu.cmcc.basic.FileManipulator;
import edu.thu.cmcc.basic.FileUtils;
import edu.thu.cmcc.classification.annotation.Annotation;

/**
 * 
 * @author Miyayx 给数据加上类别
 * 原AddClass.java
 */
public class DatasetGenerator {

	public static double TRAIN_TEST_RATIO = 2.0; // 训练集数量和测试集数量比
	private Annotation annotation = null;

	public DatasetGenerator(Annotation ann) {
		this.annotation = ann;
	}

	/**
	 * 读取feature文件
	 * 
	 * @param file
	 * @return
	 */
	public Map<String, String> readFeatureFile(String file) {
		Map<String, String> sample2feature = new HashMap<String, String>();

		List<String> lines = FileUtils.readFileByLines(file);
		lines.remove(0);// 第一行是列名，删除
		for (String line : lines) {
			String[] ls = line.trim().split(",", 2);
			sample2feature.put(ls[0], ls[1]);
		}
		return sample2feature;
	}

	public String getColnames(String file) {
		return FileUtils.readFileByLines(file).get(0);
	}

	/**
	 * 生成各种数据集，包括train，test，待分类left，所有标注数据trainplustest
	 * 
	 * @param s2c
	 *            sample to class
	 * @param s2f
	 *            sample to feature
	 * @param ratio
	 *            TRAIN_TEST_RATIO
	 * @param colname
	 *            列名，格式：sample,feature1,feature2,...（只是拿来写文件用）
	 * @param samplefile
	 *            进入本次迭代的文档列表文件名
	 * @param leftfile
	 *            left文件名
	 * @param trainfile
	 *            train文件名
	 * @param testfile
	 *            test文件名
	 * @param trainPlusTestfile
	 *            train+test(所有标注数据)文件名
	 * @throws IOException
	 */
	public void generateClassificationDatasets(Map<String, String> s2c,
			Map<String, String> s2f, double ratio, String colname,
			String samplefile, String leftfile, String trainfile,
			String testfile, String trainPlusTestfile) throws IOException {

		double trainRatio = ratio / (ratio + 1);
		// 一下的map都是 key:类别 value:属于此类别的文档list
		Map<String, Set<String>> labeledConceptInstanceMap = new HashMap<String, Set<String>>();
		Map<String, Set<String>> trainPlusTest = new HashMap<String, Set<String>>();
		Map<String, Set<String>> train = new HashMap<String, Set<String>>();
		Map<String, Set<String>> test = new HashMap<String, Set<String>>();
		Map<String, Set<String>> left = new HashMap<String, Set<String>>();

		Map<String, Set<String>> taxonomy = FileManipulator.loadOneToMany(
				"etc/ontology2.txt", "\t\t", ";;;");// 人工标注的数据集
		Set<String> allInstanceSet = FileManipulator.loadOneColum(samplefile,
				"", -1);// 本次迭代的所有文档list
		Set<String> leftSet = new HashSet<String>(allInstanceSet);
		colname = colname.trim() + ",class\n";// 原文件最后一列是没有类别的，现在加一列类别

		// 已标记数据的class to sample list map
		for (String instance : s2c.keySet()) {
			String concept = s2c.get(instance);
			Set<String> instanceSet = labeledConceptInstanceMap.get(concept);
			if (instanceSet == null)
				instanceSet = new HashSet<String>();
			instanceSet.add(instance);
			labeledConceptInstanceMap.put(concept, instanceSet);
		}

		// 对每种类别，将其按比例分割成训练集与测试集
		for (String concept : labeledConceptInstanceMap.keySet()) {
			List<String> list = new LinkedList<String>(
					labeledConceptInstanceMap.get(concept));
			Set<Integer> indexSet = new HashSet<Integer>();
			Random rdm = new Random();
			while (indexSet.size() < trainRatio * list.size()) {
				int index = Math.abs(rdm.nextInt() % list.size());
				if (indexSet.contains(index))
					continue;
				indexSet.add(index);
			}
			Set<String> trainSet = new HashSet<String>();
			Set<String> testSet = new HashSet<String>();
			Set<String> trainPlusTestSet = new HashSet<String>();
			for (int i = 0; i < list.size(); i++) {
				String instance = list.get(i);
				trainPlusTestSet.add(instance);
				if (indexSet.contains(i)) {
					trainSet.add(instance);
				} else {
					testSet.add(instance);
				}
			}
			test.put(concept, testSet);
			train.put(concept, trainSet);
			trainPlusTest.put(concept, trainPlusTestSet);
			leftSet.removeAll(trainPlusTestSet);
		}

		// 自 动运行时才用，把剩下的待分类数据根据人工标记赋类。
		 for (String concept : taxonomy.keySet()) {
		 Set<String> set = new HashSet<String>();
		 for (String instance : taxonomy.get(concept)) {
		 // if (!labeledConceptInstanceMap.containsKey(instance)) {
		 // if (!allInstanceSet.contains(instance))
		 // continue;
		 if(leftSet.contains(instance)){
		 set.add(instance);
		 }
		 }
		 if (set.size() > 0) {
		 left.put(concept, set);
		 }
		 }

		// leftSet.removeAll(labeledConceptInstanceMap.values());
		// 把剩下的待分类数据全归为left类别
		//left.put("left", leftSet);

		// System.out.println("Train length: " + countMapValues(train));
		// System.out.println("Test length: " + countMapValues(test));
		// System.out.println("All length: " + countMapValues(trainPlusTest));
		// // System.out.println("Left length: " + countMapValues(left));

		// 输出
		outputFeatureWithClass(s2f, trainfile, colname, train);// train.csv
		outputFeatureWithClass(s2f, testfile, colname, test);// test.csv
		outputFeatureWithClass(s2f, trainPlusTestfile, colname, trainPlusTest);// classify.csv
		outputFeatureWithClass(s2f, leftfile, colname, left);// left.csv
	}

	@SuppressWarnings("unchecked")
	public int countMapValues(Map<String, Set<String>> map) {
		Iterator it = map.entrySet().iterator();
		int count = 0;
		while (it.hasNext()) {
			Map.Entry e = (Map.Entry) it.next();
			int num = ((Set<String>) e.getValue()).size();
			// System.out.println(e.getKey() + ":" + num);
			count += num;
		}
		return count;
	}

	public void outputFeatureWithClass(Map<String, String> s2f, String outfile,
			String colname, Map<String, Set<String>> conceptInstanceMap)
			throws IOException {
		BufferedWriter out = new BufferedWriter(new FileWriter(outfile));
		out.write(colname + "\n");
		for (String concept : conceptInstanceMap.keySet()) {
			for (String instance : conceptInstanceMap.get(concept)) {
				if (s2f.get(instance) != null) {
					out.write(instance + "," + s2f.get(instance) + ","
							+ concept + "\n");
					out.flush();
				}
			}
		}
		out.close();
	}

	/**
	 * 迭代自动运行时使用
	 * 
	 * @param classfile
	 * @param featurefile
	 * @param samplefile
	 * @param leftfile
	 * @param trainfile
	 * @param testfile
	 * @param trainPlusTestfile
	 * @throws IOException
	 */
	public void run(String clusterfile, String featurefile, String samplefile,
			String leftfile, String trainfile, String testfile,
			String trainPlusTestfile) throws IOException {

		Map<String, String> s2c = annotation.annotation(clusterfile);
		Map<String, String> s2f = readFeatureFile(featurefile);
		String colname = getColnames(featurefile);
		generateClassificationDatasets(s2c, s2f, TRAIN_TEST_RATIO, colname,
				samplefile, leftfile, trainfile, testfile, trainPlusTestfile);
	}

}
