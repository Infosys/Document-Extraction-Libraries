/** =============================================================================================================== *
 * Copyright 2021 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */
package com.infosys.ainauto.formatconverter.process;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.io.File;
import java.util.ArrayList;
import java.util.List;

import javax.imageio.ImageIO;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.infosys.ainauto.formatconverter.common.CommonUtil;

public class ImageProcessor {

	private static final Logger LOGGER = LoggerFactory.getLogger(ImageProcessor.class);
	private static final String[] HOCR_CLASS_NAMES = { "ocr_carea", "ocrx_word", "ocr_line", "ocr_par" };
	private static final String HOCR_CLASS_NAME_OCRX_WORD = "ocrx_word";

	public static void plotBboxAndSaveACopy(String imageFilePath, String hocrFilePath, String outputDir)
			throws Exception {
		long startTime = System.nanoTime();
		List<String> imageFilePathList = new ArrayList<>();
		try {
			String outputDirPathActual = CommonUtil.getActualOutputDirPath(outputDir, imageFilePath, false);
			String outputFileBaseName = CommonUtil.getPathTokens(hocrFilePath)[CommonUtil.PATH_TOKEN_FILE_NAME];
			CommonUtil.createDirsRecursively(outputDirPathActual);
			Document hocrDocument = Jsoup.parse(new File(hocrFilePath), "UTF8");
			// Create and save a separate image for each HOCR class name
			for (String className : HOCR_CLASS_NAMES) {
				BufferedImage bufImgInput = ImageIO.read(new File(imageFilePath));
				plotBboxForHocrClass(bufImgInput, hocrDocument, className, false);

				String outputFileName = outputFileBaseName + "_bbox_" + className + ".png";

				File outputfile = new File(outputDirPathActual + '/' + outputFileName);
				ImageIO.write(bufImgInput, "png", outputfile);
				imageFilePathList.add(outputfile.getAbsolutePath());
			}

			// Create one blank image with text only
			{
				BufferedImage bufferedImage = ImageIO.read(new File(imageFilePath));
				clearImage(bufferedImage, Color.WHITE);
				plotBboxForHocrClass(bufferedImage, hocrDocument, HOCR_CLASS_NAME_OCRX_WORD, true);
				
				String outputFileName = outputFileBaseName + "_bbox_" + HOCR_CLASS_NAME_OCRX_WORD + "_text_only" + ".png";

				File outputfile = new File(outputDirPathActual + '/' + outputFileName);
				ImageIO.write(bufferedImage, "png", outputfile);
				imageFilePathList.add(outputfile.getAbsolutePath());
			}

		} catch (Exception ex) {
			throw new Exception("Error occurred while plotting bbox on image", ex);
		}
		double timeElapsed = (System.nanoTime() - startTime) / 1000000000.0;
		LOGGER.info("Time taken for plotting bbox for image {} is {} secs", imageFilePath, timeElapsed);

		CommonUtil.returnResultToCaller(imageFilePathList);
	}

	private static void plotBboxForHocrClass(BufferedImage bufferedImage, Document hocrDocument, String className,
			boolean isWriteText) {
		Elements elements = hocrDocument.getElementsByClass(className);
		Graphics2D graphics2D = bufferedImage.createGraphics();
		graphics2D.setStroke(new BasicStroke(2));
		graphics2D.setColor(Color.BLUE);
		for (Element element : elements) {
			String text = element.text().trim();
			if (text.length() == 0) {
				continue;
			}
			String attrValue = element.attr("title");
			String[] bboxWord = attrValue.split(";")[0].split(" ");

			int x = Integer.parseInt(bboxWord[1]);
			int y = Integer.parseInt(bboxWord[2]);
			int width = Integer.parseInt(bboxWord[3]) - x;
			int height = Integer.parseInt(bboxWord[4]) - y;

			graphics2D.drawRect(x, y, width, height);
			if (isWriteText) {
				graphics2D.setFont(new Font(graphics2D.getFont().getName(), Font.PLAIN, height));
				graphics2D.drawString(text, x, y + height);
			}
		}
		graphics2D.dispose();
	}

	private static void clearImage(BufferedImage bufferedImage, Color color) {
		Graphics2D graphics2D = bufferedImage.createGraphics();
		graphics2D.setBackground(color);
		graphics2D.clearRect(0, 0, bufferedImage.getWidth(), bufferedImage.getHeight());
		graphics2D.dispose();
	}
}
