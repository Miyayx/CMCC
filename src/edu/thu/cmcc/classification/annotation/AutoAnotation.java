package edu.thu.cmcc.classification.annotation;

import java.io.IOException;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;

import edu.thu.cmcc.basic.CSVFileIO;
import edu.thu.cmcc.basic.FileManipulator;
import edu.thu.cmcc.classification.ClassifyProperties;

/**
 * 
 * @author Miyayx 程序选择最大簇为最优聚类，随机选择样本自动标注 最终返回标注数据map，key是文档id，value是class
 */
public class AutoAnotation implements Annotation {

	@Override
	public Map<String, String> annotation(String clusterfile, int clusterIndex)
			throws IOException {
		Map<String, String> labeledInstanceSet = new HashMap<String, String>();
		Map<String, String> instanceClusterMap = FileManipulator.loadOneToOne(
				clusterfile, ",", 0, clusterIndex);

		// 得到cluster和instance的对应
		Map<String, Set<String>> clusterInstanceMap = new HashMap<String, Set<String>>();
		for (String instance : instanceClusterMap.keySet()) {
			String cluster = instanceClusterMap.get(instance);
			Set<String> instanceSet = clusterInstanceMap.get(cluster);
			if (instanceSet == null) {
				instanceSet = new HashSet<String>();
			}
			instanceSet.add(instance);
			clusterInstanceMap.put(cluster, instanceSet);
		}

		String positiveCluster = ""; // 最大簇的簇号
		int size = 0;

		if (ClassifyProperties.POSITIVE_CLUSTER == -1) {
			// 如果没指定正例簇号， 选取最大簇为正例簇
			for (String key : clusterInstanceMap.keySet()) {
				int s = clusterInstanceMap.get(key).size();
				if (s > size) {
					size = s;
					positiveCluster = key;
				}
			}
		} else {
			//如果指定了正例簇号
			positiveCluster = String
					.valueOf(ClassifyProperties.POSITIVE_CLUSTER);
			size = clusterInstanceMap.get(positiveCluster).size();
		}

		double class1SizeLimit = size * class1SizePercent;
		if (class1SizeLimit < minClass1SizeLimit)
			class1SizeLimit = minClass1SizeLimit;// 至少要标20个

		// 正例集合
		List<String> bestCluster = new LinkedList<String>(
				clusterInstanceMap.get(positiveCluster));
		clusterInstanceMap.remove(positiveCluster);

		// 负例集合
		List<String> otherCluster = new LinkedList<String>();
		for (Set<String> set : clusterInstanceMap.values())
			otherCluster.addAll(set);

		// 随机排列
		long seed = System.nanoTime();
		Collections.shuffle(bestCluster, new Random(seed));
		Collections.shuffle(otherCluster, new Random(seed));

		// 取正例标注数据
		int labelSize = 0;
		for (String instance : bestCluster) {
			labeledInstanceSet.put(instance, positiveCluster);
			labelSize++;
			if (labelSize > class1SizeLimit)
				break;
		}

		// 取负例标注数据
		labelSize = 0;
		double class0SizeLimit = class0SizePercent * class1SizeLimit;
		for (String instance : otherCluster) {
			labeledInstanceSet.put(instance, ClassifyProperties.OTHER_CLASS);
			labelSize++;
			if (labelSize > class0SizeLimit)
				break;
		}

		return labeledInstanceSet;

	}

	@Override
	public Map<String, String> annotation(String clusterfile)
			throws IOException {

		return this.annotation(clusterfile, 1);
	}

}
