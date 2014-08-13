package edu.thu.cmcc.classification.annotation;

public class AnnotationFactory {

	static public Annotation create(int type) {
		switch (type) {
		case AnnotationType.MANUAL_ANOTATION:
			return new ManualAnotation();
		case AnnotationType.MANUAL_ALL_ANOTATION:
			return new ManualAllAnotation();
		case AnnotationType.MANUAL_ONFILE_ANOTATION:
			return new ManualRecordAnnotation();
		default:
			return new AutoAnotation();

		}
	}
}
