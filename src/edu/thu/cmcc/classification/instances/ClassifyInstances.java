package edu.thu.cmcc.classification.instances;

import java.io.File;

import edu.thu.cmcc.classification.ClassifyProperties;
import weka.core.Attribute;
import weka.core.Instance;
import weka.core.Instances;
import weka.core.converters.CSVLoader;
import weka.filters.Filter;
import weka.filters.unsupervised.attribute.NumericToNominal;

public class ClassifyInstances extends InstancesGetter {

	/**
	 * 读取分类feature文件，生成Instances
	 */
	@Override
	public Instances getInstances(String filename) throws Exception {
		NumericToNominal ntn = new NumericToNominal();

		// if (filename.endsWith(".csv")) {
		// filename = FileUtils.csv2arff(filename);
		// }
		// ArffLoader atf = new ArffLoader();
		// atf.setFile(new File(filename));
		// Instances instances = atf.getDataSet(); // 读入训练文件
		CSVLoader csvloader = new CSVLoader();
		csvloader.setFile(new File(filename));
		Instances instances = csvloader.getDataSet();

		ntn.setInputFormat(instances);
		instances = Filter.useFilter(instances, ntn);
		instances.setClassIndex(instances.numAttributes() - 1); // 设置分类属性所在行号（第一行为0号），instancesTest.numAttributes()可以取得属性总数
		return instances;
	}

}
