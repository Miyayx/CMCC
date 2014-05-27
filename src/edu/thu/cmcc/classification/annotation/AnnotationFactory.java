package edu.thu.cmcc.classification.annotation;

public class AnnotationFactory {

	static public Annotation create(int type){
		switch(type){
		case AnnotationType.MANUAL_ANOTATION:
			return new ManualAnotation();
		case AnnotationType.FILTER_ANOTATION:
			return new FilterAnotation();
		default:
			return new AutoAnotation();
		
		}
	}
}
