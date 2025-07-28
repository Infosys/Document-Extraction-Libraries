/** =============================================================================================================== *
 * Copyright 2020 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */
package com.infosys.ainauto.formatconverter.process;

import java.awt.geom.Rectangle2D;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import javax.imageio.ImageIO;
import javax.json.Json;
import javax.json.JsonArrayBuilder;
import javax.json.JsonObjectBuilder;

import org.apache.pdfbox.cos.COSName;
import org.apache.pdfbox.multipdf.Splitter;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDResources;
import org.apache.pdfbox.pdmodel.graphics.PDXObject;
import org.apache.pdfbox.pdmodel.graphics.form.PDFormXObject;
import org.apache.pdfbox.pdmodel.graphics.image.PDImageXObject;
import org.apache.pdfbox.rendering.ImageType;
import org.apache.pdfbox.rendering.PDFRenderer;
import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.pdfbox.text.PDFTextStripperByArea;
import org.apache.pdfbox.tools.PDFText2HTML;
import org.apache.pdfbox.tools.imageio.ImageIOUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.infosys.ainauto.formatconverter.common.CommonUtil;
import com.infosys.ainauto.formatconverter.common.Constants;
import com.infosys.ainauto.formatconverter.model.SwitchData;

public class PdfToOther {

	private static final Logger LOGGER = LoggerFactory.getLogger(PdfToOther.class);
	public static final int DEFAULT_DPI = 300;

	
	private static final String JSON_OBJ_PAGE_NUM = "pageNum";
	private static final String JSON_OBJ_PAGE_TEXT = "pageText";
	private static final String JSON_OBJ_REGIONS = "regions";
	private static final String JSON_OBJ_BBOX = "bbox";
	private static final String JSON_OBJ_NAME = "name";
	private static final String JSON_OBJ_TEXT = "text";

	

	public static void convertPdfToImage(String pdfFilePath, String outputDir, int dpi, String pages) throws Exception {
		long startTime = System.nanoTime();
		List<String> imageFilePathList = new ArrayList<>();
		String outputDirPathActual;
		try {
			File file = new File(pdfFilePath);
			PDDocument document = PDDocument.load(file);
			PDFRenderer pdfRenderer = new PDFRenderer(document);

			outputDirPathActual = CommonUtil.getActualOutputDirPath(outputDir, pdfFilePath, true);
			CommonUtil.createDirsRecursively(outputDirPathActual);

			List<Integer> pageNumList = CommonUtil.getPageNumbers(pages, document.getNumberOfPages());
			String outputFilename = "";
			// Convert PDF to image(s) and save to newly created output folder.
			for (int i = 0; i < pageNumList.size(); i++) {
				BufferedImage bim = pdfRenderer.renderImageWithDPI(pageNumList.get(i) - 1, dpi, ImageType.RGB);
				outputFilename = outputDirPathActual + "/" + (pageNumList.get(i)) + ".jpg";
				ImageIOUtil.writeImage(bim, outputFilename, dpi);
				imageFilePathList.add(outputFilename);
			}
			document.close();
		} catch (Exception ex) {
			throw new Exception("Error occurred while converting PDF to image", ex);
		}

		double timeElapsed = (System.nanoTime() - startTime) / 1000000000.0;
		LOGGER.info("Time taken for converting {} to {} is {} secs", pdfFilePath, outputDirPathActual, timeElapsed);

		CommonUtil.returnResultToCaller(imageFilePathList);
	}

	public static void extractImagesFromPdf(String pdfFilePath, String outputDir, String imageFormats, String pages)
			throws Exception {
		long startTime = System.nanoTime();
		List<String> imageFilePathList = new ArrayList<>();
		String outputDirPathActual;
		try {
			File file = new File(pdfFilePath);
			PDDocument document = PDDocument.load(file);

			outputDirPathActual = CommonUtil.getActualOutputDirPath(outputDir, pdfFilePath, true);
			CommonUtil.createDirsRecursively(outputDirPathActual);

			List<Integer> pageNumList = CommonUtil.getPageNumbers(pages, document.getNumberOfPages());
			String outputFilename = "";
			// Extract images from each page and save to newly created output folder
			for (int i = 0; i < pageNumList.size(); i++) {
				PDPage pdPage = document.getPage(pageNumList.get(i) - 1);
				List<BufferedImage> pageLevelImages = getImages(pdPage.getResources());

				for (int k = 0; k < pageLevelImages.size(); k++) {
					String imageIndex = "";
					// If only single image in a page, then don't use sub index
					if (pageLevelImages.size() > 1) {
						imageIndex = "-" + (k + 1);
					}
					BufferedImage buffImg = pageLevelImages.get(k);

					for (String requestedImageFormat : imageFormats.split(",")) {
						String imageFormat = requestedImageFormat.toLowerCase().trim();
						// If image is ARGB, then force usage of PNG format
						if (buffImg.getColorModel().hasAlpha()) {
							imageFormat = Constants.IMAGE_FORMAT_PNG;
						}
						outputFilename = outputDirPathActual + "/" + (pageNumList.get(i)) + imageIndex + "."
								+ imageFormat;
						File outputfile = new File(outputFilename);
						ImageIO.write(buffImg, imageFormat, outputfile);
						imageFilePathList.add(outputFilename);
					}

				}
			}
			document.close();
		} catch (Exception ex) {
			throw new Exception("Error occurred while extracting images from PDF", ex);
		}

		double timeElapsed = (System.nanoTime() - startTime) / 1000000000.0;
		LOGGER.info("Time taken for extracting images from {} to {} is {} secs", pdfFilePath, outputDirPathActual,
				timeElapsed);

		CommonUtil.returnResultToCaller(imageFilePathList);

	}

	public static void rotatePdfPage(String pdfFilePath, String outputDir, String pages, String angles)
			throws Exception {
		long startTime = System.nanoTime();
		String outputFilename = pdfFilePath;
		try {
			File file = new File(pdfFilePath);
			PDDocument document = PDDocument.load(file);
			if (outputDir != null) {
				outputFilename = outputDir + "/" + file.getName();
				CommonUtil.createDirsRecursively(outputDir);
			}

			List<Integer> pageNumList = CommonUtil.getPageNumbers(pages, document.getNumberOfPages());
			// Extract images from each page and save to newly created output folder
			String pageAngleArray[] = angles.split(",");
			for (int i = 0; i < pageNumList.size(); i++) {
				PDPage pdPage = document.getPage(pageNumList.get(i) - 1);
				pdPage.setRotation(
						Integer.parseInt((i >= pageAngleArray.length) ? pageAngleArray[0]:pageAngleArray[i]));
			}
			document.save(outputFilename);
			document.close();
		} catch (Exception ex) {
			throw new Exception("Error occurred while extracting images from PDF", ex);
		}
		double timeElapsed = (System.nanoTime() - startTime) / 1000000000.0;
		LOGGER.info("Time taken for PDF rotation {} is {} secs", pdfFilePath, timeElapsed);
		CommonUtil.returnResultToCaller(outputFilename);
	}

	public static void convertPdfToMultiPdf(String pdfFilePath, String outputDir, String pages) throws Exception {
		long startTime = System.nanoTime();
		List<String> filePathList = new ArrayList<>();
		String outputDirPathActual;
		try {
			File file = new File(pdfFilePath);
			PDDocument document = PDDocument.load(file);
			// instantiating Splitter
			Splitter splitter = new Splitter();
			// split the pages of a PDF document
			List<PDDocument> Pages = splitter.split(document);
			outputDirPathActual = CommonUtil.getActualOutputDirPath(outputDir, pdfFilePath, true);
			CommonUtil.createDirsRecursively(outputDirPathActual);

			List<Integer> pageNumList = CommonUtil.getPageNumbers(pages, document.getNumberOfPages());
			// Creating an iterator
			Iterator<PDDocument> iterator = Pages.listIterator();
			// saving splits as pdf
			int i = 1;
			while (iterator.hasNext()) {
				PDDocument pd = iterator.next();
				if (pageNumList.contains(i)) {
					// provide destination path to the PDF split
					String outputFilename = outputDirPathActual + "/" + file.getName() + "." + i + ".pdf";
					pd.save(outputFilename);
					filePathList.add(outputFilename);
				}
				i++;
			}
			document.close();
		} catch (Exception ex) {
			throw new Exception("Error occurred while converting PDF to image", ex);
		}

		double timeElapsed = (System.nanoTime() - startTime) / 1000000000.0;
		LOGGER.info("Time taken for converting {} to {} is {} secs", pdfFilePath, outputDirPathActual, timeElapsed);
		CommonUtil.returnResultToCaller(filePathList);
	}

	public static void convertPdfToText(SwitchData switchData) throws Exception {
		convertPdfTo(switchData, true, false);
	}

	public static void convertPdfToJson(SwitchData switchData) throws Exception {
		convertPdfTo(switchData, false, true);
	}

	public static void convertPdfToHtml(String pdfFilePath, String outputDir) throws Exception {
		long startTime = System.nanoTime();
		PDDocument pdDocument = null;
		String outputFilePath;
		try {
			File file = new File(pdfFilePath);
			pdDocument = PDDocument.load(file);
			PDFText2HTML pdfText2HTML = new PDFText2HTML();

			{
				String outputDirPathActual = CommonUtil.getActualOutputDirPath(outputDir, pdfFilePath, false);
				CommonUtil.createDirsRecursively(outputDirPathActual);
				String outputFileName = CommonUtil.getPathTokens(pdfFilePath)[CommonUtil.PATH_TOKEN_FILE_NAME]
						+ ".html";
				outputFilePath = outputDirPathActual + "/" + outputFileName;
			}

			try (Writer writer = new OutputStreamWriter(new FileOutputStream(outputFilePath));) {
				pdfText2HTML.writeText(pdDocument, writer);
			} catch (Exception ex) {
				throw new Exception("Error occurred while writing to HTML file", ex);
			}
		} catch (Exception ex) {
			throw new Exception("Error occurred while converting PDF to HTML", ex);
		} finally {
			if (pdDocument != null) {
				pdDocument.close();
			}
		}

		double timeElapsed = (System.nanoTime() - startTime) / 1000000000.0;
		LOGGER.info("Time taken for converting {} to {} is {} secs", pdfFilePath, outputFilePath, timeElapsed);
		CommonUtil.returnResultToCaller(outputFilePath);
	}

	private static void convertPdfTo(SwitchData switchData, boolean isToPlainText, boolean isToJson) throws Exception {
		long startTime = System.nanoTime();
		String pdfFilePath = switchData.getFromFile();
		String outputDir = switchData.getToDir();
		String fileExtension = isToPlainText ? ".txt" : (isToJson ? ".json" : "");
		PDDocument pdDocument = null;
		String outputFilePath = null;
		String content = "";
		try {
			File file = new File(pdfFilePath);
			pdDocument = PDDocument.load(file);
			Map<String, Map<String, String>> pageToBboxToTextMap = getText(switchData, pdDocument);

			if (isToJson) {
				content = convertToJsonString(pageToBboxToTextMap, switchData);
			} else if (isToPlainText) {
				content = conertToPlainText(pageToBboxToTextMap, switchData);
			}
			if (outputDir != null) {
				String outputDirPathActual = CommonUtil.getActualOutputDirPath(outputDir, pdfFilePath, false);
				CommonUtil.createDirsRecursively(outputDirPathActual);
				String outputFileName = CommonUtil.getPathTokens(pdfFilePath)[CommonUtil.PATH_TOKEN_FILE_NAME]
						+ fileExtension;
				outputFilePath = outputDirPathActual + "/" + outputFileName;
				CommonUtil.saveAsFile(outputFilePath, content);
			}
		} catch (Exception ex) {
			throw new Exception("Error occurred while converting PDF to TEXT", ex);
		} finally {
			if (pdDocument != null) {
				pdDocument.close();
			}
		}
		double timeElapsed = (System.nanoTime() - startTime) / 1000000000.0;
		LOGGER.info("Time taken for converting {} is {} secs", pdfFilePath, timeElapsed);
		CommonUtil.returnResultToCaller((outputDir != null) ? outputFilePath : content);
	}

	private static String conertToPlainText(Map<String, Map<String, String>> pageToBboxToTextMap,
			SwitchData switchData) {
		String content = "";
		for (Map.Entry<String, Map<String, String>> entry1 : pageToBboxToTextMap.entrySet()) {
			String pageText = "";
			String bboxText = "";
			Map<String, String> bboxToTextMap = entry1.getValue();
			for (Map.Entry<String, String> entry2 : bboxToTextMap.entrySet()) {
				if (entry2.getKey().equalsIgnoreCase(JSON_OBJ_PAGE_TEXT)) {
					pageText = entry2.getValue() + "\n";
				} else {
					bboxText += entry2.getKey() + "=" + entry2.getValue() + "\n";
				}
			}
			content += pageText + bboxText;
		}
		return content;
	}

	private static String convertToJsonString(Map<String, Map<String, String>> pageToBboxToTextMap,
			SwitchData switchData) {
		JsonArrayBuilder arrayBuilder = Json.createArrayBuilder();
		for (Map.Entry<String, Map<String, String>> entry1 : pageToBboxToTextMap.entrySet()) {
			JsonObjectBuilder pageObject = Json.createObjectBuilder();
			pageObject.add(JSON_OBJ_PAGE_NUM, entry1.getKey());
			String pageText = "";
			Map<String, String> bboxToTextMap = entry1.getValue();
			JsonArrayBuilder textArrayBuilder = Json.createArrayBuilder();
			for (Map.Entry<String, String> entry2 : bboxToTextMap.entrySet()) {
				JsonObjectBuilder regionObject = Json.createObjectBuilder();
				if (entry2.getKey().equalsIgnoreCase(JSON_OBJ_PAGE_TEXT)) {
					pageText = entry2.getValue();
				} else {
					regionObject.add(JSON_OBJ_NAME, entry2.getKey());
					regionObject.add(JSON_OBJ_TEXT, entry2.getValue());

					int[] bbox = switchData.getBboxNameValueMap().get(entry2.getKey());

					JsonArrayBuilder bboxArrayBuilder = Json.createArrayBuilder();
					for (int i = 0; i < bbox.length; i++) {
						bboxArrayBuilder.add(bbox[i]);
					}
					regionObject.add(JSON_OBJ_BBOX, bboxArrayBuilder.build());
					textArrayBuilder.add(regionObject);
				}

			}
			pageObject.add(JSON_OBJ_REGIONS, textArrayBuilder.build());
			pageObject.add(JSON_OBJ_PAGE_TEXT, pageText);

			arrayBuilder.add(pageObject);
		}
		return CommonUtil.getPrettyJson(arrayBuilder.build());
	}

	private static Map<String, Map<String, String>> getText(SwitchData switchData, PDDocument pdDocument)
			throws IOException {
		String content = "";
		Map<String, Map<String, String>> pageToBboxToTextMap = new LinkedHashMap<String, Map<String, String>>();
		List<Integer> pageNumList = CommonUtil.getPageNumbers(switchData.getPages(), pdDocument.getNumberOfPages());
		if (switchData.getBboxNameValueMap().isEmpty()) {
			PDFTextStripper pdfStripper = new PDFTextStripper();
			for (int i = 0; i < pageNumList.size(); i++) {
				int actualPageNum = pageNumList.get(i);
				pdfStripper.setStartPage(actualPageNum);
				pdfStripper.setEndPage(actualPageNum);
				content = pdfStripper.getText(pdDocument);
				content = content == null ? "" : content.trim();
				Map<String, String> bboxToTextMap = new LinkedHashMap<String, String>();
				bboxToTextMap.put(JSON_OBJ_PAGE_TEXT, content);
				pageToBboxToTextMap.put(String.valueOf(pageNumList.get(i)), bboxToTextMap);
			}
		} else {
			for (int i = 0; i < pageNumList.size(); i++) {
				int actualPageNum = pageNumList.get(i) - 1;
				PDPage docPage = pdDocument.getPage(actualPageNum);
				float conversionRatio = CommonUtil.getConversionRatio(switchData.getPageWidth(),
						switchData.getPageHeight(), docPage.getBBox().getWidth(), docPage.getBBox().getHeight());

				Map<String, String> bboxToTextMap = new LinkedHashMap<String, String>();
				for (Map.Entry<String, int[]> entry : switchData.getBboxNameValueMap().entrySet()) {
					String key = entry.getKey();
					int[] bbox = entry.getValue();

					Rectangle2D rect = new java.awt.geom.Rectangle2D.Float(bbox[0] * conversionRatio,
							bbox[1] * conversionRatio, bbox[2] * conversionRatio, bbox[3] * conversionRatio);
					PDFTextStripperByArea textStripper = new PDFTextStripperByArea();
					textStripper.addRegion("myregion", rect);
					textStripper.extractRegions(docPage);
					content = textStripper.getTextForRegion("myregion");
					content = content == null ? "" : content.trim();
					bboxToTextMap.put(key, content);
				}
				pageToBboxToTextMap.put(String.valueOf(pageNumList.get(i)), bboxToTextMap);
			}
		}
		return pageToBboxToTextMap;
	}

	private static List<BufferedImage> getImages(PDResources pdResources) throws IOException {

		List<BufferedImage> images = new ArrayList<>();
		for (COSName xObjectName : pdResources.getXObjectNames()) {
			PDXObject xObject = pdResources.getXObject(xObjectName);
			if (xObject instanceof PDFormXObject) {
				images.addAll(getImages(((PDFormXObject) xObject).getResources()));
			} else if (xObject instanceof PDImageXObject) {
				images.add(((PDImageXObject) xObject).getImage());
			}
		}
		return images;
	}
}
