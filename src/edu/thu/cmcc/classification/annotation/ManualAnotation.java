package edu.thu.cmcc.classification.annotation;

import java.io.IOException;
import java.util.Map;

import edu.thu.cmcc.basic.FileManipulator;

/**
 * @author Miyayx
 * 人工标注生成标注数据集
 * 最终返回标注数据map，key是文档id，value是class
 */
public class ManualAnotation implements Annotation{

	@Override
	public Map<String, String> annotation(String clusterfile)
			throws IOException {
		return this.annotation(clusterfile, 2);
		
	}

	@Override
	public Map<String, String> annotation(String clusterfile, int clusterIndex)
			throws IOException {
		Map<String, String> s2c = FileManipulator.loadOneToOne(clusterfile,
				",", 0, clusterIndex);
		return s2c;
	}

}
