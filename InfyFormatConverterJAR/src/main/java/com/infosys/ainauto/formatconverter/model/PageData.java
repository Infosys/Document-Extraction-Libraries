/** =============================================================================================================== *
 * Copyright 2021 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */

package com.infosys.ainauto.formatconverter.model;

import java.util.List;

public class PageData {

	private int page;
	private float width;
	private float height;
	private List<TokenData> tokenDataList;

	public PageData(int page, float width, float height) {
		super();
		this.page = page;
		this.width = width;
		this.height = height;
	}

	public int getPage() {
		return page;
	}

	public void setPage(int page) {
		this.page = page;
	}

	public float getWidth() {
		return width;
	}

	public void setWidth(float width) {
		this.width = width;
	}

	public float getHeight() {
		return height;
	}

	public void setHeight(float height) {
		this.height = height;
	}

	public List<TokenData> getTokenDataList() {
		return tokenDataList;
	}

	public void setTokenDataList(List<TokenData> tokenDataList) {
		this.tokenDataList = tokenDataList;
	}
}
