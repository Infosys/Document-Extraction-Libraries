/** =============================================================================================================== *
 * Copyright 2020 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */
package com.infosys.ainauto.formatconverter.process;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.OutputStreamWriter;
import java.io.StringReader;
import java.io.Writer;
import java.util.ArrayList;
import java.util.List;

import javax.json.Json;
import javax.json.JsonArray;
import javax.json.JsonArrayBuilder;
import javax.json.JsonReader;
import javax.json.JsonValue;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.infosys.ainauto.formatconverter.common.CommonUtil;
import com.infosys.ainauto.formatconverter.common.DataObjectHelper;
import com.infosys.ainauto.formatconverter.common.PdfHelper;
import com.infosys.ainauto.formatconverter.model.PageData;
import com.infosys.ainauto.formatconverter.model.SwitchData;
import com.infosys.ainauto.formatconverter.service.PdfTextStripperCustom;

public class PdfToTextBbox {

	private static final Logger LOGGER = LoggerFactory.getLogger(PdfToTextBbox.class);
	private static final String DATA_FILE_SUFFIX = "_bbox.json";
	private static final String PDF_WITH_BBOX_FILE_SUFFIX = "_bbox.pdf";
	public static final String DEFAULT_PAGES = "-100";

	public static void convertPdfToTextBbox(SwitchData switchData) throws Exception {
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

			JsonReader jsonReader = Json.createReader(new StringReader("[]"));
			JsonArrayBuilder jsonArrayBuilder = Json.createArrayBuilder();
			List<PageData> allPageDataList = new ArrayList<PageData>();
			for (int i = 0; i < pageNumList.size(); i++) {
				PdfTextStripperCustom stripper = new PdfTextStripperCustom();
				stripper.setSortByPosition(true);
				int pageNumStart = pageNumList.get(i);
				int pageNumEnd = pageNumStart;
				stripper.setStartPage(pageNumStart);
				stripper.setEndPage(pageNumEnd);

				Writer writer = new OutputStreamWriter(new ByteArrayOutputStream());
				stripper.writeText(pdDocument, writer);

				List<PageData> currentPageDataList = stripper.getPageDataList();
				allPageDataList.addAll(currentPageDataList);

				content = DataObjectHelper.getJsonString(currentPageDataList, 1, 4);

				JsonReader jsonReader1 = Json.createReader(new StringReader(content));
				JsonArray jsonItemArray = jsonReader1.readArray();
				for (JsonValue value : jsonItemArray) {
					jsonArrayBuilder.add(value);
				}
				jsonReader1.close();

			}
			content = CommonUtil.getPrettyJson(jsonArrayBuilder.build());
			jsonReader.close();

			if (outputDir != null) {
				String outputDirPathActual = CommonUtil.getActualOutputDirPath(outputDir, pdfFilePath, false);
				CommonUtil.createDirsRecursively(outputDirPathActual);
				String outputDataFileName = CommonUtil.getPathTokens(pdfFilePath)[CommonUtil.PATH_TOKEN_FILE_NAME]
						+ DATA_FILE_SUFFIX;
				String outputPdfWithBboxFileName = CommonUtil
						.getPathTokens(pdfFilePath)[CommonUtil.PATH_TOKEN_FILE_NAME] + PDF_WITH_BBOX_FILE_SUFFIX;
				outputDataFilePath = outputDirPathActual + "/" + outputDataFileName;
				outputPdfWithBboxFilePath = outputDirPathActual + "/" + outputPdfWithBboxFileName;
				CommonUtil.saveAsFile(outputDataFilePath, content);
				resultFilePathList.add(outputDataFilePath);
				if (switchData.isPlotBbox()) {
					PdfHelper.plotBboxOnCopyOfPdf(allPageDataList, pdfFilePath, outputPdfWithBboxFilePath, pageNumList,
							1);
					resultFilePathList.add(outputPdfWithBboxFilePath);
				}
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
