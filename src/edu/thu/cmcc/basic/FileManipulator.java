package edu.thu.cmcc.basic;

import java.io.*;
import java.util.*;
import java.util.Map.Entry;

import org.apache.commons.lang3.StringUtils;

public class FileManipulator {
	public final static int Only_One_Column_Flag = -1;
	public final static int First_Column_Num = 0;
	public final static int Second_Column_Num = 1;

	// column=-1 means load a file with only one column
	public static Set<String> loadOneColum(String fileName, String separator,
			int column) throws IOException {
		Set<String> columnSet = new HashSet<String>();

		// System.out.println("Start loading " + fileName);

		BufferedReader in = new BufferedReader(new FileReader(fileName));
		String line = null;
		if (column == Only_One_Column_Flag)
			while (null != (line = in.readLine()))
				columnSet.add(line.trim());
		else
			while (null != (line = in.readLine())) {
				String[] array = line.trim().split(separator);
				if (array.length > column) {
					String value = array[column].trim();
					if (!StringUtils.isEmpty(value))
						columnSet.add(value);
				}
			}
		in.close();

		System.out.println(fileName + " loaded. " + new Date());

		return columnSet;
	}

	public static Map<String, Set<String>> loadSets(String fileName,
			String separator) throws IOException {
		Map<String, Set<String>> resultMap = new HashMap<String, Set<String>>();
		BufferedReader in = new BufferedReader(new FileReader(fileName));
		String line = null;
		while (null != (line = in.readLine())) {
			String[] array = line.trim().split(separator);
			Set<String> set = new HashSet<String>();
			for (String string : array) {
				set.add(string.trim());
			}
			for (String string : array) {
				resultMap.put(string, set);
			}
		}
		in.close();
		System.out.println(fileName + " loaded. " + new Date());
		return resultMap;
	}

	public static List<Set<String>> loadSet(String fileName, String separator)
			throws IOException {
		List<Set<String>> result = new LinkedList<Set<String>>();
		BufferedReader in = new BufferedReader(new FileReader(fileName));
		String line = null;
		while (null != (line = in.readLine())) {
			String[] array = line.trim().split(separator);
			Set<String> set = new HashSet<String>();
			for (String string : array) {
				set.add(string.trim());
			}
			result.add(set);
		}
		in.close();
		System.out.println(fileName + " loaded. " + new Date());
		return result;
	}

	public static Map<String, String> loadOneToOne(String fileName,
			String separator, int keyColumnNum) throws IOException {
		Map<String, String> map = new HashMap<String, String>();

		 System.out.println("Start loading " + fileName);

		BufferedReader in = new BufferedReader(new FileReader(fileName));
		String line = null;
		while (null != (line = in.readLine())) {
			String[] array = line.trim().split(separator);
			if (array.length != 2)
				continue;
			map.put(array[keyColumnNum].trim(), array[1 - keyColumnNum].trim());
		}
		in.close();
		System.out.println(fileName + " loaded. " + new Date());

		return map;
	}
	
	public static Map<String, String> loadOneToOne(String fileName,
			String separator, int keyColumnNum, int valueColumnNum) throws IOException {
		
		Map<String, String> map = new HashMap<String, String>();

		BufferedReader in = new BufferedReader(new FileReader(fileName));
		String line = null;
		while (null != (line = in.readLine())) {
			String[] array = line.trim().split(separator);
			if (array.length < valueColumnNum+1)
				continue;
		//	String value = array[valueColumnNum].trim();
		//	if(value.length() == 0)
		//		value = "";
			map.put(array[keyColumnNum].trim(), array[valueColumnNum].trim());
		}
		in.close();
		System.out.println(fileName + " loaded. " + new Date());

		return map;
	}

	public static Map<String, String> loadOneToOne(String fileName,
			String separator, int keyColumnNum, Set<String> keySet)
			throws IOException {
		Map<String, String> map = new HashMap<String, String>();

		// System.out.println("Start loading " + fileName);

		BufferedReader in = new BufferedReader(new FileReader(fileName));
		String line = null;
		while (null != (line = in.readLine())) {
			String[] array = line.trim().split(separator);
			if (array.length != 2)
				continue;
			if (!keySet.contains(array[keyColumnNum].trim()))
				continue;
			map.put(array[keyColumnNum].trim(), array[1 - keyColumnNum].trim());
		}
		in.close();

		System.out.println(fileName + " loaded. " + new Date());

		return map;
	}

	public static Map<String, Set<String>> loadOneToMany(String fileName,
			String separator1, String separator2) throws IOException {
		Map<String, Set<String>> oneToMany = new HashMap<String, Set<String>>();

		// System.out.println("Start loading " + fileName);

		BufferedReader in = new BufferedReader(new FileReader(fileName));
		String line = null;
		while (null != (line = in.readLine())) {
			String[] keyValues = line.trim().split(separator1);
			if (keyValues.length != 2)
				continue;

			String key = keyValues[0].trim();
			if (StringUtils.isEmpty(key))
				continue;

			String[] many = keyValues[1].split(separator2);
			Set<String> set = new HashSet<String>();
			for (String each : many) {
				each = each.trim();
				if (!StringUtils.isEmpty(each))
					set.add(each);
			}

			if (set.size() == 0)
				continue;
			oneToMany.put(key, set);
		}
		in.close();
		System.out.println(fileName + " loaded. " + new Date());

		return oneToMany;
	}

	public static Map<String, Set<String>> loadOneToMany(String fileName,
			String separator) throws IOException {
		Map<String, Set<String>> oneToMany = new HashMap<String, Set<String>>();
		BufferedReader in = new BufferedReader(new FileReader(fileName));
		String line = null;
		while (null != (line = in.readLine())) {
			String[] keyValues = line.trim().split(separator);
			if (keyValues.length != 2)
				continue;
			String key = keyValues[0].trim();
			if (StringUtils.isEmpty(key))
				continue;

			String value = keyValues[1].trim();
			if (StringUtils.isEmpty(key))
				continue;

			if (oneToMany.containsKey(key)) {
				Set<String> set = oneToMany.get(key);
				set.add(value);
				oneToMany.put(key, set);
			} else {
				Set<String> set = new HashSet<String>();
				set.add(value);
				oneToMany.put(key, set);
			}
		}
		in.close();
		System.out.println(fileName + " loaded. " + new Date());

		return oneToMany;
	}

	public static Map<String, Set<String>> loadOneToMany(String fileName,
			String separator1, String separator2, Set<String> keySet,
			Set<String> valueSet) throws IOException {
		Map<String, Set<String>> oneToMany = new HashMap<String, Set<String>>();

		// System.out.println("Start loading " + fileName);

		BufferedReader in = new BufferedReader(new FileReader(fileName));
		String line = null;
		while (null != (line = in.readLine())) {
			String[] keyValues = line.trim().split(separator1);
			if (keyValues.length != 2)
				continue;

			String key = keyValues[0].trim();
			if (StringUtils.isEmpty(key) || !keySet.contains(key))
				continue;

			String[] many = keyValues[1].split(separator2);
			Set<String> set = new HashSet<String>();
			for (String each : many) {
				each = each.trim();
				if (!StringUtils.isEmpty(each) && valueSet.contains(each))
					set.add(each);
			}

			if (set.size() == 0)
				continue;
			oneToMany.put(key, set);
		}
		in.close();
		System.out.println(fileName + " loaded. " + new Date());

		return oneToMany;
	}

	public static void outputOneToOne(Map<String, String> map, String fileName,
			String separator, int keyColumnNum) throws IOException {
		String key = null;
		String value = null;

		// System.out.println("Start outputing " + fileName);

		BufferedWriter out = new BufferedWriter(new FileWriter(fileName));
		for (Map.Entry<String, String> e : map.entrySet()) {
			if (keyColumnNum == FileManipulator.First_Column_Num) {
				key = e.getKey();
				value = e.getValue();
			} else if (keyColumnNum == FileManipulator.Second_Column_Num) {
				key = e.getValue();
				value = e.getKey();
			} else {
				System.out
						.println("Error happens in FileManipulator.outputOneToOne()");
			}
			if (StringUtils.isEmpty(key))
				continue;

			out.write(key + separator + value + "\n");
			out.flush();
		}
		out.close();

		// System.out.println("Finish outputing " + fileName);
	}

	public static void outputOneToMany(Map<String, Set<String>> oneToMany,
			String fileName, String separator1, String separator2)
			throws IOException {
		// System.out.println("Start outputing " + fileName);

		BufferedWriter out = new BufferedWriter(new FileWriter(fileName));
		for (Map.Entry<String, Set<String>> e : oneToMany.entrySet()) {
			String key = e.getKey();
			if (StringUtils.isEmpty(key))
				continue;

			Set<String> set = e.getValue();
			StringBuilder tmp = new StringBuilder();
			tmp.append(key + separator1);
			for (String s : set)
				tmp.append(s + separator2);
			String tmps = tmp.toString();
			if (tmps.toString().endsWith(separator2))
				tmps = tmps.substring(0, tmps.length() - separator2.length());

			out.write(tmps + "\n");
			out.flush();
		}
		out.close();

		// System.out.println("Finish outputing " + fileName);
	}

	public static void outputOneToMany(Map<String, Set<String>> oneToMany,
			String fileName, String separator) throws IOException {
		BufferedWriter out = new BufferedWriter(new FileWriter(fileName));
		for (Map.Entry<String, Set<String>> e : oneToMany.entrySet()) {
			String key = e.getKey();
			if (StringUtils.isEmpty(key))
				continue;

			Set<String> set = e.getValue();
			for (String value : set) {
				out.write(key + separator + value + "\n");
				out.flush();
			}
		}
		out.close();
		System.out.println("Finish outputing " + fileName);
	}

	public static Set<String> loadOneRow(String fileName, String rowName)
			throws IOException {
		Set<String> rowSet = new HashSet<String>();
		BufferedReader in = new BufferedReader(new FileReader(fileName));
		String line = null;
		while (null != (line = in.readLine())) {
			if (line.startsWith(rowName)) {
				rowSet.add(line.substring(rowName.length() + 1).trim());
			}
		}
		in.close();
		System.out.println(fileName + " loaded. " + new Date());

		return rowSet;
	}

	public static void outputOneToMap(
			Map<String, Map<String, String>> oneToOneToMany, String fileName,
			String separator1, String separator2, String separator3)
			throws IOException {
		// System.out.println("Start outputing " + fileName);
		int i = 0;
		BufferedWriter out = new BufferedWriter(new FileWriter(fileName));
		for (Entry<String, Map<String, String>> e : oneToOneToMany.entrySet()) {

			String key = e.getKey();
			if (StringUtils.isEmpty(key))
				continue;

			Map<String, String> map = e.getValue();
			StringBuilder tmp = new StringBuilder();
			tmp.append(key + separator1);
			for (String s : map.keySet()) {
				tmp.append(s + separator3 + map.get(s) + separator2);
			}
			String tmps = tmp.toString();
			if (tmps.endsWith(separator2))
				tmps = tmps.substring(0, tmps.length() - separator2.length());

			out.write(tmp + "\n");
			out.flush();
		}
		out.close();

		System.out.println("Finish outputing " + fileName);
	}

	public static Map<String, Set<String>> loadOneToMany_map(String fileName,
			String separator1, String separator2, String separator3)
			throws IOException {
		Map<String, Set<String>> oneToMany = new HashMap<String, Set<String>>();

		BufferedReader in = new BufferedReader(new FileReader(fileName));
		String line = null;
		while (null != (line = in.readLine())) {
			String[] keyValues = line.trim().split(separator1);
			if (keyValues.length != 2)
				continue;

			String key = keyValues[0].trim();
			if (StringUtils.isEmpty(key))
				continue;

			String[] many = keyValues[1].split(separator2);
			Set<String> set = new HashSet<String>();
			for (String each : many) {
				String[] ss = each.trim().split(separator3);
				if (ss.length == 2 && !StringUtils.isEmpty(ss[0])
						&& !StringUtils.isEmpty(ss[1]))
					set.add(ss[0]);
			}

			if (set.size() == 0)
				continue;
			oneToMany.put(key, set);
		}
		in.close();
		System.out.println(fileName + " loaded. " + new Date());

		return oneToMany;
	}

	public static Map<String, Map<String, String>> loadOneToMap(
			String fileName, String separator1, String separator2,
			String separator3) throws IOException {
		Map<String, Map<String, String>> oneToMany = new HashMap<String, Map<String, String>>();

		BufferedReader in = new BufferedReader(new FileReader(fileName));
		String line = null;
		while (null != (line = in.readLine())) {
			String[] keyValues = line.trim().split(separator1);
			if (keyValues.length != 2)
				continue;

			String key = keyValues[0].trim();
			if (StringUtils.isEmpty(key))
				continue;

			String[] many = keyValues[1].split(separator2);
			Map<String, String> map = new HashMap<String, String>();
			for (String each : many) {
				String[] ss = each.trim().split(separator3);
				if (ss.length == 2 && !StringUtils.isEmpty(ss[0])
						&& !StringUtils.isEmpty(ss[1]))
					map.put(ss[0], ss[1]);
			}

			if (map.size() == 0)
				continue;
			oneToMany.put(key, map);
		}
		in.close();
		System.out.println(fileName + " loaded. " + new Date());

		return oneToMany;
	}

	public static void reverse(String infile, String outfile,
			String separator1, String separator2) throws IOException {
		BufferedReader reader = new BufferedReader(new FileReader(infile));
		BufferedWriter writer = new BufferedWriter(new FileWriter(outfile));
		Map<String, Set<String>> antes = new HashMap<String, Set<String>>();
		Map<String, Set<String>> conses = new HashMap<String, Set<String>>();
		String s;
		while ((s = reader.readLine()) != null) {
			String[] ss = s.split(separator1);
			if (ss.length > 0) {
				String title = ss[0].trim();
				if (ss.length > 1 && StringUtils.isNotBlank(ss[1])) {
					Set<String> set = new HashSet<String>();
					String[] conse = ss[1].split(separator2);
					for (int i = 0; i < conse.length; i++) {
						if (StringUtils.isNotBlank(conse[i].trim())) {
							set.add(conse[i].trim());
						}
					}
					antes.put(title, set);
				}
			}
		}
		System.out.println("read is done " + antes.size());
		for (String title2 : antes.keySet()) {
			Set<String> conseSet = antes.get(title2);
			for (String conse : conseSet) {
				if (conses.containsKey(conse)) {
					Set<String> set = conses.get(conse);
					set.add(title2);
				} else {
					Set<String> set = new HashSet<String>();
					set.add(title2);
					conses.put(conse, set);
				}
			}
		}
		System.out.println("reverse is done " + conses.size());
		for (String title3 : conses.keySet()) {
			StringBuilder sb = new StringBuilder();
			sb.append(title3 + separator1);
			Iterator<String> iter = conses.get(title3).iterator();
			if (iter.hasNext()) {
				sb.append(iter.next());
			}
			while (iter.hasNext()) {
				sb.append(separator2 + iter.next());
			}
			writer.write(sb.toString() + "\n");
			writer.flush();
		}
		System.out.println("output is done ");
	}

	public static Map<String, Set<String>> reverse(
			Map<String, Set<String>> input) {
		Map<String, Set<String>> output = new HashMap<String, Set<String>>();
		for (String key : input.keySet()) {
			Set<String> values = input.get(key);
			for (String value : values) {
				if (output.containsKey(value)) {
					output.get(value).add(key);
				} else {
					Set<String> set = new HashSet<String>();
					set.add(key);
					output.put(value, set);
				}
			}
		}
		return output;
	}

	public static void transformN21(String infile, String outfile,
			String separator1, String separator2) throws IOException {
		Map<String, Set<String>> map = FileManipulator.loadOneToMany(infile,
				separator1, separator2);
		BufferedWriter writer = new BufferedWriter(new FileWriter(outfile));
		for (String s : map.keySet()) {
			Set<String> set = map.get(s);
			for (String s2 : set) {
				writer.write(s + separator1 + s2 + "\n");
				writer.flush();
			}
		}
		writer.close();
	}

	public static void transform12N(String infile, String outfile,
			String separator1, String separator2) throws IOException {
		Map<String, Set<String>> map = FileManipulator.loadOneToMany(infile,
				separator1);
		FileManipulator.outputOneToMany(map, outfile, separator1, separator2);
	}

	public static Set<String> getSet(Map<String, Set<String>> map) {
		Set<String> set = new HashSet<String>();
		for (String s : map.keySet()) {
			set.add(s);
			set.addAll(map.get(s));
		}
		return set;
	}

	public static int getRelationCount(Map<String, Set<String>> map) {
		int count = 0;
		for (String s : map.keySet()) {
			count += map.get(s).size();
		}
		return count;
	}

	public static void generateTop(String folder, String name, String suffix,
			int n, String separator1, String separator2) throws IOException {
		BufferedReader reader = new BufferedReader(new FileReader(folder + name
				+ "." + suffix));
		BufferedWriter writer = new BufferedWriter(new FileWriter(folder + name
				+ "-top" + n + "." + suffix));
		String string;
		while ((string = reader.readLine()) != null) {
			String[] strings = string.split(separator1);
			if (strings == null || strings.length != 2)
				continue;
			StringBuilder sBuilder = new StringBuilder();
			sBuilder.append(strings[0] + separator1);
			if (!strings[1].contains(separator2))
				continue;
			String[] values = strings[1].split(separator2);
			for (int i = 0; i < n; i++) {
				sBuilder.append(values[i] + separator2);
			}
			writer.write(sBuilder.toString().substring(0,
					sBuilder.toString().length() - 1)
					+ "\n");
			writer.flush();
		}
		System.out.println("output " + folder + name + "-top" + n + "."
				+ suffix + " done..." + new Date());
		writer.close();
		reader.close();
	}

	// ---------------------生成的文件是1v1的--------------------
	public void transformIdTitle(String infile, String outfile,
			Map<String, String> map1, Map<String, String> map2,
			String separator1, String separator2) throws IOException {
		BufferedWriter writer = new BufferedWriter(new FileWriter(outfile));
		Map<String, Set<String>> title = FileManipulator.loadOneToMany(infile,
				separator1, separator2);
		for (String s1 : title.keySet()) {
			for (String s2 : title.get(s1)) {
				if (!map1.containsKey(s1) || !map2.containsKey(s2)) {
					continue;
				} else {
					writer.write(map1.get(s1) + "," + map2.get(s2) + "\n");
					writer.flush();
				}
			}
		}
		writer.close();
	}

	// ------------输入是map-----------------
	public static void generateID(String infile, String outfile, String title)
			throws IOException {
		Set<String> set = FileManipulator.loadOneColum(infile, "\t", 0);
		BufferedWriter writer = new BufferedWriter(new FileWriter(outfile));
		int i = 0;
		for (String s : set) {
			writer.write(s + "\t" + title + i + "\n");
			writer.flush();
			i++;
		}
		writer.close();
	}
}
