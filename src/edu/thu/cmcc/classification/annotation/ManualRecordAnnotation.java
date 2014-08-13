package edu.thu.cmcc.classification.annotation;

import java.io.IOException;
import java.util.Collections;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;

import edu.thu.cmcc.basic.FileManipulator;
import edu.thu.cmcc.classification.ClassifyProperties;

public class ManualRecordAnnotation implements Annotation {

	@Override
	public Map<String, String> annotation(String clusterfile)
			throws IOException {
		return this.annotation(clusterfile, 0);
	}

	@Override
	public Map<String, String> annotation(String clusterfile, int clusterIndex)
			throws IOException {

		Map<String, String> s2c = FileManipulator.loadOneToOne(clusterfile,
				",", 0, clusterIndex);//sample to cluster
		Map<String, String> s2a = FileManipulator.loadOneToOne(ClassifyProperties.ANNOTATION_FILE,
				",", 0,1);//sample to 标注的类

		Set<String> posClusters = new HashSet<String>(); //正例所屬的簇号

		for (Iterator<Map.Entry<String, String>> it = s2a.entrySet().iterator(); it
				.hasNext();) {
			Map.Entry<String, String> entry = it.next();
			if (!entry.getValue().equals(ClassifyProperties.POS_CLASS)) {
				it.remove();//不是指定的类，从map中删除，最后只留下指定正例的标注map
			} else{
				if(s2c.containsKey(entry.getKey()))
					posClusters.add(s2c.get(entry.getKey()));//是指定的类，取其在本次聚类中所处的簇号
			}
		}

		// 负例集合
		List<String> otherCluster = new LinkedList<String>();

		for (Iterator<Map.Entry<String, String>> it = s2c.entrySet().iterator(); it
				.hasNext();) {
			Map.Entry<String, String> entry = it.next();
			if (!posClusters.contains(entry.getValue()))
				otherCluster.add(entry.getKey());//所有不在正例簇的簇都是负例簇，负例簇里的样本都是负例
		}

		//负例取30%，正例因为人工标注了30%所以不用再筛选了
		// 随机排列
		long seed = System.nanoTime();
		Collections.shuffle(otherCluster, new Random(seed));

		// 取负例标注数据
		int labelSize = 0;
		double negSizeLimit = otherCluster.size() * instanceRatio;
		for (String instance : otherCluster) {
			s2a.put(instance, ClassifyProperties.OTHER_CLASS);
			labelSize++;
			if (labelSize > negSizeLimit)
				break;
		}

		return s2a;
	}

}
