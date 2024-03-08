/** =============================================================================================================== *
 * Copyright 2020 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */

package com.infosys.ainauto.formatconverter.process;

import java.io.IOException;
import java.util.List;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.common.PDRectangle;
import org.apache.pdfbox.pdmodel.font.PDFont;
import org.apache.pdfbox.pdmodel.font.PDType1Font;
import org.apache.pdfbox.pdmodel.graphics.image.PDImageXObject;
import org.apache.pdfbox.pdmodel.graphics.state.PDExtendedGraphicsState;
import org.apache.pdfbox.util.Matrix;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.infosys.ainauto.formatconverter.common.CommonUtil;

public class OtherToPdf {

	private static final Logger LOGGER = LoggerFactory.getLogger(OtherToPdf.class);
	private static final float WATERMARK_FONT_SIZE = 50.0f;
	private static final PDFont WATERMARK_FONT = PDType1Font.HELVETICA_OBLIQUE;
	private static final float RADIAN_TO_DEGREE = 57.2958f;
	private static final float WATERMARK_TEXT_ROTATION_DEGREE = 30;

	public static void convertImageToPdf(List<String> inputFilePathList, String outputFilePath, String watermarkText)
			throws Exception {
		long startTime = System.nanoTime();
		try (PDDocument newDocument = new PDDocument()) {
			for (String inputFilePath : inputFilePathList) {
				PDPage pdPage = getNewPageWithImage(inputFilePath, newDocument);
				if (watermarkText != null && watermarkText.trim().length() > 0) {
					addWatermark(newDocument, pdPage, watermarkText);
				}
				newDocument.addPage(pdPage);
			}
			newDocument.save(outputFilePath);
		} catch (Exception ex) {
			throw new Exception("Error occurred while converting Image(s) to PDF", ex);
		}
		double timeElapsed = (System.nanoTime() - startTime) / 1000000000.0;
		LOGGER.info("Time taken for converting {} file(s) to {} is {} secs", inputFilePathList.size(), outputFilePath,
				timeElapsed);
		CommonUtil.returnResultToCaller(outputFilePath);
	}

	private static PDPage getNewPageWithImage(String imageFilePath, PDDocument newDocument) throws Exception {
		PDPage pdPage = null;
		try {
			PDImageXObject image = PDImageXObject.createFromFile(imageFilePath, newDocument);
			PDRectangle pdRectangle = PDRectangle.A4;

			float conversionRatio = Math.min(pdRectangle.getWidth() / image.getWidth(),
					pdRectangle.getHeight() / image.getHeight());
			float actualWidth = image.getWidth() * conversionRatio;
			float actualHeight = image.getHeight() * conversionRatio;
			float xCoordinate = (pdRectangle.getWidth() - actualWidth) / 2;
			float yCoordinate = (pdRectangle.getHeight() - actualHeight) / 2;

			pdPage = new PDPage(pdRectangle);

			try (PDPageContentStream pdPageContentStream = new PDPageContentStream(newDocument, pdPage)) {
				pdPageContentStream.drawImage(image, xCoordinate, yCoordinate, actualWidth, actualHeight);
			}
		} catch (IOException ex) {
			throw new Exception("Error occurred while converting image to PDF", ex);
		}
		return pdPage;
	}

	private static void addWatermark(PDDocument pdDocument, PDPage pdPage, String text) throws IOException {
		PDPageContentStream pdPageContentStream = new PDPageContentStream(pdDocument, pdPage,
				PDPageContentStream.AppendMode.APPEND, true, true);
		PDExtendedGraphicsState pdExtendedGraphicsState = new PDExtendedGraphicsState();
		pdExtendedGraphicsState.setNonStrokingAlphaConstant(0.2f);
		pdExtendedGraphicsState.setAlphaSourceFlag(true);
		pdPageContentStream.setGraphicsStateParameters(pdExtendedGraphicsState);
		pdPageContentStream.setNonStrokingColor(50, 50, 50);// Gray
		pdPageContentStream.setFont(WATERMARK_FONT, WATERMARK_FONT_SIZE);
		pdPageContentStream.beginText();

		float textWidth = WATERMARK_FONT.getStringWidth(text) / 1000 * WATERMARK_FONT_SIZE;

		float textHeight = WATERMARK_FONT.getFontDescriptor().getFontBoundingBox().getHeight() / 1000
				* WATERMARK_FONT_SIZE;

//		float widthReduction = Math.max(textWidth* (WATERMARK_TEXT_ROTATION_DEGREE / 90), textHeight);

		float xCoordinate = (pdPage.getMediaBox().getWidth() / 2) - (textWidth / 2);
		float yCoordinate = (pdPage.getMediaBox().getHeight() / 2) - (textHeight / 2);

		pdPageContentStream.setTextMatrix(
				Matrix.getRotateInstance(WATERMARK_TEXT_ROTATION_DEGREE / RADIAN_TO_DEGREE, xCoordinate, yCoordinate));
		pdPageContentStream.showText(text);
		pdPageContentStream.endText();

		pdPageContentStream.close();
	}

}
