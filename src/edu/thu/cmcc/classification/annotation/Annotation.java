package edu.thu.cmcc.classification.annotation;

import java.io.IOException;
import java.util.Map;

import edu.thu.cmcc.classification.ClassifyProperties;

public interface Annotation {
	
	static int classNumber = ClassifyProperties.CLASS_NUMBER; // 分类数量
	// 二分类设为1，三分类设为2
	static double instanceRatio   = ClassifyProperties.INSTANCE_RATIO;
	static int minClass1SizeLimit = 20;
	
	public Map<String,String> annotation(String annotationfile)throws IOException;
	
	public Map<String,String> annotation(String annotationfile,int clusterIndex)throws IOException;

}
