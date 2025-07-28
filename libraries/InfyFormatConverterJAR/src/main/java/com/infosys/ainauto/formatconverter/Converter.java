/** =============================================================================================================== *
 * Copyright 2020 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */
package com.infosys.ainauto.formatconverter;

import java.io.File;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.infosys.ainauto.formatconverter.common.CommonUtil;
import com.infosys.ainauto.formatconverter.common.Constants;
import com.infosys.ainauto.formatconverter.model.SwitchData;
import com.infosys.ainauto.formatconverter.process.ImageProcessor;
import com.infosys.ainauto.formatconverter.process.OtherToPdf;
import com.infosys.ainauto.formatconverter.process.PdfToImageBbox;
import com.infosys.ainauto.formatconverter.process.PdfToTextBbox;
import com.infosys.ainauto.formatconverter.process.PdfToOther;
import com.infosys.ainauto.formatconverter.process.WordToPdf;

public class Converter {

	// Create logs folder before instantiating logger object
	static {
		new File("./logs").mkdirs();
	}

	private static final Logger LOGGER = LoggerFactory.getLogger(Converter.class);
	private static final String SWITCH_PREFIX = "--";
	private static String HELP_TEXT = "";

	static {
		HELP_TEXT = new String(CommonUtil.readResourceFile(("README.TXT")));
	}

	private enum EnumActionType {
		WORD_T0_PDF("wordToPdf"), PDF_TO_IMG("pdfToImg"), PDF_TO_TEXT("pdfToText"), PDF_TO_JSON("pdfToJson"),
		PDF_TO_HTML("pdfToHtml"), PDF_TO_MULTIPDF("pdfToMultiPdf"), PDF_TO_TEXT_BBOX("pdfToTextBbox"),
		PDF_TO_IMAGE_BBOX("pdfToImageBbox"), IMG_TO_PDF("imgToPdf"), PLOT_BBOX("plotBbox"), IMG_FROM_PDF("imgFromPdf"),
		ROTATE_PDF_PAGE("rotatePdfPage");

		private String propertyValue;

		private EnumActionType(String s) {
			propertyValue = s;
		}

		public String getValue() {
			return propertyValue;
		}
	}

	private enum EnumSwitchName {
		FROM_FILE("fromfile"), TO_FILE("tofile"), HOCR_FILE("hocrfile"), TO_DIR("todir"), DPI("dpi"), PAGES("pages"),
		PAGE_WIDTH("pagewidth"), PAGE_HEIGHT("pageheight"), BBOX("bbox"), WATERMARK_TEXT("watermarktext"),
		PLOT_BBOX("plotbbox"), IMG_FORMAT("imgformats"), TIMEOUT("timeout"), ANGLES("angles"),
		SAVE_RESOURCE("saveresource");

		private String propertyValue;

		private EnumSwitchName(String s) {
			propertyValue = s;
		}

		public String getValue() {
			return propertyValue;
		}
	}

	public static void main(String[] args) throws Exception {
		try {
			boolean isShowHelpText = false;
			if (args.length > 0) {
				Map<String, String> switchMap = getSwitchMap(args);
				validateSwitches(switchMap);
				SwitchData switchData = getSwitchData(switchMap);

				String action = args[0];
				if (action.equalsIgnoreCase(EnumActionType.WORD_T0_PDF.getValue())) {
					WordToPdf.convertWordToPdf(switchData.getFromFile(), switchData.getToFile(),
							switchData.getTimeout());
				} else if (action.equalsIgnoreCase(EnumActionType.PDF_TO_MULTIPDF.getValue())) {
					PdfToOther.convertPdfToMultiPdf(switchData.getFromFile(), switchData.getToDir(),
							switchData.getPages());
				} else if (action.equalsIgnoreCase(EnumActionType.ROTATE_PDF_PAGE.getValue())) {
					PdfToOther.rotatePdfPage(switchData.getFromFile(), switchData.getToDir(), switchData.getPages(),
							switchData.getAngles());
				} else if (action.equalsIgnoreCase(EnumActionType.PDF_TO_IMG.getValue())) {
					PdfToOther.convertPdfToImage(switchData.getFromFile(), switchData.getToDir(), switchData.getDpi(),
							switchData.getPages());
				} else if (action.equalsIgnoreCase(EnumActionType.PDF_TO_TEXT.getValue())) {
					PdfToOther.convertPdfToText(switchData);
				} else if (action.equalsIgnoreCase(EnumActionType.PDF_TO_JSON.getValue())) {
					PdfToOther.convertPdfToJson(switchData);
				} else if (action.equalsIgnoreCase(EnumActionType.PDF_TO_HTML.getValue())) {
					PdfToOther.convertPdfToHtml(switchData.getFromFile(), switchData.getToDir());
				} else if (action.equalsIgnoreCase(EnumActionType.PDF_TO_TEXT_BBOX.getValue())) {
					PdfToTextBbox.convertPdfToTextBbox(switchData);
				} else if (action.equalsIgnoreCase(EnumActionType.PDF_TO_IMAGE_BBOX.getValue())) {
					PdfToImageBbox.convertPdfToImageBbox(switchData);
				} else if (action.equalsIgnoreCase(EnumActionType.IMG_TO_PDF.getValue())) {
					List<String> imagePathList = Arrays.<String>asList(switchData.getFromFile().split("\\|"));
					OtherToPdf.convertImageToPdf(imagePathList, switchData.getToFile(), switchData.getWatermarktext());
				} else if (action.equalsIgnoreCase(EnumActionType.PLOT_BBOX.getValue())) {
					ImageProcessor.plotBboxAndSaveACopy(switchData.getFromFile(), switchData.getHocrFile(),
							switchData.getToDir());
				} else if (action.equalsIgnoreCase(EnumActionType.IMG_FROM_PDF.getValue())) {
					PdfToOther.extractImagesFromPdf(switchData.getFromFile(), switchData.getToDir(),
							switchData.getImageFormats(), switchData.getPages());
				} else {
					isShowHelpText = true;
				}
			} else {
				isShowHelpText = true;
			}

			if (isShowHelpText) {
				CommonUtil.returnResultToCaller(HELP_TEXT);
			}
		} catch (Exception ex) {
			LOGGER.error("Error occurred in main method.", ex);
			CommonUtil.returnResultToCaller("Error occurred in main method. Please refer to log file for details.");
		}
	}

	private static SwitchData getSwitchData(Map<String, String> switchMap) {
		SwitchData switchData = new SwitchData();

		switchData.setFromFile(switchMap.getOrDefault(EnumSwitchName.FROM_FILE.getValue(), ""));

		switchData.setToFile(switchMap.getOrDefault(EnumSwitchName.TO_FILE.getValue(), ""));
		switchData.setToDir(switchMap.getOrDefault(EnumSwitchName.TO_DIR.getValue(), null));

		switchData.setHocrFile(switchMap.getOrDefault(EnumSwitchName.HOCR_FILE.getValue(), ""));
		switchData.setTimeout(Integer.valueOf(switchMap.getOrDefault(EnumSwitchName.TIMEOUT.getValue(), "60")));
		switchData.setDpi(Integer.parseInt(
				switchMap.getOrDefault(EnumSwitchName.DPI.getValue(), String.valueOf(PdfToOther.DEFAULT_DPI))));
		switchData.setPages(switchMap.getOrDefault(EnumSwitchName.PAGES.getValue(), Constants.DEFAULT_PAGES));
		switchData.setWatermarktext(switchMap.getOrDefault(EnumSwitchName.WATERMARK_TEXT.getValue(), ""));

		switchData.setPageWidth(Integer.parseInt(switchMap.getOrDefault(EnumSwitchName.PAGE_WIDTH.getValue(), "0")));
		switchData.setPageHeight(Integer.parseInt(switchMap.getOrDefault(EnumSwitchName.PAGE_HEIGHT.getValue(), "0")));

		switchData.setPlotBbox(
				Boolean.parseBoolean(switchMap.getOrDefault(EnumSwitchName.PLOT_BBOX.getValue(), "False")));
		switchData.setSaveResource(
				Boolean.parseBoolean(switchMap.getOrDefault(EnumSwitchName.SAVE_RESOURCE.getValue(), "False")));
		switchData.setImageFormats(
				switchMap.getOrDefault(EnumSwitchName.IMG_FORMAT.getValue(), Constants.IMAGE_FORMAT_JPG));
		switchData.setAngles(switchMap.getOrDefault(EnumSwitchName.ANGLES.getValue(), "0"));

		Map<String, int[]> bboxNameValueMap = new LinkedHashMap<>();
		// switches can be any word starting with "bbox" followed by any other char(s)
		for (Map.Entry<String, String> entry : switchMap.entrySet()) {
			String key = entry.getKey();
			if (key.startsWith(EnumSwitchName.BBOX.getValue())) {
				String value = switchMap.getOrDefault(key, "");
				if (value.length() > 0) {
					String[] tokens = value.split(",");
					int size = tokens.length;
					int[] arr = new int[size];
					for (int j = 0; j < size; j++) {
						arr[j] = Integer.parseInt(tokens[j]);
					}
					bboxNameValueMap.put(key, arr);
				}
			}
		}
		switchData.setBboxNameValueMap(bboxNameValueMap);

		return switchData;
	}

	private static Map<String, String> getSwitchMap(String[] tokens) {
		Map<String, String> switchMap = new LinkedHashMap<String, String>();
		for (int i = 0; i < tokens.length; i++) {
			if (tokens[i].startsWith(SWITCH_PREFIX)) {
				String switchName = tokens[i].substring(SWITCH_PREFIX.length());
				String switchValue = "";
				if (((i + 1) < tokens.length) && !tokens[i + 1].startsWith(SWITCH_PREFIX)) {
					switchValue = tokens[i + 1];
					i++;
				}
				switchMap.put(switchName, switchValue);
			}
		}
		return switchMap;
	}

	private static void validateSwitches(Map<String, String> switchMap) throws Exception {
		for (Map.Entry<String, String> entry : switchMap.entrySet()) {
			if (entry.getValue() == "") {
				throw new Exception("Value not provided for --" + entry.getKey());
			}
		}
	}

}
