package edu.thu.cmcc.classification.annotation;

import java.io.IOException;
import java.util.Map;

import edu.thu.cmcc.classification.ClassifyProperties;

public interface Annotation {
	
	static int classNumber = ClassifyProperties.CLASS_NUMBER; // 分类数量
	// 二分类设为1，三分类设为2
	static double class0SizePercent = ClassifyProperties.NEG_POSITIVE_RATIO; // 负例/正例
	static double class1SizePercent = ClassifyProperties.POSITIVE_ALL_RATIO; // 正例/全部
	static int minClass1SizeLimit = 20;
	
	public Map<String,String> annotation(String clusterfile)throws IOException;
	
	public Map<String,String> annotation(String clusterfile,int clusterIndex)throws IOException;

}
