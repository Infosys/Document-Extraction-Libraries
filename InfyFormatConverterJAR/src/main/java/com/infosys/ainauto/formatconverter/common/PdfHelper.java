/** =============================================================================================================== *
 * Copyright 2023 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */

package com.infosys.ainauto.formatconverter.common;

import java.awt.Color;
import java.io.File;
import java.util.List;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.font.PDType1Font;

import com.infosys.ainauto.formatconverter.model.PageData;
import com.infosys.ainauto.formatconverter.model.TokenData;

/**
 * Utility class for PDF manipulations.
 *
 */
public class PdfHelper {

	public static void plotBboxOnCopyOfPdf(List<PageData> pageDataList, String origPdfPath, String plotBboxPdfPath,
			List<Integer> pageNumList, float conversionRatio) throws Exception {
		PDDocument pdDocument;
		try {
			// Load document
			pdDocument = PDDocument.load(new File(origPdfPath));
			for (int p = 0; p < pageDataList.size(); p++) {
				List<TokenData> tokenDataList = pageDataList.get(p).getTokenDataList();

				PDPage pdPage = pdDocument.getPage(p);
				int pageNumBase1 = p + 1;
				if (!pageNumList.contains(pageNumBase1)) {
					continue;
				}

				// Create content stream with append mode to draw on top
				PDPageContentStream pdPageContentStream = new PDPageContentStream(pdDocument, pdPage,
						PDPageContentStream.AppendMode.APPEND, true, true);

				pdPageContentStream.setNonStrokingColor(Color.RED);
				pdPageContentStream.setStrokingColor(Color.RED);

				for (int i = 0; i < tokenDataList.size(); i++) {
					TokenData tokenData = tokenDataList.get(i);
					int[] bbox = { 0, 0, 0, 0 };

					for (int j = 0; j < tokenData.getBbox().length; j++) {
						bbox[j] = Math.round(conversionRatio * tokenData.getBbox()[j]);
					}

					int x = bbox[0];
					int y = bbox[1];
					int width = bbox[2] - x;
					int height = bbox[3] - y;

					// Note: PDF rectangles are drawn with 0,0 as bottom left of page
					// Hence actualY needs to be calculated as follow
					int actualY = Math.round(pdPage.getBBox().getHeight() - y - height);

					// pdPageContentStream.addRect(50, 400, 300, 100);
					pdPageContentStream.addRect(x, actualY, width, height);
					pdPageContentStream.stroke();

					pdPageContentStream.beginText();
					pdPageContentStream.setFont(PDType1Font.HELVETICA, 9);
					if (tokenData.getType() == TokenData.TOKEN_TYPE_IMAGE) {
						pdPageContentStream.newLineAtOffset(x, actualY + 2);
					} else {
						pdPageContentStream.newLineAtOffset(x, actualY + height + 2);
					}

					pdPageContentStream.showText(tokenData.getId());
					pdPageContentStream.endText();
				}
				pdPageContentStream.close();
			}
			pdDocument.save(plotBboxPdfPath);
			pdDocument.close();

		} catch (Exception ex) {
			throw new Exception("Error occurred while drawing BBOX on PDF", ex);
		}
	}
}
