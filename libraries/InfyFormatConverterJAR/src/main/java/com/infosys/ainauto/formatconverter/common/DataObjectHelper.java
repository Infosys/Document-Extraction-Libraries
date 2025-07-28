/** =============================================================================================================== *
 * Copyright 2023 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */
package com.infosys.ainauto.formatconverter.common;

import java.util.List;

import javax.json.Json;
import javax.json.JsonArrayBuilder;
import javax.json.JsonObjectBuilder;

import com.infosys.ainauto.formatconverter.model.PageData;
import com.infosys.ainauto.formatconverter.model.TokenData;

/**
 * Utility class for data transformations (from one type to another type).
 *
 */
public class DataObjectHelper {

	public static String getJsonString(List<PageData> pageDataList, float scaleFactor, int decimals) {
		JsonArrayBuilder pageJAB = Json.createArrayBuilder();
		for (PageData pageData : pageDataList) {
			JsonObjectBuilder pageJOB = Json.createObjectBuilder();
			pageJOB.add("page", pageData.getPage());
			pageJOB.add("width", pageData.getWidth());
			pageJOB.add("height", pageData.getHeight());
			pageJOB.add("bbox", "X1,Y1,X2,Y2");

			JsonArrayBuilder lineJAB = Json.createArrayBuilder();
			for (TokenData lineTokenData : pageData.getTokenDataList()) {
				JsonObjectBuilder lineJOB = getTokenJOB(lineTokenData, scaleFactor, decimals);
				JsonArrayBuilder charJAB = Json.createArrayBuilder();
				for (TokenData charTokenData : lineTokenData.getTokenDataList()) {
					JsonObjectBuilder charJOB = getTokenJOB(charTokenData, scaleFactor, decimals);
					charJAB.add(charJOB);
				}
				lineJOB.add("tokens", charJAB);
				lineJAB.add(lineJOB);
			}
			pageJOB.add("tokens", lineJAB.build());
			pageJAB.add(pageJOB);
		}
		return CommonUtil.getPrettyJson(pageJAB.build());
	}

	private static JsonObjectBuilder getTokenJOB(TokenData tokenData, float scaleFactor, int decimals) {
		JsonObjectBuilder tokenJOB = Json.createObjectBuilder();
		tokenJOB.add("id", tokenData.getId());
		tokenJOB.add("type", tokenData.getType());
		tokenJOB.add("text", tokenData.getText());
		if (tokenData.getTextHtml() != null) {
			tokenJOB.add("textHtml", tokenData.getTextHtml());
		} else {
			tokenJOB.addNull("textHtml");
		}
		tokenJOB.add("uri", tokenData.getUri());
		JsonArrayBuilder bboxJAB = Json.createArrayBuilder();

		for (float x : tokenData.getBbox()) {
			// In Java, when you add a float to a JsonArrayBuilder, it is automatically
			// converted to a double with full precision.
			double parsedNumber = Double.parseDouble(String.format("%." + decimals + "f", scaleFactor * x));
			bboxJAB.add(parsedNumber);
		}
		tokenJOB.add("bbox", bboxJAB.build());
		return tokenJOB;
	}
}
