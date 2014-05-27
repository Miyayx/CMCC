package classification_old;

import java.io.*;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;

import com.hp.hpl.jena.ontology.*;
import com.hp.hpl.jena.rdf.model.ModelFactory;

import edu.thu.cmcc.basic.FileManipulator;

public class Preprocessing {

	static double threshold = 0.85;

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

	public static void generateCorrectClusterData(String clusterFile,
			Map<String, String> instanceConceptTaxonomy, String correctFile,
			String wrongFile) throws IOException {
		BufferedWriter writer = new BufferedWriter(new FileWriter(correctFile));
		BufferedWriter writer2 = new BufferedWriter(new FileWriter(wrongFile));
		Map<String, String> instanceClusterMap = FileManipulator.loadOneToOne(
				clusterFile, "\t\t", 0);
		Map<String, Set<String>> clusterInstanceMap = new HashMap<String, Set<String>>();
		for (String instance : instanceClusterMap.keySet()) {
			String cluster = instanceClusterMap.get(instance);
			Set<String> instanceSet = clusterInstanceMap.get(cluster);
			if (instanceSet == null) {
				instanceSet = new HashSet<String>();
			}
			instanceSet.add(instance);
			clusterInstanceMap.put(cluster, instanceSet);
		}
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
		System.out.println(clusterConceptMap);
		Map<String, String> clusterCorrectConcept = new HashMap<String, String>();
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
			System.out.println(cluster + ":" + correctConcept);
		}
		for (String cluster : clusterInstanceMap.keySet()) {
			for (String instance : clusterInstanceMap.get(cluster)) {
				if (!instanceConceptTaxonomy.containsKey(instance)) {
					continue;
				}
				String concept = instanceConceptTaxonomy.get(instance);
				if (concept.equals(clusterCorrectConcept.get(cluster))) {
					writer.write(cluster + "\t\t" + instance + "\t\t" + concept
							+ "\n");
					writer.flush();
				} else {
					writer2.write(instance + "\n");
					writer2.flush();
				}
			}
		}
		writer.close();
		writer2.close();

	}

	public static void run(String clusterFile) throws IOException {
		// TODO Auto-generated method stub
		Map<String, Set<String>> map = FileManipulator.loadOneToMany(
				"etc/ontology.txt", "\t\t", ";;;");
		Map<String, String> instanceConceptTaxonomy = new HashMap<String, String>();
		for (String key : map.keySet()) {
			for (String value : map.get(key)) {
				instanceConceptTaxonomy.put(value, key);
			}
		}
		BufferedWriter writer = new BufferedWriter(new FileWriter(
				"etc/taxonomy.txt"));
		writer.write("Root\t\t");
		for (String key : map.keySet()) {
			writer.write(key + ";;;");
		}
		writer.write("\n");
		writer.flush();

		Preprocessing.generateCorrectClusterData(clusterFile,
				instanceConceptTaxonomy, "etc/correctInstance.txt",
				"etc/wrongInstance.txt");

	}

	/**
	 * @param args
	 * @throws IOException
	 */
	public static void main(String[] args) throws IOException {
		// TODO Auto-generated method stub
		Map<String, Set<String>> map = FileManipulator.loadOneToMany(
				"etc/ontology.txt", "\t\t", ";;;");
		Map<String, String> instanceConceptTaxonomy = new HashMap<String, String>();
		for (String key : map.keySet()) {
			for (String value : map.get(key)) {
				instanceConceptTaxonomy.put(value, key);
			}
		}
		BufferedWriter writer = new BufferedWriter(new FileWriter(
				"etc/taxonomy.txt"));
		writer.write("Root\t\t");
		for (String key : map.keySet()) {
			writer.write(key + ";;;");
		}
		writer.write("\n");
		writer.flush();
		String clusterFile = "etc/ClusterResult1_f1.txt";
		Preprocessing.generateCorrectClusterData(clusterFile,
				instanceConceptTaxonomy, "etc/correctInstance.txt",
				"etc/wrongInstance.txt");
	}

}
