package edu.thu.cmcc.classification.annotation;

import java.io.BufferedWriter;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;

import com.hp.hpl.jena.ontology.Individual;
import com.hp.hpl.jena.ontology.OntClass;
import com.hp.hpl.jena.ontology.OntModel;
import com.hp.hpl.jena.ontology.OntModelSpec;
import com.hp.hpl.jena.rdf.model.ModelFactory;

import edu.thu.cmcc.basic.CSVFileIO;
import edu.thu.cmcc.basic.FileManipulator;
import edu.thu.cmcc.classification.ClassifyProperties;

/**
 * 
 * @author Miyayx 原Preprocessing.java
 * 之前人工标注过一些文件，从中筛选出标注数据集
 * 最终返回标注数据map，key是文档id，value是class
 */
public class FilterAnotation implements Annotation {

	/**
	 * 读取人工标注数据文件
	 * 
	 * @param ontPath
	 * @param outPath
	 * @throws IOException
	 */
	@SuppressWarnings("unchecked")
	public static void readOntology(String ontPath, String outPath)
			throws IOException {
		OntModel model = ModelFactory.createOntologyModel(OntModelSpec.OWL_MEM);//
		model.read(new FileInputStream(ontPath), "");
		Iterator<OntClass> iterator = model.listClasses();
		Map<String, Set<String>> map = new HashMap<String, Set<String>>();
		while (iterator.hasNext()) {
			OntClass ontClass = iterator.next();
			Iterator<Individual> iteratorInstance = (Iterator<Individual>) ontClass
					.listInstances();
			String conceptID = ontClass.toString();
			conceptID = conceptID
					.substring("http://mobile.keg.cs.tsinghua.edu.cn/".length());
			Set<String> set = new HashSet<String>();
			while (iteratorInstance.hasNext()) {
				String instance = iteratorInstance.next().toString();
				instance = instance
						.substring("http://mobile.keg.cs.tsinghua.edu.cn/"
								.length());
				set.add(instance);
			}
			if (set.size() > 0)
				map.put(conceptID, set);
		}
		FileManipulator.outputOneToMany(map, outPath, "\t\t", ";;;");
	}

	/**
	 * 生成标注数据
	 * 
	 * @param clusterFile
	 * @param instanceConceptTaxonomy
	 * @throws IOException
	 */
	public static Map<String, String> generateLabeledData(
			Map<String, String> clusterMap,
			Map<String, String> instanceConceptTaxonomy) throws IOException {
		double class1SizeLimit = instanceConceptTaxonomy.size()
				* class1SizePercent;
		if (class1SizeLimit < minClass1SizeLimit)
			class1SizeLimit = minClass1SizeLimit;// 至少要标20个
		Map<String, String> labeledInstanceSet = new HashMap<String, String>();

		Set<String> conceptSet = new HashSet<String>();
		for (String instance : instanceConceptTaxonomy.keySet()) {
			conceptSet.add(instanceConceptTaxonomy.get(instance));
		}
		// 得到cluster和instance的对应
		Map<String, Set<String>> clusterInstanceMap = new HashMap<String, Set<String>>();
		for (String instance : clusterMap.keySet()) {
			String cluster = clusterMap.get(instance);
			Set<String> instanceSet = clusterInstanceMap.get(cluster);
			if (instanceSet == null) {
				instanceSet = new HashSet<String>();
			}
			instanceSet.add(instance);
			clusterInstanceMap.put(cluster, instanceSet);
		}

		if (classNumber == 1) {
			// 删除数量不足平均的cluster
			Set<String> rmClusterSet = new HashSet<String>();
			for (String cluster : clusterInstanceMap.keySet()) {
				double avgSize = clusterMap.size() * 1.0
						/ clusterInstanceMap.size();
				if (clusterInstanceMap.get(cluster).size() < avgSize) {
					rmClusterSet.add(cluster);
				}
			}
			for (String rmCluster : rmClusterSet) {
				clusterInstanceMap.remove(rmCluster);
			}
		}
		// 得到cluster中concept的出现次数
		Map<String, Map<String, Integer>> clusterConceptMap = new HashMap<String, Map<String, Integer>>();
		for (String cluster : clusterInstanceMap.keySet()) {
			Map<String, Integer> countMap = new HashMap<String, Integer>();
			for (String instance : clusterInstanceMap.get(cluster)) {
				String concept = instanceConceptTaxonomy.get(instance);
				if (concept == null) {
					// System.out.println(instance + " is not in taxonomy");
					continue;
				}
				if (countMap.containsKey(concept)) {
					countMap.put(concept, countMap.get(concept) + 1);
				} else {
					countMap.put(concept, 1);
				}
			}
			clusterConceptMap.put(cluster, countMap);
		}
		// System.out.println(clusterConceptMap);
		// 得到每个cluster对应的占比最大的concept，和该concept占的比重
		Map<String, String> clusterCorrectConcept = new HashMap<String, String>();
		Map<String, Double> clusterCorrectPercentage = new HashMap<String, Double>();
		for (String cluster : clusterConceptMap.keySet()) {
			int max = 0;
			String correctConcept = null;
			for (String concept : clusterConceptMap.get(cluster).keySet()) {
				if (clusterConceptMap.get(cluster).get(concept) > max) {
					max = clusterConceptMap.get(cluster).get(concept);
					correctConcept = concept;
				}
			}
			clusterCorrectConcept.put(cluster, correctConcept);
			Double percentage = new Double(max * 1.0
					/ clusterInstanceMap.get(cluster).size());
			clusterCorrectPercentage.put(cluster, percentage);
		}
		// 找到classNumber个聚类最好的cluster
		Set<String> bestClusters = new HashSet<String>();
		Set<String> conceptsForBestClusters = new HashSet<String>();
		Set<String> doneClusterSet = new HashSet<String>();
		while (bestClusters.size() < classNumber
				&& doneClusterSet.size() < clusterCorrectConcept.size()) {
			double maxPercentage = 0.0;
			String bestCluster = null;
			String conceptOfBestCluster = null;
			for (String cluster : clusterCorrectConcept.keySet()) {
				String concept = clusterCorrectConcept.get(cluster);
				if (conceptsForBestClusters.contains(concept)) {
					doneClusterSet.add(cluster);
					continue;
				}
				if (clusterCorrectPercentage.get(cluster) > maxPercentage) {
					maxPercentage = clusterCorrectPercentage.get(cluster);
					bestCluster = cluster;
					conceptOfBestCluster = concept;
				}
			}

			bestClusters.add(bestCluster);
			conceptsForBestClusters.add(conceptOfBestCluster);
			doneClusterSet.add(bestCluster);
		}
		// 把上面的bestclusters中的instance加入标注范围
		int class1Size = 0;
		for (String cluster : bestClusters) {
			int labelSize = 0;
			for (String instance : clusterInstanceMap.get(cluster)) {
				if (!instanceConceptTaxonomy.containsKey(instance)) {
					continue;
				}
				String concept = instanceConceptTaxonomy.get(instance);
				if (concept.equals(clusterCorrectConcept.get(cluster))) {
					labeledInstanceSet.put(instance, concept);
					labelSize++;
					if (labelSize > class1SizeLimit / bestClusters.size())
						break;
				}
			}
			class1Size += labelSize;
		}
		// 在其他cocnept中抽取一部分非a非b的instance标注为others
		List<String> otherInstances = new LinkedList<String>();
		int count = 0;
		for (String instance : instanceConceptTaxonomy.keySet()) {
			String concept = instanceConceptTaxonomy.get(instance);
			if (conceptsForBestClusters.contains(concept)) {
				continue;
			}
			otherInstances.add(instance);
		}
		// System.out.println(otherInstances.size());
		Random rdm = new Random();
		Set<Integer> doneIndex = new HashSet<Integer>();
		double class0Size = class0SizePercent * class1Size;
		while (count < class0Size && count < otherInstances.size()) {
			int index = Math.abs(rdm.nextInt() % otherInstances.size());
			if (doneIndex.contains(index)) {
				continue;
			}
			doneIndex.add(index);
			labeledInstanceSet.put(otherInstances.get(index),
					ClassifyProperties.OTHER_CLASS);
			count++;
		}

		return labeledInstanceSet;

	}

	@Override
	public Map<String, String> annotation(String clusterFile, int clusterIndex)
			throws IOException {
		// TODO Auto-generated method stub
		Map<String, Set<String>> map = FileManipulator.loadOneToMany(
				"etc/ontology2.txt", "\t\t", ";;;");
		Set<String> allInstanceSet = FileManipulator.loadOneColum("etc/samples"
				+ ClassifyProperties.Iteration_ID + ".txt", "", -1);
		Map<String, String> instanceConceptTaxonomy = new HashMap<String, String>();
		for (String key : map.keySet()) {
			for (String value : map.get(key)) {
				if (!allInstanceSet.contains(value))
					continue;
				instanceConceptTaxonomy.put(value, key);
			}
		}

		Map<String, String> clusterMap = FileManipulator.loadOneToOne(
				clusterFile, ",", 0, clusterIndex);

		return FilterAnotation.generateLabeledData(clusterMap, instanceConceptTaxonomy);

	}

	@Override
	public Map<String, String> annotation(String clusterfile)
			throws IOException {

		return this.annotation(clusterfile, 1);
	}

}
