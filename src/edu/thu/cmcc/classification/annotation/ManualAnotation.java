package edu.thu.cmcc.classification.annotation;

import java.io.IOException;
import java.util.Iterator;
import java.util.Map;
import java.util.Map.Entry;

import edu.thu.cmcc.basic.FileManipulator;
import edu.thu.cmcc.classification.ClassifyProperties;

/**
 * @author Miyayx 人工标注生成标注数据集 最终返回标注数据map，key是文档id，value是class
 */
public class ManualAnotation implements Annotation {

	@Override
	public Map<String, String> annotation(String clusterfile)
			throws IOException {
		return this.annotation(clusterfile, 2);

	}

	@Override
	public Map<String, String> annotation(String annotationfile, int clusterIndex)
			throws IOException {
		Map<String, String> s2c = FileManipulator.loadOneToOne(annotationfile,
				",", 0, clusterIndex + 1);// flagIndex = clusterIndex+1

		for (Iterator<Map.Entry<String, String>> it = s2c.entrySet().iterator(); it
				.hasNext();) {
			Map.Entry<String, String> entry = it.next();
			if (entry.getValue().length() == 0) {
				it.remove();
			}
		}
		return s2c;
	}

}
