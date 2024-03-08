/** =============================================================================================================== *
 * Copyright 2021 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */

package com.infosys.ainauto.formatconverter.model;

import java.util.Map;

public class SwitchData {

	private String fromFile;
	private String toFile;
	private String hocrFile;
	private String toDir;
	private int dpi;
	private String pages;
	private String watermarktext;
	private int timeout;
	private float pageWidth;
	private float pageHeight;
	private boolean plotBbox;
	private String imageFormats;
	private String angles;
	private boolean saveResource;
	
	private Map<String,int[]> bboxNameValueMap;

	public String getFromFile() {
		return fromFile;
	}

	public void setFromFile(String fromFile) {
		this.fromFile = fromFile;
	}

	public String getToFile() {
		return toFile;
	}

	public void setToFile(String toFile) {
		this.toFile = toFile;
	}

	public String getHocrFile() {
		return hocrFile;
	}

	public void setHocrFile(String hocrFile) {
		this.hocrFile = hocrFile;
	}

	public String getToDir() {
		return toDir;
	}

	public void setToDir(String toDir) {
		this.toDir = toDir;
	}

	public int getDpi() {
		return dpi;
	}

	public void setDpi(int dpi) {
		this.dpi = dpi;
	}

	public String getPages() {
		return pages;
	}

	public void setPages(String pages) {
		this.pages = pages;
	}

	public String getWatermarktext() {
		return watermarktext;
	}

	public void setWatermarktext(String watermarktext) {
		this.watermarktext = watermarktext;
	}

	public int getTimeout() {
		return timeout;
	}

	public void setTimeout(int timeout) {
		this.timeout = timeout;
	}

	public Map<String,int[]> getBboxNameValueMap() {
		return bboxNameValueMap;
	}

	public void setBboxNameValueMap(Map<String,int[]> bboxNameValueMap) {
		this.bboxNameValueMap = bboxNameValueMap;
	}

	public float getPageWidth() {
		return pageWidth;
	}

	public void setPageWidth(float pageWidth) {
		this.pageWidth = pageWidth;
	}

	public float getPageHeight() {
		return pageHeight;
	}

	public void setPageHeight(float pageHeight) {
		this.pageHeight = pageHeight;
	}

	public boolean isPlotBbox() {
		return plotBbox;
	}

	public void setPlotBbox(boolean plotBbox) {
		this.plotBbox = plotBbox;
	}

	public String getImageFormats() {
		return imageFormats;
	}

	public void setImageFormats(String imageFormats) {
		this.imageFormats = imageFormats;
	}

	public String getAngles() {
		return angles;
	}

	public void setAngles(String angles) {
		this.angles = angles;
	}

	public boolean isSaveResource() {
		return saveResource;
	}

	public void setSaveResource(boolean saveResource) {
		this.saveResource = saveResource;
	}

}
