/** =============================================================================================================== *
 * Copyright 2021 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */
package com.infosys.ainauto.formatconverter.model;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class TokenData {

	public static final String TOKEN_TYPE_LINE = "line";
	public static final String TOKEN_TYPE_CHAR = "char";
	public static final String TOKEN_TYPE_WORD = "word";
	public static final String TOKEN_TYPE_IMAGE = "image";
	public static final String TOKEN_TYPE_LINK = "link";
	
	private String id;
	private String type;
	private String text;
	private String textHtml = null;
	private String uri = "";
	private float[] bbox;
	private List<TokenData> tokenDataList;

	public TokenData(String id, String type, String text, float[] bbox) {
		this.id = id;
		this.type = type;
		this.text = text;
		this.bbox = bbox;
		this.setTokenDataList(new ArrayList<TokenData>());
	}

	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}
	
	public String getType() {
		return type;
	}

	public void setType(String type) {
		this.type = type;
	}

	public String getText() {
		return text;
	}

	public void setText(String text) {
		this.text = text;
	}
	
    public String getTextHtml() {
        return textHtml;
    }

    public void setTextHtml(String textHtml) {
        this.textHtml = textHtml;
    }

	public String getUri() {
		return uri;
	}

	public void setUri(String uri) {
		this.uri = uri;
	}
	
	public float[] getBbox() {
		return bbox;
	}

	public void setBbox(float[] bbox) {
		this.bbox = bbox;
	}

	public List<TokenData> getTokenDataList() {
		return tokenDataList;
	}

	public void setTokenDataList(List<TokenData> tokenDataList) {
		this.tokenDataList = tokenDataList;
	}

	@Override
	public String toString() {
		String text = this.text + Arrays.toString(this.bbox);
		return text;
	}
}
