/** =============================================================================================================== *
 * Copyright 2024 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */

package com.infosys.ainauto.ocrengine.process;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.lang.NumberFormatException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import com.infosys.ainauto.ocrengine.common.CommonUtil;
import com.infosys.ainauto.ocrengine.common.Constants;
import com.infosys.ainauto.ocrengine.model.SwitchData;

import net.sourceforge.tess4j.Tesseract;
import net.sourceforge.tess4j.TesseractException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.util.DefaultIndenter;
import com.fasterxml.jackson.core.util.DefaultPrettyPrinter;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

public class TesseractHandler {

    private static final String SUPPORTED_OCR_FORMATS[] = { Constants.OCR_FORMAT_HOCR, Constants.OCR_FORMAT_TXT };

    public static void extractText(SwitchData switchData)
            throws TesseractException, Exception {

        String inputFilePath = switchData.getFromFile();
        String outputDir = switchData.getToDir();
        String ocrFormat = switchData.getOcrFormat();

        List<String> outputFilePathList = new ArrayList<String>();
        validateModelFile(switchData.getModelDirPath(), switchData.getLanguage());
        List<String> requestedOcrFormats = new ArrayList<>();
        {
            String[] ocrFormatArray = ocrFormat.split(",");
            List<String> supportedOcrFormats = new ArrayList<>(Arrays.asList(SUPPORTED_OCR_FORMATS));
            for (String ocrFormat1 : ocrFormatArray) {
                if (supportedOcrFormats.contains(ocrFormat1)) {
                    requestedOcrFormats.add(ocrFormat1);
                } else {
                    throw new Exception("Unsupported OCR format: " + ocrFormat1);
                }
            }
        }
        try {

            String outputDirPathActual = getOutputDirPathActual(inputFilePath, outputDir);
            CommonUtil.createDirsRecursively(outputDirPathActual);
            if (requestedOcrFormats.contains(Constants.OCR_FORMAT_HOCR)) {
                String outputFilePath = writeToFile(switchData, Constants.FILE_EXT_HOCR, outputDirPathActual);
                outputFilePathList.add(outputFilePath);
            }
            if (requestedOcrFormats.contains(Constants.OCR_FORMAT_TXT)) {
                String outputFilePath = writeToFile(switchData, Constants.FILE_EXT_TXT, outputDirPathActual);
                outputFilePathList.add(outputFilePath);
            }
        } catch (Exception ex) {
            throw new Exception("Error occurred while extracting text from the image", ex);
        }
        CommonUtil.returnResultToCaller(outputFilePathList);
    }

    private static String writeToFile(SwitchData switchData, String fileExtension,
            String outputDirPathActual)
            throws TesseractException, FileNotFoundException, IOException, NumberFormatException {

        String inputFilePath = switchData.getFromFile();
        String outputFilePath;
        Tesseract tesseract = new Tesseract();
        tesseract.setLanguage(switchData.getLanguage());
        // String dataPath = String.join("\\", new File("").getAbsolutePath(),
        // Constants.TRAINED_DATA_DIR);
        tesseract.setDatapath(switchData.getModelDirPath());
        if (fileExtension.equals(Constants.FILE_EXT_HOCR)) {
            tesseract.setVariable("tessedit_create_hocr", "1");
        } else if (fileExtension.equals(Constants.FILE_EXT_TXT)) {
            tesseract.setVariable("tessedit_create_txt", "1");
        }

        int pageSegMode;

        try {
            pageSegMode = Integer.parseInt(switchData.getPageSegMode());
            if (pageSegMode != 3 && pageSegMode != 6 && pageSegMode != 7) {
                throw new NumberFormatException("Page segmentation mode must be 3, 6, or 7.");
            }
        } catch (NumberFormatException e) {
            throw new NumberFormatException("Invalid page segmentation mode: " + switchData.getPageSegMode());
        }

        tesseract.setPageSegMode(pageSegMode);
        tesseract.setVariable("hocr_font_info", "0");
        if (inputFilePath.endsWith(".json")) {
            ObjectMapper objectMapper = new ObjectMapper();
            JsonNode rootNode = objectMapper.readTree(new File(inputFilePath));
            for (JsonNode node : rootNode) {
                String imagePath = node.get("image_path").asText();
                String data = getDataFromImage(imagePath, tesseract);
                ((ObjectNode) node).put("data", data);
            }
            outputFilePath = getOutputFilePath(inputFilePath, outputDirPathActual, "_infy_ocr_engine.json");
            // objectMapper.writeValue(new File(outputFilePath), rootNode);
            // objectMapper.writer(new DefaultPrettyPrinter()).writeValue(new
            // File(outputFilePath), rootNode);
            DefaultPrettyPrinter prettyPrinter = new DefaultPrettyPrinter();
            prettyPrinter.indentArraysWith(DefaultIndenter.SYSTEM_LINEFEED_INSTANCE.withIndent("    "));
            prettyPrinter.indentObjectsWith(DefaultIndenter.SYSTEM_LINEFEED_INSTANCE.withIndent("    "));

            objectMapper.writer(prettyPrinter).writeValue(new File(outputFilePath), rootNode);
        } else {
            String result = getDataFromImage(inputFilePath, tesseract);
            outputFilePath = getOutputFilePath(inputFilePath, outputDirPathActual, fileExtension);
            Writer fstream = new OutputStreamWriter(
                    new FileOutputStream(outputFilePath), StandardCharsets.UTF_8);
            fstream.write(result);
            fstream.close();
        }
        return outputFilePath;
    }

    private static String getDataFromImage(String imageFilePath, Tesseract tesseract)
            throws TesseractException {
        File image = new File(imageFilePath);
        String result = tesseract.doOCR(image);

        String fileName = CommonUtil.getPathTokens(imageFilePath)[CommonUtil.PATH_TOKEN_FILE_NAME]
                + "." + CommonUtil.getPathTokens(imageFilePath)[CommonUtil.PATH_TOKEN_FILE_EXT];

        result = result.replace(imageFilePath, fileName);
        result = result.replaceAll("\\n$", "");

        return result;
    }

    private static String getOutputFilePath(String inputFilePath, String outputDirPathActual, String fileExtension) {
        String outputFileName = CommonUtil.getPathTokens(inputFilePath)[CommonUtil.PATH_TOKEN_FILE_NAME]
                + "." + CommonUtil.getPathTokens(inputFilePath)[CommonUtil.PATH_TOKEN_FILE_EXT]
                + fileExtension;
        return outputDirPathActual + "/" + outputFileName;
    }

    private static String getOutputDirPathActual(String inputFilePath, String outputDir) {
        String outputDirPathActual;
        if (outputDir == null) {
            outputDirPathActual = CommonUtil.getActualOutputDirPath(outputDir, inputFilePath, false);
        } else {
            outputDirPathActual = outputDir;
        }
        return outputDirPathActual;
    }

    private static void validateModelFile(String modelDir, String lang) throws Exception {
        String fileName = lang + Constants.FILE_EXT_MODEL;
        String trainedDataFilePath = modelDir + File.separator + fileName;
        if (!new File(trainedDataFilePath).exists()) {

            throw new Exception("Model File not found for language '" + lang
                    + "'.Please verify if a valid traindata is present in the 'models' folder."
                    + trainedDataFilePath);
        }
    }
}
