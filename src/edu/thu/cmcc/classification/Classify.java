package edu.thu.cmcc.classification;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import edu.thu.cmcc.basic.CSVFileIO;
import edu.thu.cmcc.basic.FileManipulator;
import edu.thu.cmcc.classification.instances.ClassifyInstances;
import edu.thu.cmcc.classification.instances.InstancesGetter;
import edu.thu.cmcc.classification.throwable.LowAccuracyException;
import weka.classifiers.Classifier;
import weka.classifiers.Evaluation;
import weka.classifiers.functions.LibSVM;
import weka.core.Attribute;
import weka.core.Instance;
import weka.core.Instances;

public class Classify {

	public static double TRAIN_TEST_RATIO = 2.0; // 训练集数量和测试集数量比

	public List<String> suspicious = null;
	private Classifier m_classifier = null;
	private InstancesGetter insGetter = null;
	private Map<String, String> allSample2Class = new HashMap<String, String>();
	private Instances instancesTrain = null;
	private Instances instancesTest = null;
	private Instances instancesTrainPlusTest = null;
	private Instances instancePredict = null;
	private Evaluation evaluation = null;

	public Classify() {
		insGetter = new ClassifyInstances();
		m_classifier = new LibSVM();
		/*
		 * -S set type of SVM (default 0) 0 = C-SVC 1 = nu-SVC 2 = one-class SVM
		 * 3 = epsilon-SVR 4 = nu-SVR -K set type of kernel function (default 2)
		 * 0 = linear: u'*v 1 = polynomial: (gamma*u'*v + coef0)^degree 2 =
		 * radial basis function: exp(-gamma*|u-v|^2) 3 = sigmoid:
		 * tanh(gamma*u'*v + coef0) -D set degree in kernel function (default 3)
		 * -G set gamma in kernel function (default 1/k) -R set coef0 in kernel
		 * function (default 0) -C set the parameter C of C-SVC, epsilon-SVR,
		 * and nu-SVR (default 1) -N set the parameter nu of nu-SVC, one-class
		 * SVM, and nu-SVR (default 0.5) -Z whether to normalize input data, 0
		 * or 1 (default 0) -P set the epsilon in loss function of epsilon-SVR
		 * (default 0.1) -M set cache memory size in MB (default 40) -E set
		 * tolerance of termination criterion (default 0.001) -H whether to use
		 * the shrinking heuristics, 0 or 1 (default 1) -W set the parameters C
		 * of class i to weight[i]*C, for C-SVC (default 1)
		 */

		String[] options = {// SVM的参数配置
				// "-split-percentage","50",
				"-K", "0", "-S", "0", "-x", "10", "-N", "0", "-M", "100", "-W",
				"1.0 1.0", "-G", "0.5", "-P", "0.8", "-b", "1" };
		try {
			m_classifier.setOptions(options);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public Classify(Classifier c) {
		insGetter = new ClassifyInstances();
		this.m_classifier = c;
	}

	public void initDataset(DatasetGenerator2 dg) {
		this.instancesTrain = dg.getInstancesTrain();
		this.instancesTest = dg.getInstancesTest();
		this.instancesTrainPlusTest = dg.getInstancesTrainPlusTest();
		this.instancePredict = dg.getInstancePredict();
	}

	/**
	 * 从Instances里提取出class信息
	 * 
	 * @param instances
	 * @return
	 */
	public Map<String, String> generateClassMapFromInstances(Instances instances) {
		Map<String, String> map = new HashMap<String, String>();
		String[] labelAttr = InstancesGetter.getIDs(instances);
		Attribute classAttr = instances.classAttribute();
		for (int i = 0; i < instances.numInstances(); i++) {
			Instance ins = instances.instance(i);
			map.put(labelAttr[i], classAttr.value((int) ins.classValue()));
		}
		return map;
	}

	/**
	 * 写结果
	 * 
	 * @param map
	 *            key：文档名 value：分类结果
	 * @param file
	 *            结果文件
	 * @throws IOException
	 */
	public void writeAllClassificationResult(Map<String, String> map,
			String file) throws IOException {

		CSVFileIO csv = new CSVFileIO();
		csv.load(file, true);
		for (Entry pairs : map.entrySet()) {
			csv.update(pairs.getKey().toString(), 1, pairs.getValue()
					.toString());
		}
		csv.write(file, ",", true, true, ClassifyProperties.CLASSIFY_INDEX);
	}

	/**
	 * 
	 * @param map
	 * @param file
	 * @throws IOException
	 */
	public void writeClassificationResult(Map<String, String> map, String file)
			throws IOException {

		CSVFileIO csv = new CSVFileIO();
		csv.load(file, true);
		csv.column("class" + ClassifyProperties.Iteration_ID, map);
		csv.write(file, ",", true, true, ClassifyProperties.CLASSIFY_INDEX);
	}

	/**
	 * 输出测试结果
	 * 
	 * @param evaluatefile
	 * @throws IOException
	 */
	public void writeTestStatisticsToFile(String evaluatefile)
			throws IOException {
		BufferedWriter bw = new BufferedWriter(new FileWriter(evaluatefile));
		double[][] matrix = evaluation.confusionMatrix();
		bw.write("====================\n");
		for (int i = 0; i < matrix.length; i++)
			bw.write(matrix[i][0] + "   " + matrix[i][1] + "\n");
		bw.write("====================\n");
		bw.write(evaluation.toSummaryString("\nResults\n======", false) + "\n");
		bw.close();
	}

	public void writeSuspiciousToFile(String file) throws IOException {
		BufferedWriter bw = new BufferedWriter(new FileWriter(file));
		for (String s : suspicious)
			bw.write(s + "\n");
		bw.close();
	}

	/**
	 * 训练过程
	 * 
	 * @param instancesTrain
	 * @throws Exception
	 */
	public void train(Instances instancesTrain) throws Exception {
		this.instancesTrain = instancesTrain;
		instancesTrain.deleteAttributeAt(0);// 第一列是文档名，删除
		m_classifier.buildClassifier(instancesTrain); // 训练
	}

	/**
	 * 测试过程
	 * 
	 * @param featureFile
	 * @param trainFile
	 * @param testFile
	 * @param testResultFile
	 * @return
	 * @throws Exception
	 */
	public List<Object> test(String trainFile, String testFile,
			String testResultFile) throws Exception {
		instancesTrain = insGetter.getInstances(trainFile);
		instancesTest = insGetter.getInstances(testFile);
		instancesTrainPlusTest = DatasetGenerator2.mergeInstances(
				instancesTrain, instancesTest);
		this.train(instancesTrain);
		return this.test(instancesTest, testResultFile);
	}

	public List<Object> test(String testResultFile) throws Exception {
//		for (int i = 0; i < instancesTrain.numInstances(); i++)// 测试分类结果
//		{
//			Instance ins = instancesTrain.instance(i);
//			System.out.println(ins.stringValue(0)+","+ins.stringValue(ins.classIndex()));
//		}
		this.train(instancesTrain);
		return this.test(instancesTest, testResultFile);
	}

	/**
	 * 测试过程
	 * 
	 * @param instancesTest
	 * @param testFile
	 * @return
	 * @throws Exception
	 */
	public List<Object> test(Instances instancesTest, String testResultFile)
			throws Exception {
		this.instancesTest = instancesTest;
		double sum = instancesTest.numInstances(), // 实例数
		right = 0.0f;
		String[] testLabels = InstancesGetter.getIDs(instancesTest);
		instancesTest.deleteAttributeAt(0);

		Map<String, String> resultMap = new LinkedHashMap<String, String>();// 分类结果map
		// label to result class
		double precision = 0;
		int wrong = 0;
		Attribute testClassAttr = instancesTest.classAttribute();
		StringBuilder wrongInfo = new StringBuilder();
		for (int i = 0; i < sum; i++)// 测试分类结果
		{
			Instance testInstance = instancesTest.instance(i);
			int result = (int) m_classifier.classifyInstance(testInstance);
			if (instancesTest.classAttribute().numValues() < 2)
				System.out.println(instancesTest.classAttribute().toString());
			String resultString = testClassAttr.value(result);
			resultMap.put(testLabels[i], resultString);
			if (result == instancesTest.instance(i).classValue())// 如果预测值和答案值相等
			{
				right++;// 正确值加1
			} else {
				wrong++;
				// 输出分类错误样本
				wrongInfo.append(testLabels[i]
						+ " "
						+ instancesTest.instance(i).toString(
								instancesTest.numAttributes() - 1) + "->"
						+ resultString + ";\n");
			}
		}
		precision = right / sum;
		System.out.println("Classification precision:" + precision);
		System.out.println("Wrong number:" + wrong);
		FileManipulator.outputOneToOne(resultMap, testResultFile, ",", 0);

		// =============== Evaluation output =====================
		evaluation = new Evaluation(instancesTrain);
		evaluation.evaluateModel(m_classifier, instancesTest);
		System.out.println("Correct number:" + evaluation.correct());
		double[][] matrix = evaluation.confusionMatrix();
		System.out.println("====================");
		for (int i = 0; i < matrix.length; i++)
			System.out.println(matrix[i][0] + " " + matrix[i][1]);
		System.out.println("====================");
		System.out.println(evaluation.toSummaryString("\nResults\n======",
				false));
		// =============== Evaluation output =====================

		List<Object> statistics = new LinkedList<Object>();// 输出各种数据结果
		statistics.add(precision);
		statistics.add(wrong);
		statistics.add(wrongInfo.toString());
		if (precision < ClassifyProperties.LOWEST_ACCURACY) {
			System.out.println(statistics.toString());
			throw new LowAccuracyException("Low Precision");
		}
		System.out.println("Train: " + instancesTrain.numInstances()
				+ "; Test: " + instancesTest.numInstances());
		statistics.add(0, instancesTrain.numInstances());
		statistics.add(1, instancesTest.numInstances());
		return statistics;
	}

	public List<Object> classify(String resultfile) throws Exception {
		return this.classify(instancesTrainPlusTest, instancePredict,
				resultfile);
	}

	/**
	 * 分类过程，这部分主要是进行一些预处理
	 * 
	 * @param trainFile
	 *            训练集
	 * @param unlabeledfile
	 *            待分类
	 * @param resultfile
	 *            结果文件
	 * @param suspiciousfile
	 *            进入下次迭代的文件
	 * @return
	 * @throws Exception
	 */
	public List<Object> classify(String trainFile, String predictfile,
			String resultfile) throws Exception {
		return this.classify(insGetter.getInstances(trainFile),
				insGetter.getInstances(predictfile), resultfile);
	}

	public List<Object> classify(Instances trainInstances,
			Instances predictInstances, String resultfile) throws Exception {

		this.instancesTrainPlusTest = trainInstances;
		this.instancePredict = predictInstances;

		List<Object> statistics = this.classify(this.instancePredict,
				resultfile);
		return statistics;
	}

	/**
	 * 分类过程
	 * 
	 * @param instances
	 *            待分类实例
	 * @param classAttribute
	 *            class属性
	 * @param resultfile
	 *            结果文件
	 * @return
	 * @throws Exception
	 */
	public List<Object> classify(Instances instances, String resultfile)
			throws Exception {

		suspicious = new ArrayList<String>();
		// 先把训练集中的others类别放入下一次迭代list
		for (int i = 0; i < this.instancesTrainPlusTest.numInstances(); i++) {
			Instance ins = this.instancesTrainPlusTest.instance(i);
			if (ins.classAttribute().value((int) ins.classValue())
					.equals(ClassifyProperties.OTHER_CLASS))
				suspicious.add(ins.stringValue(0));
		}

		// train的时候已经把第一列sample删除了，因此要先提取sample和class关系
		Attribute classAttribute = this.instancesTrainPlusTest.classAttribute();
		Map<String, String> labeledClass = generateClassMapFromInstances(this.instancesTrainPlusTest);

		this.train(this.instancesTrainPlusTest);// 训练获得分类器

		String[] labelAttr = InstancesGetter.getIDs(instances);
		instances.deleteAttributeAt(0);// 第一列是文档名，删除
		Map<String, String> resultMap = new LinkedHashMap<String, String>();
		int rightCount = 0;
		int sumCount = 0;
		StringBuilder wrongInfoBuilder = new StringBuilder();
		for (int i = 0; i < instances.numInstances(); i++) {
			int result = 0;
			Instance instance = instances.instance(i);
			result = (int) this.m_classifier.classifyInstance(instance);
			String resultString = classAttribute.value(result);
			resultMap.put(labelAttr[i], resultString);

			if (resultString.equals(ClassifyProperties.OTHER_CLASS))
				suspicious.add(labelAttr[i]);
			else {
				sumCount++;
				if (resultString.equals(instances.instance(i).classAttribute()
						.name())) {
					rightCount++;
				} else {
					wrongInfoBuilder.append(labelAttr[i]
							+ "("
							+ instances.instance(i).toString(
									instances.numAttributes() - 1) + "->"
							+ resultString + ");");
					// System.out.println(labelAttr.value(i)
					// + " ours:"
					// + resultString
					// + ": true: "
					// + instances.instance(i).toString(
					// instances.numAttributes() - 1));
				}
			}
		}

		// 统计各个文件数据量并输出
		List<Object> statistics = new LinkedList<Object>();
		statistics.add(sumCount);// 所有分出来的正例
		statistics.add(instances.numInstances());// left数量
		statistics.add(suspicious.size());// 进入下一迭代
		statistics.add(sumCount - rightCount);// 错误数量
		statistics.add(wrongInfoBuilder.toString());
		StringBuilder classAttrBuilder = new StringBuilder();
		for (int i = 0; i < classAttribute.numValues(); i++) {
			classAttrBuilder.append(classAttribute.value(i).toString() + ";");
		}
		statistics.add(classAttrBuilder.toString());
		System.out.println(classAttribute + ":" + sumCount + ";wrong:"
				+ (sumCount - rightCount) + ";suspicious:" + suspicious.size());

		// allSample2Class = FileManipulator.loadOneToOne(resultfile, ",", 0,
		// ClassifyProperties.ALL_CLASS_INDEX);// 结果文件原来的分类数据
		allSample2Class = new HashMap<String, String>(labeledClass);

		// allSample2Class.putAll(labeledClass);
		allSample2Class.putAll(resultMap);// 本次迭代结果加入最终结果

		// for(String key: resultMap.keySet())
		// System.out.println(key+":"+resultMap.get(key));

		writeClassificationResult(allSample2Class, resultfile);
		// writeToMongo(allSample2Class);
		return statistics;

	}

	public static void main(String[] args) throws Exception {
		Classify c = new Classify();

		c.test("etc/train1_f1.csv", "etc/test1_f1.csv",
				"etc/ClassifyResult1_f1.txt");

	}

}
