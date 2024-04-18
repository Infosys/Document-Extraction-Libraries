/** =============================================================================================================== *
 * Copyright 2024 Infosys Ltd.                                                                                      *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */

package com.infosys.ainauto.ocrengine.process;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
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

public class TesseractHandler {

    private static final String SUPPORTED_OCR_FORMATS[] = { Constants.OCR_FORMAT_HOCR, Constants.OCR_FORMAT_TXT };

    public static void extractText(SwitchData switchData)
            throws TesseractException, Exception {

        String imageFilePath = switchData.getFromFile();
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

            String outputDirPathActual = getOutputDirPathActual(imageFilePath, outputDir);
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
            throws TesseractException, FileNotFoundException, IOException {

        String imageFilePath = switchData.getFromFile();
        File image = new File(imageFilePath);
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

        tesseract.setPageSegMode(3);
        tesseract.setVariable("hocr_font_info", "0");
        String result = tesseract.doOCR(image);

        String fileName = CommonUtil.getPathTokens(imageFilePath)[CommonUtil.PATH_TOKEN_FILE_NAME]
                + "." + CommonUtil.getPathTokens(imageFilePath)[CommonUtil.PATH_TOKEN_FILE_EXT];

        result = result.replace(imageFilePath, fileName);

        String outputFileName = CommonUtil.getPathTokens(imageFilePath)[CommonUtil.PATH_TOKEN_FILE_NAME]
                + "." + CommonUtil.getPathTokens(imageFilePath)[CommonUtil.PATH_TOKEN_FILE_EXT]
                + fileExtension;
        outputFilePath = outputDirPathActual + "/" + outputFileName;
        Writer fstream = new OutputStreamWriter(
                new FileOutputStream(outputFilePath), StandardCharsets.UTF_8);
        fstream.write(result);
        fstream.close();
        return outputFilePath;
    }

    private static String getOutputDirPathActual(String imageFilePath, String outputDir) {
        String outputDirPathActual;
        if (outputDir == null) {
            outputDirPathActual = CommonUtil.getActualOutputDirPath(outputDir, imageFilePath, false);
        } else {
            outputDirPathActual = outputDir;
        }
        return outputDirPathActual;
    }

    private static void validateModelFile(String modelDir, String lang) throws Exception {
        String fileName = lang + Constants.FILE_EXT_MODEL;
        String trainedDataFilePath = modelDir + "\\" + fileName;
        if (!new File(trainedDataFilePath).exists()) {

            throw new Exception("Model File not found for language '" + lang
                    + "'.Please verify if a valid traindata is present in the 'models' folder.");
        }
    }
}
