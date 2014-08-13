package edu.thu.cmcc.classification.instances;

import java.io.File;

import org.bson.types.Binary;

import edu.thu.cmcc.basic.FileUtils;
import edu.thu.cmcc.classification.ClassifyProperties;
import weka.core.Attribute;
import weka.core.Instance;
import weka.core.Instances;
import weka.core.converters.ArffLoader;
import weka.core.converters.CSVLoader;
import weka.filters.Filter;
import weka.filters.unsupervised.attribute.NominalToBinary;
import weka.filters.unsupervised.attribute.NumericToBinary;
import weka.filters.unsupervised.attribute.NumericToNominal;
import weka.filters.unsupervised.attribute.Remove;

public class ClusterInstances extends InstancesGetter {

	/**
	 * 读取聚类feature文件，生成Instances
	 */
	@Override
	public Instances getInstances(String filename) throws Exception {
		//NumericToNominal ntn = new NumericToNominal();
		//NumericToBinary ntn = new NumericToBinary();

//		 if (filename.endsWith(".csv")) {
//		 filename = FileUtils.csv2arff(filename);
//		 }
//		 ArffLoader atf = new ArffLoader();
//		 atf.setFile(new File(filename));
//		 Instances instances = atf.getDataSet(); // 读入训练文件
		 
		CSVLoader csvloader = new CSVLoader();
		csvloader.setFile(new File(filename));
		Instances instances = csvloader.getDataSet();

		//ntn.setInputFormat(instances);
		//instances = Filter.useFilter(instances, ntn);
		return instances;
	}

}
