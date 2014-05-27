package edu.thu.cmcc.classification.throwable;

/**
 * 
 * @author Miyayx
 * 自定义异常
 * 测试准确率过低时抛出
 */
public class LowAccuracyException extends Exception {

	public LowAccuracyException() {
		super();
	}

	public LowAccuracyException(String msg) {
		super(msg);
	}

}
