package edu.thu.cmcc.classification;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import edu.thu.cmcc.basic.CSVFileIO;
import edu.thu.cmcc.basic.FileUtils;
import edu.thu.cmcc.classification.annotation.AnnotationFactory;
import edu.thu.cmcc.classification.annotation.AnnotationType;

public class Iteration {

	static String featurefile = null;
	static String clusterResult = null;
	static String samplefile = null;
	static String leftfile = null;
	static String trainfile = null;
	static String testfile = null;
	static String trainPlusTest = null;
	static String suspicious = null;
	static String classifyTestResult = null;
	static String classifyResult = null;
	static String statisticsResult = null;

	private static int iterend;// 迭代在第几次停止

	public static void run(String[] args) {

		long startTime = System.currentTimeMillis(); // 获取开始时间
		long endTime = System.currentTimeMillis(); // 获取结束时间

		try {
			// 读取配置文件
			ClassifyProperties.getGlobalProperties();
			ClassifyProperties.getProperties();

			Map<String, Integer> map = getArgs(args);
			int iter = 0;
			String method = "";
			for (String k : map.keySet()) {
				method = k;
				iter = map.get(k);
			}

			if (iter == 0) {
				// 如果iter==0，则让程序自动跑到停为止（剩余文档数量少于总数的10%）
				iter = 1;
				iterend = 1000;
			} else {
				// 否则就只跑一次
				iterend = iter + 1;
			}
			ClassifyProperties.Iteration_ID = iter;

			if (method.equals("-iter"))
				iterate();
			if (method.equals("-cluster"))
				cluster();
			if (method.equals("-classify"))
				classify();
			if (method.equals("-gather")) {
				filenameInit(ClassifyProperties.Iteration_ID);
				gatherAllClass();
			}

		} catch (Exception e) {

			e.printStackTrace();

		} finally {
			endTime = System.currentTimeMillis(); // 获取结束时间
			System.out.println("程序运行时间： " + (double) (endTime - startTime)
					/ 1000 + "s");
		}
	}

	/**
	 * 对各种文件名进行初始化命名
	 * 
	 * @param iter
	 */
	public static void filenameInit(int iter) {

		// ************** 外部输出文件 ******************
		// featurefile = ClassifyProperties.FILE_PATH
		// + "feature/"
		// + ClassifyProperties
		// .updateFilename(ClassifyProperties.FEATURE_FILE);
		featurefile = ClassifyProperties.FILE_PATH
				+ ClassifyProperties
						.updateFilename(ClassifyProperties.RESULT_FILE);
		clusterResult = ClassifyProperties.FILE_PATH
				+ ClassifyProperties
						.updateFilename(ClassifyProperties.CLUSTER_RESULT);
		classifyTestResult = ClassifyProperties.FILE_PATH
				+ ClassifyProperties
						.updateFilename(ClassifyProperties.CLASSIFY_TEST_RESULT);
		classifyResult = ClassifyProperties.FILE_PATH
				+ ClassifyProperties
						.updateFilename(ClassifyProperties.RESULT_FILE);
		statisticsResult = ClassifyProperties.FILE_PATH
				+ ClassifyProperties
						.updateFilename(ClassifyProperties.CLASSIFY_TEST_STATISTICS);

		// ************* 临时文件 *********************
		// samplefile = ClassifyProperties.INNER_FILE_PATH +
		// ClassifyProperties.updateFilename(ClassifyProperties.CLUSTER_INPUT);
		// samplefile = ClassifyProperties.INNER_FILE_PATH + "samples" + iter
		// + ".txt";
		
//		leftfile = ClassifyProperties.INNER_FILE_PATH
//				+ ClassifyProperties
//						.updateFilename(ClassifyProperties.CLASSIFY_PREDICT);
//		trainfile = ClassifyProperties.INNER_FILE_PATH
//				+ ClassifyProperties
//						.updateFilename(ClassifyProperties.CLASSIFY_TRAIN);
//		testfile = ClassifyProperties.INNER_FILE_PATH
//				+ ClassifyProperties
//						.updateFilename(ClassifyProperties.CLASSIFY_TEST);
//		trainPlusTest = ClassifyProperties.INNER_FILE_PATH
//				+ ClassifyProperties
//						.updateFilename(ClassifyProperties.TRAIN_AND_TEST);
		
		leftfile = ClassifyProperties.FILE_PATH
				+ ClassifyProperties
						.updateFilename(ClassifyProperties.CLASSIFY_PREDICT);
		trainfile = ClassifyProperties.FILE_PATH
				+ ClassifyProperties
						.updateFilename(ClassifyProperties.CLASSIFY_TRAIN);
		testfile = ClassifyProperties.FILE_PATH
				+ ClassifyProperties
						.updateFilename(ClassifyProperties.CLASSIFY_TEST);
		trainPlusTest = ClassifyProperties.FILE_PATH
				+ ClassifyProperties
						.updateFilename(ClassifyProperties.TRAIN_AND_TEST);
	}

	/**
	 * 自动迭代程序
	 * 
	 * @param iter
	 * @throws Exception
	 */
	public static void iterate() throws Exception {

		filenameInit(ClassifyProperties.Iteration_ID);

		// 进入迭代器的文档总数量，不会因为迭代次数而减少
		int totalSize = FileUtils.getTotalLines(classifyResult);
		// int sampleSize = FileUtils.getTotalLines(samplefile);// 本次迭代的文档数量
		// if (sampleSize < totalSize * ClassifyProperties.STOP_RATIO) {
		// System.out.println("Iteration is stopped...");// 如果迭代文档数量小于一定比例，停止迭代
		// return;
		// }

		// 聚类簇数，如果为0则程序自己计算
		int maxClusterNum = ClassifyProperties.MAX_CLUSTER_NUM == 0 ? Cluster
				.getMaxClusterNum(featurefile)
				: ClassifyProperties.MAX_CLUSTER_NUM;
		System.out.println("Cluster Num:" + maxClusterNum);
		
		ClassifyProperties.BEST_SEED = ClassifyProperties.BEST_SEED == 0 ? Cluster
				.getBestSeed(featurefile)
				: ClassifyProperties.BEST_SEED;
		System.out.println("Seed:" + ClassifyProperties.BEST_SEED);

		for (; ClassifyProperties.Iteration_ID < iterend; ClassifyProperties.Iteration_ID++) {
			System.out.println("-------------------------------f"
					+ ClassifyProperties.FEATURE_ID + "--i"
					+ ClassifyProperties.Iteration_ID
					+ "-----------------------------------------");

			// 聚类。。。
			filenameInit(ClassifyProperties.Iteration_ID);
			ClassifyProperties.updateFieldIndex();
			Cluster cluster = new Cluster();
			// cluster.run(maxClusterNum, featurefile, samplefile,
			// clusterResult);
			cluster.run(maxClusterNum, classifyResult);
			cluster.appendToResultFile(classifyResult);
			cluster.writeToFile(clusterResult);

			// 根据人工标注文件选择簇，选择标注数据等
			// Preprocessing.run(clusterResult, samplefile, iter);

			//int annotationType = AnnotationType.FILTER_ANOTATION;
			int annotationType = AnnotationType.AUTO_ANOTATION;
			DatasetGenerator2 dg = new DatasetGenerator2(
					AnnotationFactory.create(annotationType));
			dg.run(classifyResult, classifyResult, leftfile, trainfile,
					testfile, trainPlusTest);

			// 分类。。。
			Classify c = new Classify();
			c.initDataset(dg);
			// List<Object> statistics1 = c.test(trainfile, testfile,
			// classifyTestResult);
			// List<Object> statistics2 = c.classify(trainPlusTest, leftfile,
			// classifyResult);
			List<Object> statistics1 = c.test(classifyTestResult);
			c.writeTestStatisticsToFile(statisticsResult);
			List<Object> statistics2 = c.classify(classifyResult);
			samplefile = ClassifyProperties.INNER_FILE_PATH + "samples"
					+ (ClassifyProperties.Iteration_ID + 1) + ".txt";
			c.writeSuspiciousToFile(samplefile);

			// 控制台输出数据结果
			StringBuilder stringBuilder = new StringBuilder();
			for (int i = 0; i < statistics1.size(); i++) {
				stringBuilder.append(statistics1.get(i).toString() + "\t");
			}
			for (int i = 0; i < statistics2.size(); i++) {
				stringBuilder.append(statistics2.get(i).toString() + "\t");
			}
			System.out.println(stringBuilder.toString());
			if (c.suspicious.size() < totalSize * ClassifyProperties.STOP_RATIO) {
				System.out.println("Iteration is stopped...");
				return;
			}
		}
	}

	public static Map<String, Integer> getArgs(String[] args) {
		Map<String, Integer> map = new HashMap<String, Integer>();
		for (String s : args)
			System.out.println(s);
		if (args.length == 1)
			map.put(args[0], 0);

		if (args.length >= 2) {
			for (int i = 0; i < args.length; i += 2) {
				map.put(args[i], Integer.valueOf(args[i + 1]));
			}
		}
		return map;
	}

	public static void cluster() {
		int featureid = ClassifyProperties.FEATURE_ID;
		filenameInit(ClassifyProperties.Iteration_ID);

		int maxClusterNum = ClassifyProperties.MAX_CLUSTER_NUM == 0 ? Cluster
				.getMaxClusterNum(featurefile)
				: ClassifyProperties.MAX_CLUSTER_NUM;
		System.out.println("Cluster Num:" + maxClusterNum);
		
		ClassifyProperties.BEST_SEED = ClassifyProperties.BEST_SEED == 0 ? Cluster
				.getBestSeed(featurefile)
				: ClassifyProperties.BEST_SEED;
		System.out.println("Seed:" + ClassifyProperties.BEST_SEED);

		System.out.println("-------------------------------f" + featureid
				+ "--i" + ClassifyProperties.Iteration_ID
				+ "--cluster -----------------------------------------");

		Cluster cluster = new Cluster();
		// cluster.run(maxClusterNum, featurefile, samplefile, clusterResult);
		try {
			cluster.run(maxClusterNum, classifyResult);
			cluster.appendToResultFile(classifyResult);
			cluster.writeToFile(clusterResult);
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}

	public static void classify() throws Exception {
		int featureid = ClassifyProperties.FEATURE_ID;

		System.out.println("-------------------------------f" + featureid
				+ "--i" + ClassifyProperties.Iteration_ID
				+ "--cluster -----------------------------------------");

		filenameInit(ClassifyProperties.Iteration_ID);

		DatasetGenerator2 dg = new DatasetGenerator2(
				AnnotationFactory.create(AnnotationType.MANUAL_ANOTATION));
		dg.run(clusterResult, featurefile, leftfile, trainfile, testfile,
				trainPlusTest);

		Classify c = new Classify();
		List<Object> statistics1 = c.test(trainfile, testfile,
				classifyTestResult);
		List<Object> statistics2 = c.classify(trainPlusTest, leftfile,
				classifyResult);
		samplefile = "etc/samples" + (ClassifyProperties.Iteration_ID + 1)
				+ ".txt";
		c.writeSuspiciousToFile(samplefile);

		StringBuilder stringBuilder = new StringBuilder();
		for (int i = 0; i < statistics1.size(); i++) {
			stringBuilder.append(statistics1.get(i).toString() + "\t");
		}
		for (int i = 0; i < statistics2.size(); i++) {
			stringBuilder.append(statistics2.get(i).toString() + "\t");
		}
		System.out.println(stringBuilder.toString());
		if (c.suspicious.size() < ClassifyProperties.STOP_LIMITATION) {
			System.out.println("Iteration is stopped...");
			return;
		}
	}

	public static void gatherAllClass() {
		CSVFileIO csv = new CSVFileIO();
		csv.load(classifyResult, true);
		Map<String, String> classMap = new HashMap<String, String>();
		// try {
		// classMap = csv.getColumn("Class");
		// } catch (NoSuchFieldException e) {
		// e.printStackTrace();
		// }

		try {
			for (int i = 1;; i++)
				classMap.putAll(csv.getColumn("class" + i));

		} catch (NoSuchFieldException e) {
			// e.printStackTrace();
		}

		List<String> attrfiles = FileUtils
				.readFileByLines(ClassifyProperties.ATTRIBUTE_FILR);
		for (String f : attrfiles)
			classMap.put(f, "属性");

		csv.insertColumn("Class", 1, classMap);
		try {
			csv.write(classifyResult, ",", true, true, 1);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}

	public static void clearResultFile(String resultfile) {
		CSVFileIO csv = new CSVFileIO();
		csv.load(resultfile, true);
		for (int i = ClassifyProperties.CLUSTER_INDEX; i < csv.getFields()
				.size(); i++) {
			csv.deleteColumn(i);
		}
		try {
			csv.write(resultfile, "", true);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public static void main(String[] args) {

		Iteration.run(args);
	}
}
