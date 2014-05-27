package classification_dbscan;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;

import org.apache.commons.lang3.StringUtils;

import edu.thu.cmcc.basic.FileManipulator;
import edu.thu.cmcc.basic.FileUtils;

public class AddClass {

	public Map<String, String> readClassFile(String file) {
		Map<String, String> sample2class = new HashMap<String, String>();

		List<String> lines = FileUtils.readFileByLines(file);
		for (String line : lines) {
			String[] ls = line.trim().split("\t\t");
			sample2class.put(ls[1], ls[2]);
		}
		return sample2class;
	}

	public Map<String, String> readFeatureFile(String file) {
		Map<String, String> sample2feature = new HashMap<String, String>();

		List<String> lines = FileUtils.readFileByLines(file);
		lines.remove(0);
		for (String line : lines) {
			String[] ls = line.trim().split(",", 2);
			sample2feature.put(ls[0], ls[1]);
		}
		return sample2feature;
	}

	public String getColnames(String file) {
		return FileUtils.readFileByLines(file).get(0);
	}

	public List<Boolean> cutlist(List<String> list, double ratio) {
		List<Boolean> result = new LinkedList<Boolean>();
		Set<Integer> done = new HashSet<Integer>();
		int count = (int) Math.round(list.size() * ratio);
		while (done.size() < count) {
			Random rdm = new Random();
			int index = Math.abs(rdm.nextInt() % list.size());
			if (!done.contains(index)) {
				done.add(index);
			}
		}
		for (int i = 0; i < list.size(); i++) {
			if (done.contains(i)) {
				result.add(true);
			} else {
				result.add(false);
			}
		}
		return result;

	}

	public Map<String, Set<String>> filterLeftDataset(String filename)
			throws IOException {
		Map<String, Set<String>> all = FileManipulator.loadOneToMany(
				"etc/ontology.txt", "\t\t", ";;;");
		List<String> list = FileUtils.readFileByLines(filename);
		Map<String, Set<String>> map = new HashMap<String, Set<String>>();
		Iterator it = all.entrySet().iterator();
		while (it.hasNext()) {
			Map.Entry e = (Map.Entry) it.next();
			String c = (String) e.getKey();
			Set<String> samples = (Set<String>) e.getValue();
			Set<String> ss = new HashSet<String>();
			for (String s : samples) {
				if (list.contains(s))
					ss.add(s);
			}
			map.put(c, ss);
		}
		return map;
	}

	public void writeClassifyDataset(Map<String, String> s2c,
			Map<String, String> s2f, double ratio, String colname,
			String samplefile, String leftfile, String trainfile,
			String testfile) throws IOException {

		Map<String, Set<String>> map = new HashMap<String, Set<String>>();
		Map<String, Set<String>> train = new HashMap<String, Set<String>>();
		Map<String, Set<String>> test = new HashMap<String, Set<String>>();

		colname = colname.trim() + ",class\n";

		Iterator it = s2c.entrySet().iterator();
		while (it.hasNext()) {
			Map.Entry e = (Map.Entry) it.next();
			String s = (String) e.getKey();
			String c = (String) e.getValue();
			if (map.containsKey(c)) {
				Set<String> slist = (Set<String>) map.get(c);
				slist.add(s);
				map.put(c, slist);
			} else {
				Set<String> slist = new HashSet<String>();
				slist.add(s);
				map.put(c, slist);
			}

		}
		it = map.entrySet().iterator();
		while (it.hasNext()) {
			Map.Entry e = (Map.Entry) it.next();
			String c = (String) e.getKey();
			List<String> slist = new ArrayList((Set<String>) e.getValue());
			int size = slist.size();
			int index = (int) (size * 0.3);
			
			if (size > 100)
				index = (int) (size * 0.3);
			else if (size > 60)
				index = (int) (size * 0.4);
			else if (size >= 3)
				index = (int) (size * (2.0/3));
			else
				index = size;
			

			train.put(c, new HashSet(slist.subList(0, index)));
			test.put(c, new HashSet(slist.subList(index,size)));

		}
		System.out.println("Train length: " + getItemCount(train));
		System.out.println("Test length: " + getItemCount(test));

		addClass(s2f, trainfile, colname, train);
		addClass(s2f, testfile, colname, test);
	}

	public int getItemCount(Map<String, Set<String>> map) {
		Iterator it = map.entrySet().iterator();
		int count = 0;
		while (it.hasNext()) {
			Map.Entry e = (Map.Entry) it.next();
			int num = ((Set<String>) e.getValue()).size();
			System.out.println(e.getKey() + ":" + num);
			count += num;
		}
		return count;
	}

	public void addClass(Map<String, String> s2f, String file, String colname,
			Map<String, Set<String>> map) throws IOException {
		BufferedWriter out = new BufferedWriter(new FileWriter(file));
		out.write(colname + "\n");
		for (Map.Entry<String, Set<String>> e : map.entrySet()) {
			for (String s : e.getValue()) {
				if (s2f.get(s) != null) {
					out.write(s + "," + s2f.get(s) + "," + e.getKey() + "\n");
					out.flush();
				}
			}
		}
		out.close();
	}

	public void run(String classfile, String featurefile, String samplefile,
			String leftfile, String trainfile, String testfile) {
		Map<String, String> s2c = readClassFile(classfile);
		Map<String, String> s2f = readFeatureFile(featurefile);
		String colname = getColnames(featurefile);
		try {
			writeClassifyDataset(s2c, s2f, (double) 2 / 3, colname, samplefile,
					leftfile, trainfile, testfile);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

}
