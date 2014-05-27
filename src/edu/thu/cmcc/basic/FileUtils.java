package edu.thu.cmcc.basic;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.LineNumberReader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import weka.core.Instance;
import weka.core.Instances;
import weka.core.converters.ArffSaver;
import weka.core.converters.CSVLoader;


public class FileUtils {
	
	/**
	 * Turn csv format to arff format
	 * @param csv file name
	 * @return arff file name
	 * @throws IOException
	 */
	public  static String csv2arff(String filename) throws IOException {
		// load CSV
		CSVLoader loader = new CSVLoader();
		loader.setSource(new File(filename));
		Instances data = loader.getDataSet();

		// save ARFF
		ArffSaver saver = new ArffSaver();
		saver.setInstances(data);
		String newname = "temp" + ".arff";
		saver.setFile(new File(newname));
		saver.setDestination(new File(newname));
		saver.writeBatch();

		return newname;
	}
	
	 public static List<String> readFileByLines(String fileName) {
	        File file = new File(fileName);
	        BufferedReader reader = null;
	        ArrayList<String> list = new ArrayList<String>();
	        try {
	            reader = new BufferedReader(new FileReader(file));
	            String tempString = null;
	            // 一次读入一行，直到读入null为文件结束
	            while ((tempString = reader.readLine()) != null) {
	                list.add(tempString.trim());
	            }
	            reader.close();
	        } catch (IOException e) {
	            e.printStackTrace();
	        } finally {
	            if (reader != null) {
	                try {
	                    reader.close();
	                } catch (IOException e1) {
	                }
	            }
	        }
	        return list;
	    }

	public static Instances getFilterDataset(String[] filenames, Instances oldset){
		Set<String> lines = new HashSet<String>();
		for(String f :filenames){
			lines.addAll(readFileByLines(f));
		}
		Instances newset = new Instances(oldset);
		newset.delete();
		for(int i =0; i < oldset.numInstances(); i++){
			Instance ins = oldset.instance(i);
			if (lines.contains(ins.toString(0))){
				newset.add(ins);
			}
		}
		return newset;
	}
	
	public static Instances getFilterDataset(String filename, Instances oldset){
		String[] files = {filename};
	    return getFilterDataset(files, oldset);
	}
	
    /**
     * 采用 LineNumberReader方式读取总行数
     * 
     * @param fileName
     * @return
     * @throws IOException
     */
    public static int getTotalLines(String fileName) throws IOException {
        FileReader in = new FileReader(fileName);
        LineNumberReader reader = new LineNumberReader(in);
        String strLine = reader.readLine();
        int totalLines = 0;
        while (strLine != null) {
            totalLines++;
            strLine = reader.readLine();
        }
        reader.close();
        in.close();
        return totalLines;
    }
	
}
