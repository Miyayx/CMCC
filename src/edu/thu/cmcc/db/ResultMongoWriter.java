package edu.thu.cmcc.db;
import java.io.FileInputStream;
import java.io.IOException;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBObject;
import com.mongodb.Mongo;

import edu.thu.cmcc.basic.FileManipulator;
import edu.thu.cmcc.classification.ClassifyProperties;

/**
 * 分类结果写入数据库
 * @author Miyayx
 *
 */
public class ResultMongoWriter {
	
	public ResultMongoWriter(String configfie) {
		ClassifyProperties.getGlobalProperties();
	}
	
	public void write(String resultFile) throws IOException{
		Map<String,String> map = FileManipulator.loadOneToOne(resultFile, ",", 0,1);
		write(map);
	} 
	
	/**
	 *  
	 * @param map key：文档名  value：所属类别
	 * @throws UnknownHostException
	 */
	@SuppressWarnings("unchecked")
	public void write(Map map) throws UnknownHostException {
		System.out.println("writeToMongo");
		Mongo mongo = new Mongo(ClassifyProperties.DB_HOST);
		DB db = mongo.getDB(ClassifyProperties.DB_NAME);
		DBCollection collection = db.getCollection(ClassifyProperties.COLLECTION_NAME);
		
		//Mongo mongo = new Mongo();
		//DB db = mongo.getDB(ClassifyProperties.DB_NAME);
		//DBCollection collection = db.getCollection("doc_parse");
		
		//remove the origin data
		DBObject removeCondition = new BasicDBObject();
		removeCondition.put("level", "document");
		DBObject removeValue = new BasicDBObject();
		removeValue.put("classes", "");
		DBObject removeSetValue = new BasicDBObject("$unset", removeValue);
		collection.update(removeCondition, removeSetValue, false, true);

		Iterator it = map.entrySet().iterator();
		while (it.hasNext()) {
			Map.Entry pairs = (Map.Entry) it.next();
			String k = (String) pairs.getKey();
			String[] ks = k.split("/");
			int len = ks.length;
			String path = "";
			for (int i = 0; i < len - 1; i++) {
				path += ks[i];
				path += "/";
			}
			//path = "etc/移动"+path;
			String name = ks[len - 1];
			String v = (String) pairs.getValue();

			DBObject updateCondition = new BasicDBObject();
			updateCondition.put("level", "document");
			updateCondition.put("_id.name", name);
			updateCondition.put("_id.path", path);

			DBObject updatedValue = new BasicDBObject();
			updatedValue.put("classes", v);
			DBObject updateSetValue = new BasicDBObject("$set", updatedValue);
			collection.update(updateCondition, updateSetValue);

			it.remove(); 
		}
	}
	

	public void writeClusterToMongo(Map map) throws UnknownHostException {
		System.out.println("writeToMongo");
		Mongo mongo = new Mongo();
		DB db = mongo.getDB("mobile");
		DBCollection collection = db.getCollection("doc_parse");

		Iterator it = map.entrySet().iterator();
		while (it.hasNext()) {
			Map.Entry pairs = (Map.Entry) it.next();
			int k = ((Integer) pairs.getKey()).intValue(); // cluster
			List<String> list = (List<String>) pairs.getValue(); // docs for
																	// cluster k
			for (String l : list) {
				String[] ks = l.split("/");
				int len = ks.length;
				String path = "";
				for (int i = 0; i < len - 1; i++) {
					path += ks[i];
					path += "/";
				}
				path = path.replaceFirst("etc", "../data");
				String name = ks[len - 1];

				DBObject updateCondition = new BasicDBObject();
				updateCondition.put("_id.name", name);
				updateCondition.put("_id.path", path);

				DBObject updatedValue = new BasicDBObject();
				updatedValue.put("cluster", k);

				DBObject updateSetValue = new BasicDBObject("$set",
						updatedValue);

				collection.update(updateCondition, updateSetValue);
			}
			it.remove(); // avoids a ConcurrentModificationException
		}
	}

	public static void main(String[] args) {
		String classifyResultFile = "";
		if(args[0].equals("-file") && args.length ==2)
			classifyResultFile = args[1];
		ResultMongoWriter rmw = new ResultMongoWriter("../conf/conf.properties");
		try {
			rmw.write(classifyResultFile);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
}
