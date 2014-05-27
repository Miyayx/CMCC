package classification_old;

import weka.classifiers.Classifier;
import weka.classifiers.functions.LibSVM;
import weka.classifiers.functions.Logistic;

public class Iteration {
	
	public static void main(String[] args) throws Exception {
		int iter = 1;
		int feature = 1;
		String featurefile = "etc/features"+feature+".csv";
		String clusterResult = "etc/ClusterResult"+iter+"_f"+feature+".txt";
		String samplefile="etc/samples"+iter+".txt";
		String classifyfile = "etc/classify"+iter+"_f"+feature+".csv";
		String leftfile = "etc/left"+iter+"_f"+feature+".csv";
		String trainfile="etc/train"+iter+"_f"+feature+".csv";
		String testfile="etc/test"+iter+"_f"+feature+".csv";
		String suspicious = "etc/suspicious"+(iter-1)+"_f"+feature+".txt";
		String classifyTestResult = "etc/ClassifyTestResult"+iter+"_f"+feature+".txt"; 
		String classifyResult = "etc/ClassifyResult"+iter+"_f"+feature+".txt"; 
		
		KMeans km = new KMeans();
	//	String[] files = {suspicious,"etc/wrongInstance.txt"};
		String[] files = {samplefile};
		km.setIterFilter(files);
	//	km.setIterNum(iter);
		km.run(6-iter, featurefile,samplefile,clusterResult);
		
		Preprocessing.run(clusterResult);
		
		AddClass ac = new AddClass();
		ac.run("etc/correctInstance.txt",featurefile,samplefile,leftfile,trainfile, testfile);
		//ac.run("etc/correctInstance.txt",featurefile,allfile,trainfile,testfile);
		
		Classifier m_classifier = new LibSVM();
	//	Classifier m_classifier = new Logistic();
		String[] options = {// SVM的参数配置
				// "-split-percentage","50",
				"-K", "0", "-S", "0", "-x", "10", "-N", "0", "-M", "100", "-W",
				"1.0 1.0", "-G", "0.5", "-P", "0.8", "-b","1"};
		m_classifier.setOptions(options);
		Classify c = new Classify(m_classifier);
//		c.run(featurefile, classifyfile,(double)2/3,classifyResult);
		c.run(featurefile, trainfile, testfile,classifyTestResult);
		c.classification(leftfile, classifyResult);
		samplefile = "etc/samples"+(iter+1)+".txt";
		c.writeSuspiciousToFile(samplefile);
		//c.writeSuspiciousToFile(suspicious);	
	}
}
