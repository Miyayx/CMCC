package edu.thu.cmcc.classification.annotation;

public class AnnotationType {
	
	public static final int MANUAL_ANOTATION = 0;//人工标注
	public static final int AUTO_ANOTATION = 1;  //程序选择最大簇为最优聚类，随机选择样本自动标注
	public static final int FILTER_ANOTATION = 2;//之前人工标注过一些文件，从中筛选出标注数据集

}
