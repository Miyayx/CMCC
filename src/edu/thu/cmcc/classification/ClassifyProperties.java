package edu.thu.cmcc.classification;

import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

/**
 * 本类读入配置文件，并将各配置数据作为全局变量存储
 * @author Miyayx
 *
 */
public class ClassifyProperties {
	
	//property files
	public static final String CLASSIFY_PROP = "conf/classify.properties";
	public static final String FILENAME_PROP = "conf/filename.properties";
	public static final String FILE_COL_PROP = "conf/file_col.properties";
	public static final String DB_PROP       = "../conf/conf.properties";
	
	public static int      Iteration_ID       =1;
	
	// from classify.properties
	public static String   INNER_FILE_PATH    = "etc/";
	public static int      FEATURE_ID         = 0;
	public static String   SAMPLE_FILE        = null;
	public static int      CLASS_NUMBER       = 1; //分类数量 二分类设为1，三分类设为2
	public static double   INSTANCE_RATIO     = 0.3;
	public static double   STOP_RATIO         = 0.1;
	public static int 	   MAX_CLUSTER_NUM    = 4;//为0的话就由程序计算
	public static int      BEST_SEED          = -1;
	public static int      SEED_ITER          = 100;
	public static double   DBSCAN_EPS         = 2;
	public static int      DBSCAN_MINP        = 3;
	public static boolean  PROCESS_OUTPUT     = true;	
	public static String   ONTOLOGY_FILE      = null;
	public static double   LOWEST_ACCURACY    = 0;
	public static String   OTHER_CLASS        = null;
	public static String   POS_CLASS          = null;
	public static int      STOP_LIMITATION    = 0;
	public static int      POSITIVE_CLUSTER   = -1;
	public static boolean  SECTION_LABEL      = true;
	public static boolean  BLOCK_LABEL      = true;
	
	// from filename.properties
	public static String   FEATURE_FILE              = null;
	public static String   CLUSTER_INPUT             = null;
	public static String   CLUSTER_RESULT            = null;
	public static String   CLASSIFY_TRAIN            = null;
	public static String   CLASSIFY_TEST             = null;
	public static String   TRAIN_AND_TEST            = null;
	public static String   CLASSIFY_PREDICT          = null;
	public static String   CLASSIFY_TEST_RESULT      = null;
	public static String   CLASSIFY_TEST_STATISTICS  = null;
	public static String   RESULT_FILE               = null;
	public static String   ATTRIBUTE_FILR            = null;
	
	public static int      FEATURE_COUNT             = 0;
	public static int      CLUSTER_INDEX             = 0;
	public static int      FLAG_INDEX                = 0;
	public static int      CLASSIFY_INDEX            = 0;
	public static int      FILTER_INDEX              = 0;
	public static int      ALL_CLASS_INDEX           = 0;
	
	// from conf.properties
	public static String   FILE_PATH          = "";
	public static String   DB_HOST            ="localhost";
	public static String   DB_URL             ="";
	public static String   DB_NAME            ="mobile";
	public static String   COLLECTION_NAME    ="doc_parse";
	
	/**
	 * 整个mobile工程全局变量
	 * @param propFile
	 */
	public static void getGlobalProperties(){
		Properties prop = new Properties();//属性集合对象    
		   FileInputStream fis;
		try {
			fis = new FileInputStream(ClassifyProperties.DB_PROP);
			prop.load(fis);//将属性文件流装载到Properties对象中  
			FILE_PATH = prop.getProperty("data.path", "")+"/Classify/";
			DB_HOST   = prop.getProperty("mongo.host", "127.0.0.1");
			DB_URL    = prop.getProperty("mongo.url", "mongodb://127.0.0.1:27017/mobile");
			DB_NAME   = prop.getProperty("mongo.dbname", "mobile");
			COLLECTION_NAME = prop.getProperty("mongo.collection", "doc_parse");
			
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}//属性文件流    
		
	}
	/**
	 * 仅Classify工程配置
	 * @param propFile
	 */
	public static void getProperties(){
		
		Properties prop = new Properties();//属性集合对象    
		   FileInputStream fis;
		try {
			fis = new FileInputStream(ClassifyProperties.CLASSIFY_PROP);
			prop.load(fis);//将属性文件流装载到Properties对象中  
			
			INNER_FILE_PATH    = prop.getProperty("inner_file_path", "etc/");
			FEATURE_ID         = Integer.valueOf(prop.getProperty("featureid", String.valueOf(0)));
			SAMPLE_FILE        = FILE_PATH+prop.getProperty("samplefile", "samples1.txt");
			CLASS_NUMBER       = Integer.valueOf(prop.getProperty("class_number", String.valueOf(1)));
			INSTANCE_RATIO     = Double.valueOf(prop.getProperty("instance_ratio", String.valueOf(0.3)));
			STOP_RATIO         = Double.valueOf(prop.getProperty("stop_ratio", String.valueOf(0.1)));
			MAX_CLUSTER_NUM    = Integer.valueOf(prop.getProperty("max_cluster_num", String.valueOf(0)));
			BEST_SEED          = Integer.valueOf(prop.getProperty("best_seed", String.valueOf(-1)));
			SEED_ITER          = Integer.valueOf(prop.getProperty("seed_iter", String.valueOf(100)));
			DBSCAN_EPS         = Double.valueOf(prop.getProperty("dbscan_eps", String.valueOf(2)));
			DBSCAN_MINP        = Integer.valueOf(prop.getProperty("dbscan_minp", String.valueOf(3)));
			PROCESS_OUTPUT     = Boolean.valueOf(prop.getProperty("process_output", "true"));
			ONTOLOGY_FILE      = prop.getProperty("ontology", "etc/ontology.txt");
			LOWEST_ACCURACY    = Double.valueOf(prop.getProperty("lowest_accuracy",String.valueOf(0.85)));
			OTHER_CLASS        = prop.getProperty("other_class","others");
			POS_CLASS          = prop.getProperty("positive_class","");
			STOP_LIMITATION    = Integer.valueOf(prop.getProperty("stop_limitation", String.valueOf(0)));
			POSITIVE_CLUSTER   = Integer.valueOf(prop.getProperty("positive_cluster", String.valueOf(-1)));
			SECTION_LABEL      = Boolean.valueOf(prop.getProperty("section_label", "true"));
			BLOCK_LABEL        = Boolean.valueOf(prop.getProperty("block_label", "true"));
			
			fis = new FileInputStream(ClassifyProperties.FILENAME_PROP);
			prop.load(fis);//将属性文件流装载到Properties对象中  
			FEATURE_FILE             = prop.getProperty("feature");
			CLUSTER_INPUT            = prop.getProperty("cluster_input");
			CLUSTER_RESULT           = prop.getProperty("cluster_result");
			CLASSIFY_TRAIN           = prop.getProperty("classify_train");
			CLASSIFY_TEST            = prop.getProperty("classify_test");
			TRAIN_AND_TEST           = prop.getProperty("train_and_test");
			CLASSIFY_PREDICT         = prop.getProperty("classify_predict");
			CLASSIFY_TEST_RESULT     = prop.getProperty("classify_test_result");
			CLASSIFY_TEST_STATISTICS = prop.getProperty("classify_test_statistics");
			RESULT_FILE              = prop.getProperty("result");
			ATTRIBUTE_FILR           = FILE_PATH + prop.getProperty("attribute");        
			
			fis = new FileInputStream(ClassifyProperties.FILE_COL_PROP);
			prop.load(fis);
			FEATURE_COUNT            = Integer.valueOf(prop.getProperty("feature_count", String.valueOf(0)));
			ALL_CLASS_INDEX          = 1;
			updateFieldIndex();

		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}//属性文件流    
		
	}
	
	/**
	 * 每次迭代根据迭代信息生成新的文件名，将文件中的X和Y替换
	 * @param origin  原名称
	 * @return        新名称
	 */
	public static String updateFilename(String origin){
		String newName = new String(origin);
		newName = newName.replace("X", String.valueOf(ClassifyProperties.Iteration_ID));
		newName = newName.replace("Y",
				String.valueOf(ClassifyProperties.FEATURE_ID));
		return newName;
	}
	
	/**
	 * 每次迭代更新写入大表的列的信息
	 */
	public static void updateFieldIndex(){
		int feature_kind = 0;
		if(SECTION_LABEL)
			feature_kind++;
		if(BLOCK_LABEL)
			feature_kind++;
		CLUSTER_INDEX            = 1+FEATURE_COUNT+1+feature_kind+(3 * (Iteration_ID - 1));
		System.out.println("Iteration_id:"+Iteration_ID);
		System.out.println("CLUSTER_INDEX:"+CLUSTER_INDEX);
		FLAG_INDEX               = CLUSTER_INDEX + 1;
		CLASSIFY_INDEX           = FLAG_INDEX + 1;
		FILTER_INDEX             = (Iteration_ID == 1) ? 0 :CLUSTER_INDEX-1 ;
	}
}
