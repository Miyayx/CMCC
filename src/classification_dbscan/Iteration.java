package classification_dbscan;

import weka.classifiers.Classifier;
import weka.classifiers.functions.LibSVM;
import weka.classifiers.functions.Logistic;
import weka.clusterers.Clusterer;
import weka.clusterers.DBSCAN;

public class Iteration {

	public static void main(String[] args) throws Exception {
		int iter = 2;
		int feature = 1;
		String featurefile = "etc/features" + feature + ".csv";
		String clusterResult = "etc/ClusterResult" + iter + "_f" + feature
				+ ".txt";
		String samplefile = "etc/samples" + iter + ".txt";
		String nextfile = "etc/samples" + (iter + 1) + ".txt";
		String classifyfile = "etc/classify" + iter + "_f" + feature + ".csv";
		String leftfile = "etc/left" + iter + "_f" + feature + ".csv";
		String trainfile = "etc/train" + iter + "_f" + feature + ".csv";
		String testfile = "etc/test" + iter + "_f" + feature + ".csv";
		String suspicious = "etc/suspicious" + (iter - 1) + "_f" + feature
				+ ".txt";
		String classifyTestResult = "etc/ClassifyTestResult" + iter + "_f"
				+ feature + ".txt";
		String classifyResult = "etc/ClassifyResult" + iter + "_f" + feature
				+ ".txt";

		DBScan dbs = new DBScan();
		Boolean dbscanOK = dbs.run(featurefile, samplefile, clusterResult);
		while (! dbscanOK){
			dbscanOK = dbs.run( featurefile, samplefile, clusterResult);
		}

		Preprocessing2.run(clusterResult, "etc/correctInstance.txt", nextfile);

		AddClass ac = new AddClass();
		ac.run("etc/correctInstance.txt", featurefile, samplefile, leftfile,
				trainfile, testfile);
		// ac.run("etc/correctInstance.txt",featurefile,allfile,trainfile,testfile);

		Classifier m_classifier = new LibSVM();
		String[] options = {// SVM的参数配置
				// "-split-percentage","50",
				"-K", "0", "-S", "0", "-x", "10", "-N", "0", "-M", "100", "-W",
				"1.0 1.0", "-G", "0.5", "-P", "0.8", "-b", "1" };
		m_classifier.setOptions(options);
		Classify c = new Classify(m_classifier);
		c.run(featurefile, trainfile, testfile, classifyTestResult);
		c.writeSuspiciousToFile(nextfile);
	}
}
