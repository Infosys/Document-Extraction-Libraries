/** =============================================================================================================== *
 * Copyright 2020 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */
package com.infosys.ainauto.formatconverter.process;

import java.awt.image.BufferedImage;
import java.io.File;
import java.util.ArrayList;
import java.util.List;

import javax.imageio.ImageIO;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.infosys.ainauto.formatconverter.common.CommonUtil;
import com.infosys.ainauto.formatconverter.common.DataObjectHelper;
import com.infosys.ainauto.formatconverter.common.PdfHelper;
import com.infosys.ainauto.formatconverter.model.PageData;
import com.infosys.ainauto.formatconverter.model.ResourceData;
import com.infosys.ainauto.formatconverter.model.SwitchData;
import com.infosys.ainauto.formatconverter.service.PDFStreamEngineCustom;

public class PdfToImageBbox {

	private static final Logger LOGGER = LoggerFactory.getLogger(PdfToImageBbox.class);
	private static final String DATA_FILE_SUFFIX = "_image_bbox.json";
	private static final String PDF_WITH_BBOX_FILE_SUFFIX = "_image_bbox.pdf";
	public static final String DEFAULT_PAGES = "-100";

	public static void convertPdfToImageBbox(SwitchData switchData) throws Exception {
		long startTime = System.nanoTime();
		String pdfFilePath = switchData.getFromFile();
		String outputDir = switchData.getToDir();

		PDDocument pdDocument = null;
		String outputDataFilePath = null;
		String outputPdfWithBboxFilePath = null;
		String content = "";

		List<String> resultFilePathList = new ArrayList<>();
		try {
			File file = new File(pdfFilePath);
			pdDocument = PDDocument.load(file);

			List<Integer> pageNumList = CommonUtil.getPageNumbers(switchData.getPages(), pdDocument.getNumberOfPages());

			List<PageData> pageDataList = new ArrayList<>();
			List<ResourceData> resourceDataList = new ArrayList<>();
			for (int i = 0; i < pageNumList.size(); i++) {

				PDPage pdPage = pdDocument.getPage(i);
				int pageNumBase1 = i + 1;
				if (!pageNumList.contains(pageNumBase1)) {
					continue;
				}

				PDFStreamEngineCustom pdfStreamEngineCustom = new PDFStreamEngineCustom();
				pdfStreamEngineCustom.setPageNum(pageNumBase1);
				// Do the processing and store results internally
				try{
					pdfStreamEngineCustom.processPage(pdPage);
					
				}catch(Exception e){
					continue;
				}			

				PageData pageData = pdfStreamEngineCustom.getPageData();
				pageDataList.add(pageData);
				resourceDataList.addAll(pdfStreamEngineCustom.getResourceDataList());
			}

			if (outputDir != null) {
				String outputDirPathActual = CommonUtil.getActualOutputDirPath(outputDir, pdfFilePath, false);
				CommonUtil.createDirsRecursively(outputDirPathActual);
				if (switchData.isSaveResource()) {// Save images
					for (ResourceData resourceData : resourceDataList) {
						BufferedImage bufferedImage = resourceData.getBufferedImage();

						String outputImageFilePath = outputDirPathActual + "/" + resourceData.getFileName();
						File outputfile = new File(outputImageFilePath);
						ImageIO.write(bufferedImage, resourceData.getFileType(), outputfile);
					}
				}

				String outputDataFileName = CommonUtil.getPathTokens(pdfFilePath)[CommonUtil.PATH_TOKEN_FILE_NAME] 
						+ "." + CommonUtil.getPathTokens(pdfFilePath)[CommonUtil.PATH_TOKEN_FILE_EXT] 
						+ DATA_FILE_SUFFIX;
				String outputPdfWithBboxFileName = CommonUtil
						.getPathTokens(pdfFilePath)[CommonUtil.PATH_TOKEN_FILE_NAME] 
						+ "." + CommonUtil.getPathTokens(pdfFilePath)[CommonUtil.PATH_TOKEN_FILE_EXT] 
						+ PDF_WITH_BBOX_FILE_SUFFIX;
				outputDataFilePath = outputDirPathActual + "/" + outputDataFileName;
				outputPdfWithBboxFilePath = outputDirPathActual + "/" + outputPdfWithBboxFileName;

				content = DataObjectHelper.getJsonString(pageDataList, 1, 4);

				CommonUtil.saveAsFile(outputDataFilePath, content);
				resultFilePathList.add(outputDataFilePath);
				if (switchData.isPlotBbox()) {
					PdfHelper.plotBboxOnCopyOfPdf(pageDataList, pdfFilePath, outputPdfWithBboxFilePath, pageNumList, 1);
					resultFilePathList.add(outputPdfWithBboxFilePath);
				}
			} else {
				content = DataObjectHelper.getJsonString(pageDataList, 1, 4);
			}
		} catch (Exception ex) {
			throw new Exception("Error occurred while converting PDF to BBOX", ex);
		} finally {
			if (pdDocument != null) {
				pdDocument.close();
			}
		}
		double timeElapsed = (System.nanoTime() - startTime) / 1000000000.0;
		LOGGER.info("Time taken for converting {} is {} secs", pdfFilePath, timeElapsed);
		CommonUtil.returnResultToCaller((resultFilePathList.size() > 0) ? resultFilePathList : content);
	}

}
