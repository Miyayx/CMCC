package edu.thu.cmcc.classification.instances;

import edu.thu.cmcc.classification.ClassifyProperties;
import weka.core.Attribute;
import weka.core.Instance;
import weka.core.Instances;
import weka.filters.Filter;
import weka.filters.unsupervised.attribute.NominalToString;

/**
 * 
 * @author Miyayx 读取feature文档，生成Instances
 */
public abstract class InstancesGetter {

	abstract public Instances getInstances(String filename) throws Exception;

	/**
	 * 指定feature列范围，输出Instances
	 * 
	 * @param filename
	 * @param labelIndex
	 *            id列号
	 * @param begin
	 *            feature开始列号
	 * @param end
	 *            feature结束列号
	 * @param classIndex
	 *            class列号
	 * @return
	 * @throws Exception
	 */
	public Instances getInstances(String filename, int labelIndex, int begin,
			int featureCount, int filterIndex, int classIndex) throws Exception {

		int end = begin + featureCount;

		Instances instances = getInstances(filename);

		if (filterIndex > 0 && filterIndex < instances.numAttributes()) {
			System.out.println("FILTER COLOMN:"
					+ instances.attribute(filterIndex).name());
			// 为防止删除前面的会影响index，从后往前删除不是本次迭代的instances
			for (int i = instances.numInstances() - 1; i >= 0; i--) {
				Instance ins = instances.instance(i);
				if (!ins.stringValue(filterIndex).equals(
						ClassifyProperties.OTHER_CLASS))
					instances.delete(i);
			}
		}

		String[] labels = getIDs(instances);
		Attribute labelAttr = instances.attribute(labelIndex);// 文档名列
		Attribute classAttr = instances.attribute(classIndex);// 类别列

		// 从后往前，删除end后的列
		for (int i = instances.numAttributes() - 1; i >= end; i--)
			instances.deleteAttributeAt(i);
		// 从后往前，删除begin前的列
		for (int i = begin - 1; i >= 0; i--)
			instances.deleteAttributeAt(i);

		// 文档名整合回去 // 类别整合回去
		instances.insertAttributeAt(labelAttr, 0);
		instances.insertAttributeAt(classAttr, instances.numAttributes());
		for (int i = 0; i < instances.numInstances(); i++) {
			instances.instance(i).setValue(0, labels[i]);
			instances.instance(i).setValue(classAttr, classAttr.value(i));
		}
		// NominalToString filter = new NominalToString();
		// filter.setInputFormat(instances);
		// instances = Filter.useFilter(instances, filter);

		System.out.println("Iteration " + ClassifyProperties.Iteration_ID
				+ ": Classify" + instances.numInstances() + " instances");
		return instances;
	}

	/**
	 * 指定feature列范围，输出Instances
	 * 
	 * @param filename
	 * @param labelIndex
	 *            id列号
	 * @param begin
	 *            feature开始列号
	 * @param end
	 *            feature结束列号
	 * @return
	 * @throws Exception
	 */
	public Instances getInstances(String filename, int labelIndex, int begin,
			int featureCount, int filterIndex) throws Exception {

		int end = begin + featureCount;
		Instances instances = getInstances(filename);

		// col
		if (filterIndex > 0 && filterIndex < instances.numAttributes()) {
			System.out.println("FILTER COLOMN:"
					+ instances.attribute(filterIndex).name());
			// 为防止删除前面的会影响index，从后往前删除不是本次迭代的instances
			for (int i = instances.numInstances() - 1; i >= 0; i--) {
				Instance ins = instances.instance(i);
				if (!ins.stringValue(filterIndex).equals(
						ClassifyProperties.OTHER_CLASS))
					instances.delete(i);
			}
		}

		String[] labels = getIDs(instances);
		Attribute labelAttr = instances.attribute(labelIndex);// 文档名列

		// 从后往前，删除end后的列
		for (int i = instances.numAttributes() - 1; i >= end; i--)
			instances.deleteAttributeAt(i);
		// 从后往前，删除begin前的列
		for (int i = begin - 1; i >= 0; i--)
			instances.deleteAttributeAt(i);

		// 文档名整合回去
		instances.insertAttributeAt(labelAttr, 0);

		for (int i = 0; i < instances.numInstances(); i++) {

			instances.instance(i).setValue(0, labels[i]);
		}

		// NominalToString filter = new NominalToString();
		// //filter.setAttributeIndexes("sample");
		// String[] options= new String[2];
		// options[0]="-R";
		// options[1]="1";
		// filter.setInputFormat(instances);
		// instances = Filter.useFilter(instances, filter);
		System.out.println("Iteration " + ClassifyProperties.Iteration_ID
				+ ": Cluster" + instances.numInstances() + " instances");
		return instances;
	}

	/**
	 * 获得文档名（IDs），在instance的第一个attribute
	 * 
	 * @param instances
	 * @return
	 */
	public static String[] getIDs(Instances instances) {
		double sum = instances.numInstances(); // 样本数
		String[] names = new String[(int) (sum)];
		for (int i = 0; i < sum; i++) {
			names[i] = instances.instance(i).toString(0);
			if (names[i].contains("'"))
				names[i] = names[i].replace("'", "");
		}
		
		return names;
	}

}
