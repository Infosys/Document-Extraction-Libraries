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
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.common.PDRectangle;
import org.apache.pdfbox.pdmodel.interactive.action.PDAction;
import org.apache.pdfbox.pdmodel.interactive.action.PDActionURI;
import org.apache.pdfbox.pdmodel.interactive.annotation.PDAnnotation;
import org.apache.pdfbox.pdmodel.interactive.annotation.PDAnnotationLink;
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

		// TODO - The bbox calculation logic may need fine-tuning after testing on
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

			// Step2 - Handle words to create wordTokenList
			List<TokenData> wordTokenDataList = new ArrayList<>();
			StringBuilder wordBuilder = new StringBuilder();
			List<TextPosition> currentWordPositions = new ArrayList<>();
			int wordTextCounter = 0;
			for (TextPosition textPosition : textPositions) {
				if (textPosition.getUnicode().trim().isEmpty()) {
					if (wordBuilder.length() > 0) {
						wordTextCounter++;
						float[] wordBbox = createBboxForWord(currentWordPositions);
						TokenData wordTokenData = new TokenData(String.format("%s_W%d", lineId, wordTextCounter),TokenData.TOKEN_TYPE_WORD, wordBuilder.toString(), wordBbox);
						// hyperlink logic
						String word = wordBuilder.toString();
						String uri = findHyperlinkUri(wordBbox, pageCounter - 1, word);
						if (uri != null) {
							// wordTokenData.setUri(uri);
							wordTokenData.setTextHtml("<a href=\"" + uri + "\">" + word + "</a>");
						} else {
							wordTokenData.setTextHtml(null);
						}
						wordTokenDataList.add(wordTokenData);
						wordBuilder.setLength(0);
						currentWordPositions.clear();
					}
				} else {
					wordBuilder.append(textPosition.getUnicode());
					currentWordPositions.add(textPosition);
				}
			}
			if (wordBuilder.length() > 0) {
				wordTextCounter++;
				float[] wordBbox = createBboxForWord(currentWordPositions);
				TokenData wordTokenData = new TokenData(String.format("%s_W%d", lineId, wordTextCounter),
						TokenData.TOKEN_TYPE_WORD, wordBuilder.toString(), wordBbox);
				String word = wordBuilder.toString();
				String uri = findHyperlinkUri(wordBbox, pageCounter - 1, word);
				if (uri != null) {
					wordTokenData.setTextHtml("<a href=\"" + uri + "\">" + word + "</a>");
				} else {
					wordTokenData.setTextHtml(null);
				}
				wordTokenDataList.add(wordTokenData);
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
			// TODO - Below height logic works for some PDFs only
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
			// lineTokenData.setTokenDataList(charTokenDataList);
			// lineTokenData.setTokenDataList(wordTokenDataList);

			StringBuilder lineTextHtmlBuilder = new StringBuilder();
			String currentHref = null;
			StringBuilder currentAnchorText = new StringBuilder();
			boolean hasHyperlink = false;
			
			for (int i = 0; i < wordTokenDataList.size(); i++) {
				TokenData wordToken = wordTokenDataList.get(i);
				String wordTextHtml = wordToken.getTextHtml();
				String wordHref = null;
				if (wordTextHtml != null) {
					Matcher matcher = Pattern.compile("href=\"(.*?)\"").matcher(wordTextHtml);
					if (matcher.find()) {
						wordHref = matcher.group(1);
						hasHyperlink = true;
					}
				}
				if (wordHref != null && wordHref.equals(currentHref)) {
					currentAnchorText.append(" ").append(wordToken.getText());
				} else {
					if (currentHref != null) {
						lineTextHtmlBuilder.append("<a href=\"").append(currentHref).append("\">")
										   .append(currentAnchorText.toString()).append("</a> ");
					} else if (currentAnchorText.length() > 0) {
						lineTextHtmlBuilder.append(currentAnchorText.toString()).append(" ");
					}
			
					currentHref = wordHref;
					currentAnchorText.setLength(0);
					currentAnchorText.append(wordToken.getText());
				}
			}
			if (currentHref != null) {
				lineTextHtmlBuilder.append("<a href=\"").append(currentHref).append("\">")
								   .append(currentAnchorText.toString()).append("</a>");
			} else if (currentAnchorText.length() > 0) {
				lineTextHtmlBuilder.append(currentAnchorText.toString());
			}
			
			// Set textHtml only if there are hyperlinks
			if (hasHyperlink) {
				lineTokenData.setTextHtml(lineTextHtmlBuilder.toString().trim());
			} else {
				lineTokenData.setTextHtml(null);
			}

			this.pageDataList.get(this.pageDataList.size() - 1).getTokenDataList().add(lineTokenData);
		}
	}

	private float[] createBboxForWord(List<TextPosition> textPositions) {
		float[] bbox = { textPositions.get(0).getXDirAdj(), textPositions.get(0).getYDirAdj() - textPositions.get(0).getHeightDir(),
				textPositions.get(textPositions.size() - 1).getXDirAdj() + textPositions.get(textPositions.size() - 1).getWidth(),
				textPositions.get(textPositions.size() - 1).getYDirAdj() };
		for (int i = 0; i < bbox.length; i++) {
			bbox[i] = CommonUtil.roundOff(bbox[i], 4);
		}
		return bbox;
	}

	private String findHyperlinkUri(float[] wordBbox, int pageIndex, String word) throws IOException {
		PDPage page = this.pdDocument.getPage(pageIndex);
		PDRectangle pageRect = page.getMediaBox();
		float pageHeight = pageRect.getHeight();
		List<PDAnnotation> annotations = page.getAnnotations();
		for (PDAnnotation annotation : annotations) {
			if (annotation instanceof PDAnnotationLink) {
				PDAnnotationLink link = (PDAnnotationLink) annotation;
				PDRectangle rect = link.getRectangle();
				float x0 = rect.getLowerLeftX();
				float y0 = pageHeight - rect.getUpperRightY(); 
				float x1 = rect.getUpperRightX();
				float y1 = pageHeight - rect.getLowerLeftY();
				float[] linkBbox = { x0, y0, x1, y1 };
				PDAction action1 = link.getAction();
				String hyperlink = null;
				if (action1 instanceof PDActionURI) {
					hyperlink = ((PDActionURI) action1).getURI();
				}
				// System.out.println("Hyperlink: hyperlink=" + hyperlink + ", BBox= " + Arrays.toString(linkBbox));
	
				// overlap area
				float intersectionX0 = Math.max(wordBbox[0], linkBbox[0]);
				float intersectionY0 = Math.max(wordBbox[1], linkBbox[1]);
				float intersectionX1 = Math.min(wordBbox[2], linkBbox[2]);
				float intersectionY1 = Math.min(wordBbox[3], linkBbox[3]);
	
				if (intersectionX0 < intersectionX1 && intersectionY0 < intersectionY1) {
					float intersectionArea = (intersectionX1 - intersectionX0) * (intersectionY1 - intersectionY0);
					float wordArea = (wordBbox[2] - wordBbox[0]) * (wordBbox[3] - wordBbox[1]);
	
					// overlap area is atleast 60% of the wordarea
					if (intersectionArea / wordArea >= 0.6) {
						return hyperlink;
					}
				}
			}
		}
		return null;
	}

}
