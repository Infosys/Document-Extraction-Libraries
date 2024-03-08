/** =============================================================================================================== *
 * Copyright 2021 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */

package com.infosys.ainauto.formatconverter.service;

import java.io.IOException;
import java.io.Writer;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.common.PDRectangle;
import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.pdfbox.text.TextPosition;

import com.infosys.ainauto.formatconverter.common.CommonUtil;
import com.infosys.ainauto.formatconverter.model.PageData;
import com.infosys.ainauto.formatconverter.model.TokenData;

/**
 * Class that extends PDFTextStripper and contains logic to get coordinates of
 * printed text in native PDF
 *
 */
public class PdfTextStripperCustom extends PDFTextStripper {

	private PDDocument pdDocument;
	private int pageCounter = 1;
	private int lineTextCounter = 0;
	private List<PageData> pageDataList = new ArrayList<>();
	private static final float SAME_DIR_MAX_GAP = 10f;
	private static final float OPP_DIR_MAX_GAP = -10f;

	public List<PageData> getPageDataList() {
		return pageDataList;
	}

	public PdfTextStripperCustom() throws IOException {
	}

	private float[] createBbox(TextPosition textPosition) {
		float[] bbox = { 0, 0, 0, 0 }; // X1, X2, Y1, Y2

		// TODO Mohan - The bbox calculation logic may need fine-tuning after testing on
		// real documents

		bbox[0] = textPosition.getXDirAdj();
		// Y1 value includes height hence subtract height to get Y1 as top coordinate of
		// bbox
		bbox[1] = (textPosition.getYDirAdj() - textPosition.getFontSize());
//		bbox[1] = (textPosition.getYDirAdj());

//		bbox[2] = (textPosition.getXDirAdj() + textPosition.getWidth());
		bbox[2] = (textPosition.getEndX());

		bbox[3] = (textPosition.getYDirAdj());
//		bbox[3] = (textPosition.getEndY());

//		String text = textPosition.getUnicode();
//		text += ",";
//		text += "X=" + textPosition.getX();
//		text += ",Y=" + textPosition.getY();
//		text += ",XDirAdj=" + textPosition.getXDirAdj();
//		text += ",YDirAdj=" + textPosition.getYDirAdj();
//		text += ",EndX=" + textPosition.getEndX();
//		text += ",EndY=" + textPosition.getEndY();
//
//		text += ",Width=" + textPosition.getWidth();
//		text += ",Height=" + textPosition.getHeight();
//
//		text += ",WidthDirAdj=" + textPosition.getWidthDirAdj();
//		text += ",HeightDir=" + textPosition.getHeightDir();
//
//		text += "";

//		System.out.println(text);

		return bbox;
	}

	@Override
	public void writeText(PDDocument doc, Writer outputStream) throws IOException {
		this.pdDocument = doc;
		this.pageCounter = this.getStartPage();
		addNewPageToList(pageDataList);
		super.writeText(doc, outputStream);
	}

	@Override
	protected void endPage(PDPage page) throws IOException {
		if (pageCounter < this.getEndPage()) {
			pageCounter++;
			addNewPageToList(pageDataList);
			// Reset line counter after each page
			lineTextCounter = 0;
		}
		super.endPage(page);
	}

	private void addNewPageToList(List<PageData> pageDataList) {
		PDRectangle pageDimensions = this.pdDocument.getPage(this.pageCounter - 1).getBBox();
		float pageWidth = CommonUtil.roundOff(pageDimensions.getWidth(), 4);
		float pageHeight = CommonUtil.roundOff(pageDimensions.getHeight(), 4);
		PageData pageData = new PageData(pageCounter, pageWidth, pageHeight);
		pageData.setTokenDataList(new ArrayList<TokenData>());
		pageDataList.add(pageData);
	}

	@Override
	protected void writeString(String string, List<TextPosition> textPositionList) throws IOException {
		// Do clustering to separate out portions of lines that are not supposed to be together
		List<List<TextPosition>> textPositionClusterList = new ArrayList<>();
		textPositionClusterList.add(new ArrayList<TextPosition>());
		float lastX2 = -1;
		for (TextPosition textPosition : textPositionList) {
			if (lastX2 > 0) {
				float diff = textPosition.getX() - lastX2;
				if ((diff >= 0 && diff >= SAME_DIR_MAX_GAP) || (diff < 0 && diff <= OPP_DIR_MAX_GAP)) {
					// Create new cluster and add to it
					List<TextPosition> newList = new ArrayList<>();
					newList.add(textPosition);
					textPositionClusterList.add(newList);
				} else {
					// Add to existing cluster
					textPositionClusterList.get(textPositionClusterList.size() - 1).add(textPosition);
				}
			} else {
				// Add to existing cluster
				textPositionClusterList.get(textPositionClusterList.size() - 1).add(textPosition);
			}
			lastX2 = textPosition.getEndX();
		}

		for (List<TextPosition> textPositions : textPositionClusterList) {
			// Increment counter
			lineTextCounter++;
			String lineId = String.format("P%d_L%d", pageCounter, lineTextCounter);
			// Step1 - Handle characters first
			List<TokenData> charTokenDataList = new ArrayList<>();
			int charTextCounter = 0;
			for (TextPosition textPosition : textPositions) {
				charTextCounter++;

//				System.out.println(textPosition.getUnicode() + " [(X=" + textPosition.getXDirAdj() + ",Y="
//						+ textPosition.getYDirAdj() + ") height=" + textPosition.getHeightDir() + " width="
//						+ textPosition.getWidthDirAdj() + "]");
//				System.out.println(
//						textPosition.getUnicode() + "," + textPosition.getXDirAdj() + "," + textPosition.getYDirAdj() + ","
//								+ textPosition.getHeightDir() + "," + textPosition.getWidthDirAdj());
				float[] bbox = createBbox(textPosition);
				TokenData tokenData = new TokenData(String.format("%s_C%d", lineId, charTextCounter),
						TokenData.TOKEN_TYPE_CHAR, textPosition.getUnicode(), bbox);
				charTokenDataList.add(tokenData);
			}

			float[] bbox = { 0, 0, 0, 0 };
			int count = textPositions.size();

//			System.out.println(textPositions.get(0).getX() + "," + textPositions.get(0).getY());
//			System.out.println(textPositions.get(0).getEndX() + "," + textPositions.get(0).getEndY());
//			System.out.println(textPositions.get(0).getXDirAdj() + "," + textPositions.get(0).getYDirAdj());
//			System.out.println("---");
//			System.out.println(textPositions.get(0).getWidth() + "," + textPositions.get(0).getHeight());
//			System.out.println("---");
//			System.out.println(textPositions.get(0).getTextMatrix().getTranslateX() + ","
//					+ textPositions.get(0).getTextMatrix().getTranslateY());

			bbox[0] = textPositions.get(0).getXDirAdj();
			// TODO Mohan - Below height logic works for some PDFs only
//			bbox[1] = textPositions.get(0).getYDirAdj() - textPositions.get(0).getFontSize();
			bbox[1] = textPositions.get(0).getYDirAdj() - textPositions.get(0).getHeightDir();
			bbox[2] = textPositions.get(count - 1).getXDirAdj() + textPositions.get(count - 1).getWidth();
			bbox[3] = textPositions.get(count - 1).getYDirAdj();

//			for (TextPosition textPosition : textPositions) {
//				System.out.println(textPosition.getX() + "," + textPosition.getY() + "," + textPosition.getEndX() + ","
//						+ textPosition.getEndY());
//			}

			for (int i = 0; i < bbox.length; i++) {
				bbox[i] = CommonUtil.roundOff(bbox[i], 4);
			}

			String line = String.join("",
					(textPositions.stream().map(x -> x.getUnicode()).collect(Collectors.toList())));

			TokenData lineTokenData = new TokenData(lineId, TokenData.TOKEN_TYPE_LINE, line, bbox);
			// Exclude printing char tokens in output
//			lineTokenData.setTokenDataList(charTokenDataList);
			this.pageDataList.get(this.pageDataList.size() - 1).getTokenDataList().add(lineTokenData);

		}
	}

}
