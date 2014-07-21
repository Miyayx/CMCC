package edu.thu.cmcc.classification.annotation;

import java.io.IOException;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;

import edu.thu.cmcc.basic.FileManipulator;
import edu.thu.cmcc.classification.ClassifyProperties;

/**
 * @author Miyayx 人工标注生成标注数据集 最终返回标注数据map，key是文档id，value是class
 */
public class ManualAllAnotation implements Annotation {

	@Override
	public Map<String, String> annotation(String clusterfile)
			throws IOException {
		return this.annotation(clusterfile, 0);

	}

	@Override
	public Map<String, String> annotation(String annotationfile,
			int clusterIndex) throws IOException {
		Map<String, String> s2c = FileManipulator.loadOneToOne(annotationfile,
				",", 0, clusterIndex + 1);// flagIndex = clusterIndex+1

		for (Iterator<Map.Entry<String, String>> it = s2c.entrySet().iterator(); it
				.hasNext();) {
			Map.Entry<String, String> entry = it.next();
			if (entry.getValue().length() == 0) {
				it.remove();
			} else if (ClassifyProperties.POS_CLASS.length() > 0) {
				if (!entry.getValue().equals(ClassifyProperties.POS_CLASS)) {
					entry.setValue(ClassifyProperties.OTHER_CLASS);
				}
			}
		}

		// 得到cluster和instance的对应
		Map<String, Set<String>> clusterInstanceMap = new HashMap<String, Set<String>>();
		for (String instance : s2c.keySet()) {
			String cluster = s2c.get(instance);
			Set<String> instanceSet = clusterInstanceMap.get(cluster);
			if (instanceSet == null) {
				instanceSet = new HashSet<String>();
			}
			instanceSet.add(instance);
			clusterInstanceMap.put(cluster, instanceSet);
		}

		// 正例集合
		List<String> bestCluster = new LinkedList<String>(
				clusterInstanceMap.get(ClassifyProperties.POS_CLASS));

		// 负例集合
		List<String> otherCluster = new LinkedList<String>(
				clusterInstanceMap.get(ClassifyProperties.OTHER_CLASS));

		// 随机排列
		long seed = System.nanoTime();
		Collections.shuffle(bestCluster, new Random(seed));
		Collections.shuffle(otherCluster, new Random(seed));

		// 取正例标注数据
		double posSizeLimit = bestCluster.size() * instanceRatio;
		if (posSizeLimit < minClass1SizeLimit)
			posSizeLimit = minClass1SizeLimit;// 至少要标20个

		s2c.clear();

		int labelSize = 0;
		for (String instance : bestCluster) {
			s2c.put(instance, ClassifyProperties.POS_CLASS);
			labelSize++;
			if (labelSize > posSizeLimit)
				break;
		}

		// 取负例标注数据
		labelSize = 0;
		double negSizeLimit = otherCluster.size() * instanceRatio;
		for (String instance : otherCluster) {
			s2c.put(instance, ClassifyProperties.OTHER_CLASS);
			labelSize++;
			if (labelSize > negSizeLimit)
				break;
		}

		return s2c;
	}

}
