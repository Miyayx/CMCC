package edu.thu.cmcc.classification;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;

import weka.core.Attribute;
import weka.core.FastVector;
import weka.core.Instance;
import weka.core.Instances;
import weka.core.converters.CSVSaver;
import weka.filters.Filter;
import weka.filters.unsupervised.attribute.NominalToString;
import weka.filters.unsupervised.attribute.NumericToNominal;
import edu.thu.cmcc.basic.CSVFileIO;
import edu.thu.cmcc.classification.annotation.Annotation;
import edu.thu.cmcc.classification.instances.ClassifyInstances;
import edu.thu.cmcc.classification.instances.ClusterInstances;
import edu.thu.cmcc.classification.instances.InstancesGetter;

/**
 * 
 * @author Miyayx 给数据加上类别 原AddClass.java
 */
public class DatasetGenerator2 {

	public static double TRAIN_TEST_RATIO = 2.0; // 训练集数量和测试集数量比
	private Annotation annotation = null;

	private Instances instancesTrain = null;
	private Instances instancesTest = null;
	private Instances instancesTrainPlusTest = null;
	private Instances instancePredict = null;

	public DatasetGenerator2(Annotation ann) {
		this.annotation = ann;
	}

	public Instances getInstancesTrain() {
		return instancesTrain;
	}

	public Instances getInstancesTest() {
		return instancesTest;
	}

	public Instances getInstancesTrainPlusTest() {
		return instancesTrainPlusTest;
	}

	public Instances getInstancePredict() {
		return instancePredict;
	}
    
	/**
	 * 合并两个Instances，即ins1个数+ins2个数
	 * @param ins1
	 * @param ins2
	 * @return
	 */
	public static Instances mergeInstances(Instances ins1, Instances ins2) {
		Instances allInstances = new Instances(ins1);
		for (Enumeration e = ins2.enumerateInstances(); e.hasMoreElements();)
			allInstances.add((Instance) e.nextElement());
		return allInstances;
	}

	/**
	 * 生成各种数据集，包括train，test，待分类left，所有标注数据trainplustest
	 * 
	 * @param s2c
	 *            sample to class
	 * @param featurefile 含有feature的文件
	 *            
	 * @param ratio
	 *            TRAIN_TEST_RATIO
	 * @param leftfile
	 *            left文件名
	 * @param trainfile
	 *            train文件名
	 * @param testfile
	 *            test文件名
	 * @throws IOException
	 */
	public void generateClassificationDatasets(Map<String, String> s2c,
			String featurefile, double ratio, String leftfile,
			String trainfile, String testfile) throws Exception {

		double trainRatio = ratio / (ratio + 1);

		Instances instances = new ClusterInstances().getInstances(featurefile,
				0, 1, ClassifyProperties.FEATURE_COUNT,
				ClassifyProperties.FILTER_INDEX);
		
		//这样写保证Class列是Nominal类型的数据
		FastVector fv = new FastVector();
		for (String c : new HashSet<String>(s2c.values()))
			fv.addElement(c);

		//添加class列
		Attribute classAttr = new Attribute("class", fv);
		instances.insertAttributeAt(classAttr, instances.numAttributes());
		instances.setClassIndex(instances.numAttributes() - 1);

		String[] labelAttr = InstancesGetter.getIDs(instances);

		instancesTrain = new Instances(instances, 0);
		instancesTest = new Instances(instances, 0);
		instancePredict = new Instances(instances, 0);
		
		Map<String, String> trainSet = new HashMap<String, String>();
		Map<String, String> testSet = new HashMap<String, String>();
		List<String> predictSet     = new ArrayList<String>();
		
		// 一下的map都是 key:类别 value:属于此类别的文档list
		Map<String, Instances> labeledConceptInstanceMap = new HashMap<String, Instances>();

		for (int i = 0; i < instances.numInstances(); i++) {
			Instance ins = instances.instance(i);
			String s = labelAttr[i];// label
			if (s2c.containsKey(s)) {
				String c = s2c.get(s);
				ins.setClassValue(c);
				Instances instanceSet = labeledConceptInstanceMap.get(c);
				if (instanceSet == null)
					instanceSet = new Instances(instances, 0);
				instanceSet.add(ins);
				labeledConceptInstanceMap.put(c, instanceSet);
			} else{
				instancePredict.add(ins);
				predictSet.add(s);
			}
		}

		// 对每种类别，将其按比例分割成训练集与测试集
		for (String concept : labeledConceptInstanceMap.keySet()) {
			Instances instanceSet = new Instances(
					labeledConceptInstanceMap.get(concept));
			Set<Integer> indexSet = new HashSet<Integer>();
			int size = instanceSet.numInstances();
			Random rdm = new Random();
			while (indexSet.size() < trainRatio * size) {
				int index = Math.abs(rdm.nextInt() % size);
				if (indexSet.contains(index))
					continue;
				indexSet.add(index);
			}
			for (int i = 0; i < size; i++) {
				Instance instance = instanceSet.instance(i);
				if (indexSet.contains(i)) {
					instancesTrain.add(instance);
					instance.attribute(0).toString();
				} else {
					instancesTest.add(instance);
					instance.attribute(0).toString();
				}
			}
		}

		instancesTrainPlusTest = mergeInstances(instancesTrain, instancesTest);
		outputWithClass(instancesTrain, trainfile); 
		outputWithClass(instancesTest, testfile);  
		output(instancePredict, leftfile);

		// instancesTest.setClassIndex(instancesTest.numAttributes()-1);
		// instancesTrain.setClassIndex(instancesTrain.numAttributes()-1);
		instancesTrainPlusTest.setClassIndex(instancesTrainPlusTest
				.numAttributes() - 1);

	}

	/**
	 * 输出带有feature数值与class信息的文件
	 * @param instances
	 * @param outfile
	 * @throws IOException
	 */
	public void outputFeatureWithClass(Instances instances, String outfile)
			throws IOException {

		CSVSaver saver = new CSVSaver();
		saver.setInstances(instances);
		saver.setFile(new File(outfile));
		saver.writeBatch();

	}

	/**
	 * 输出仅有class信息的文件
	 * @param instances
	 * @param outfile
	 * @throws IOException
	 */
	public void outputWithClass(Instances instances, String outfile)
			throws IOException {
		BufferedWriter out = new BufferedWriter(new FileWriter(outfile));
		Attribute classAttr = instances.classAttribute();
		for (int i = 0; i < instances.numInstances(); i++) {
			Instance ins = instances.instance(i);
			out.write(ins.stringValue(0) + "," + classAttr.value((int)ins.classValue())+"\n");
			out.flush();
		}
		out.close();
	}

	/**
	 * 仅输出id
	 * @param instances
	 * @param outfile
	 * @throws IOException
	 */
	public void output(Instances instances, String outfile) throws IOException {
		BufferedWriter out = new BufferedWriter(new FileWriter(outfile));
		for (int i = 0; i < instances.numInstances(); i++) {
			Instance ins = instances.instance(i);
			out.write(ins.stringValue(0) + "\n");
			out.flush();
		}
		out.close();
	}

	/**
	 * 迭代自动运行时使用
	 * 
	 * @param classfile
	 * @param featurefile
	 * @param samplefile
	 * @param leftfile
	 * @param trainfile
	 * @param testfile
	 * @param trainPlusTestfile
	 * @throws IOException
	 */
	public void run(String clusterfile, String featurefile, String leftfile,
			String trainfile, String testfile, String trainPlusTestfile)
			throws Exception {

		Map<String, String> s2c = annotation.annotation(clusterfile);
		// ================ write annotation result to file =================
		this.writeAnnotationResultToFile(clusterfile, s2c);

		generateClassificationDatasets(s2c, featurefile, TRAIN_TEST_RATIO,
				leftfile, trainfile, testfile);
	}

	private void writeAnnotationResultToFile(String file,
			Map<String, String> map) throws IOException {
		CSVFileIO csv = new CSVFileIO();
		csv.load(file, true);
		csv.column("flag" + ClassifyProperties.Iteration_ID, map);
		csv.write(file, "", true,true,ClassifyProperties.FLAG_INDEX);
	}

}
