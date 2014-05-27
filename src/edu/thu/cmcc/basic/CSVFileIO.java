package edu.thu.cmcc.basic;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

/**
 * CSV文件处理的一些函数
 * 
 * @author Miyayx
 * 
 */
public class CSVFileIO {

	List<String> fields = null;//表头
	Map<String, List<String>> content = null;// 以第一列为key，整行（包括第一列）的内容为value
	String separator = ",";
	int columnN = 0;// 列数
	int rowN = 0;// 行数

	public CSVFileIO() {
		content = new HashMap<String, List<String>>();
	}

	public String getSeparator() {
		return separator;
	}

	public void setSeparator(String separator) {
		this.separator = separator;
	}

	public int getColumnN() {
		return columnN;
	}

	public void setColumnN(int columnN) {
		this.columnN = columnN;
	}

	public int getRowN() {
		return rowN;
	}

	public void setRowN(int rowN) {
		this.rowN = rowN;
	}

	public List<String> getFields() {
		return fields;
	}

	public void setFields(List<String> fields) {
		this.fields = fields;
	}

	/**
	 * 读取数据
	 * 
	 * @param fn
	 */
	public void load(String fn, boolean header) {
		load(fn, this.separator, header);
	}

/**
 * 读取数据
 * @param fn
 * @param separator  分隔符
 * @param header     是否有表头
 */
	public void load(String fn, String separator, boolean header) {
		this.separator = separator;

		List<String> lines = FileUtils.readFileByLines(fn);

		if (header) {
			fields = new ArrayList(Arrays.asList(lines.get(0).split(
					this.separator)));
			lines.remove(0);
		}

		int maxColumnN = 0;
		List<String> line = null;
		for (String l : lines) {
			line = new ArrayList(Arrays.asList(l.trim().split(separator)));
			content.put(line.get(0), line);
			maxColumnN = line.size() > maxColumnN ? line.size() : maxColumnN;
			if (line.size() < maxColumnN) {
				while (line.size() < maxColumnN)
					line.add("");
			}
		}
		// this.columnN = line == null ? 0 : line.size();
		this.columnN = maxColumnN;
		this.rowN = line == null ? 0 : lines.size();
	}
	
	/**
	 * 添加列的操作
	 * @param colname  列名
	 * @param map      要添加的数据，key：id，value：对应的此列内容
	 */
	public void column(String colname, Map<String, String> map) {
		if (fields.contains(colname))//如果此列已存在，update
			update(fields.indexOf(colname), map);
		else if (getRowN() == 0)     //如果是个空文件，添加到第二列，第一列是id
			addColumn(colname, 2, map);
		else
			addColumn(colname, map);//添加到后一列
	}

	/**
	 * 改变某个单元格的内容
	 * 
	 * @param key
	 *            行标志
	 * @param column
	 *            列数
	 * @param newString
	 *            新内容
	 */
	public void update(String key, int colIndex, String newString) {

		List<String> value = (List<String>) content.get(key);
		if (value == null) {
			value = new ArrayList<String>();
			value.add(key);
		}
		// System.out.println(value + " " + key + " " + newString);
		if (colIndex < value.size())
			value.set(colIndex, newString);
		else
			value.add(colIndex, newString);

		content.put(key, value);
	}

	public void update(int colIndex, Map<String, String> map) {
		for (String key : content.keySet()) {
			if (map.containsKey(key))
				this.update(key, colIndex, map.get(key).toString());
			else
				this.update(key, colIndex, "");
		}
	}

	/**
	 * 加一个空的列
	 * @param colName
	 */
	public void addEmptyColumn(String colName) {
		Map<String, String> map = new HashMap<String, String>();
		for (String key : content.keySet())
			map.put(key, "");
		this.addColumn(colName, map);
	}

	public void addColumn(String colName, Map<String, String> newCol) {
		addColumn(colName, this.columnN, newCol);
	}

	/**
	 * 添加新一列，加在原有内容后一列
	 * @param newCol
	 *            key：第一列 value：对应的新一列内容
	 */
	public void addColumn(String colName, int colindex,
			Map<String, String> newCol) {

		if (newCol == null || newCol.size() == 0) {
			System.out.println("Null Column Map");
			return;
		}
		if (colindex < columnN) {
			System.out.println("Column " + colindex
					+ " has already had data, use update");
			return;
		}

		if (fields.size() == 0 || fields == null)
			fields.add("samples");
		while (fields.size() < colindex)
			fields.add("");
		fields.add(colName);

		Set<String> keys = new HashSet<String>(newCol.keySet());
		keys.addAll(content.keySet());
		for (String key : keys) {
			List<String> value = (ArrayList<String>) content.get(key);
			if (value == null) {
				value = new ArrayList<String>();
				value.add(key);
			}
			while (value.size() < colindex) {
				value.add("");
			}
			if (newCol.containsKey(key))
				value.add((String) newCol.get(key));
			else
				value.add("");
			content.put(key, value);
			this.columnN = value.size();
		}

	}

	public void deleteColumn(int column) {

		for (Entry pairs : content.entrySet()) {
			String key = pairs.getKey().toString();
			List<String> value = (List<String>) pairs.getValue();
			value.remove(column);
			content.put(key, value);
		}
	}

	public void addRow() {

	}

	public void deleteRow(String key) {
		content.remove(key);
	}

	/**
	 * 写入文件
	 * 
	 * @param fn
	 * @param separator
	 * @param map
	 * @throws IOException
	 */
	public void write(String fn, String separator, boolean header)
			throws IOException {

		write(fn, separator, header, true, 0);// 默认以key排序

	}

	/**
	 * 写入文件
	 * 
	 * @param fn
	 *            文件名
	 * @param separator
	 *            分隔符
	 * @param sorted
	 *            是否排序
	 * @param sortedindex
	 *            按哪一列内容排序
	 * @throws IOException
	 */
	public void write(String fn, String separator, boolean header,
			boolean sorted, final int sortedindex) throws IOException {

		// 先根据类别排序
		ArrayList<Entry<String, List<String>>> l = new ArrayList<Entry<String, List<String>>>(
				content.entrySet());

		Collections.sort(l, new Comparator<Map.Entry<String, List<String>>>() {
			public int compare(Map.Entry<String, List<String>> o1,
					Map.Entry<String, List<String>> o2) {
				// 中文在前
				return (o2.getValue().get(sortedindex)).toString().compareTo(
						o1.getValue().get(sortedindex).toString());
				
				// 中文在后
				// return (o1.getValue().get(sortedindex)).toString().compareTo(
				// o2.getValue().get(sortedindex).toString()); 
			}
		});

		// 写入文件
		BufferedWriter bw = new BufferedWriter(new FileWriter(fn));
		if (header) {
			for (String v : fields.subList(0, fields.size() - 1))
				bw.write(v + ",");
			bw.write(fields.get(fields.size() - 1) + "\r\n");
		}

		for (Map.Entry pairs : l) {
			String key = (String) pairs.getKey();
			List<String> value = (List<String>) pairs.getValue();
			for (String v : value.subList(0, value.size() - 1))
				bw.write(v + ",");
			bw.write(value.get(value.size() - 1) + "\r\n");

		}
		bw.close();
	}

}
