/** =============================================================================================================== *
 * Copyright 2021 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */
package com.infosys.ainauto.ocrengine.model;

public class SwitchData {

	private String fromFile;
	private String language;
	private String ocrFormat;
	private String toDir;
	private String modelDirPath;
	private String pageSegMode;

	public String getFromFile() {
		return fromFile;
	}

	public void setFromFile(String fromFile) {
		this.fromFile = fromFile;
	}

	public String getLanguage() {
		return language;
	}

	public void setLanguage(String toFile) {
		this.language = toFile;
	}

	public String getOcrFormat() {
		return ocrFormat;
	}

	public void setOcrFormat(String ocrFormat) {
		this.ocrFormat = ocrFormat;
	}

	public String getToDir() {
		return toDir;
	}

	public void setToDir(String toDir) {
		this.toDir = toDir;
	}

	public String getModelDirPath() {
		return modelDirPath;
	}

	public void setModelDirPath(String modelDirPath) {
		this.modelDirPath = modelDirPath;
	}

	public String getPageSegMode() {
		return pageSegMode;
	}

	public void setPageSegMode(String pageSegMode) {
		this.pageSegMode = pageSegMode;
	}
}
