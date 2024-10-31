/** =============================================================================================================== *
 * Copyright 2024 Infosys Ltd.                                                                                      *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */
package com.infosys.ainauto.ocrengine;

import static org.junit.Assert.assertTrue;

import java.io.File;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.FixMethodOrder;
import org.junit.Test;
import org.junit.runners.MethodSorters;

import com.infosys.ainauto.ocrengine.common.TestHelper;

@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class OcrTest {

    private static String RESOURCE_PATH = System.getProperty("user.dir") + "\\src\\test\\resources\\";;
    private static String MODEL_DIR_PATH = "C:\\MyProgramFiles\\AI\\models\\tessdata";

    @BeforeClass
    public static void setUpBeforeClass() throws Exception {
    }

    @Test
    public void testMainImageToTextOnlyTxt() throws Exception {
        String outputPath = RESOURCE_PATH + "output\\";
        String fromFile = RESOURCE_PATH + "input\\" + "eng.png";
        String expectedTxtFilePath = outputPath + "eng.png.txt";
        String lang = "eng";
        String ocrFormat = "txt";
        String pageSegMode = "3";
        TestHelper.recursiveDelete(new File(expectedTxtFilePath));
        String args[] = { "--fromfile", fromFile, "--modeldir", MODEL_DIR_PATH,
                "--ocrformat", ocrFormat, "--todir", outputPath, "--lang", lang, "--psm", pageSegMode };
        Ocr.main(args);
        assertTrue("Text File should exist", TestHelper.doesFileExist(expectedTxtFilePath));
    }

    @Test
    public void testMainImageToTextNoLang() throws Exception {
        String outputPath = RESOURCE_PATH + "output\\";
        String fromFile = RESOURCE_PATH + "input\\" + "eng.png";
        String expectedTxtFilePath = outputPath + "eng.png.txt";
        String ocrFormat = "txt";
        String pageSegMode = "3";
        TestHelper.recursiveDelete(new File(expectedTxtFilePath));
        String args[] = { "--fromfile", fromFile, "--modeldir", MODEL_DIR_PATH,
                "--ocrformat", ocrFormat, "--todir", outputPath, "--psm", pageSegMode };
        Ocr.main(args);
        assertTrue("Text File should exist", TestHelper.doesFileExist(expectedTxtFilePath));
    }

    @Test
    public void testMainImageToTextBoth() throws Exception {
        String outputPath = RESOURCE_PATH + "output\\";
        String fromFile = RESOURCE_PATH + "input\\" + "eng.png";
        String expectedTxtFilePath = outputPath + "eng.png.txt";
        String expectedHocrFilePath = outputPath + "eng.png.hocr";
        String ocrFormat = "txt,hocr";
        String pageSegMode = "3";
        TestHelper.recursiveDelete(new File(expectedTxtFilePath));
        TestHelper.recursiveDelete(new File(expectedHocrFilePath));
        String args[] = { "--fromfile", fromFile, "--modeldir", MODEL_DIR_PATH,
                "--ocrformat", ocrFormat, "--todir", outputPath, "--psm", pageSegMode };
        Ocr.main(args);
        assertTrue("Text File should exist", TestHelper.doesFileExist(expectedTxtFilePath));
        assertTrue("Hocr File should exist", TestHelper.doesFileExist(expectedHocrFilePath));
    }

    @Test
    public void testMainImageToTextNoFromFile() {
        String outputPath = RESOURCE_PATH + "output\\";
        String toFile = outputPath + "hin.txt";
        String lang = "hin";
        String ocrFormat = "hocr";
        TestHelper.recursiveDelete(new File(toFile));
        String args[] = { "--fromfile", "--modeldir", MODEL_DIR_PATH,
                "--ocrformat", ocrFormat, "--todir", outputPath, "--lang", lang };
        Ocr.main(args);
    }

    @Test
    public void testMainImageToTextOnlyHocr() {
        String outputPath = RESOURCE_PATH + "output\\";
        String fromFile = RESOURCE_PATH + "input\\" + "hin.png";
        String expectedHocrFilePath = outputPath + "hin.png.hocr";
        String lang = "hin";
        String ocrFormat = "hocr";
        String pageSegMode = "3";
        TestHelper.recursiveDelete(new File(expectedHocrFilePath));
        String args[] = { "--fromfile", fromFile, "--modeldir", MODEL_DIR_PATH,
                "--ocrformat", ocrFormat, "--todir", outputPath, "--lang", lang, "--psm", pageSegMode };
        Ocr.main(args);
        assertTrue("Hocr File should exist", TestHelper.doesFileExist(expectedHocrFilePath));
    }

    @Test
    public void testMainImageToTextModelFilePresent() throws Exception {
        String outputPath = RESOURCE_PATH + "output\\";
        String fromFile = RESOURCE_PATH + "input\\" + "hin.png";
        String expectedHocrFilePath = outputPath + "hin.png.hocr";
        String lang = "abc"; // Invalid language
        String ocrFormat = "hocr";
        String pageSegMode = "3";
        TestHelper.recursiveDelete(new File(expectedHocrFilePath));
        String args[] = { "--fromfile", fromFile, "--modeldir", MODEL_DIR_PATH,
                "--ocrformat", ocrFormat, "--todir", outputPath, "--lang", lang, "--psm", pageSegMode };
        Ocr.main(args);
        // assertTrue("Train data not present", TestHelper.doesFileExist(toFile));
    }

    @Test
    public void testMainImageToTextNoPageSegMode() throws Exception {
        String outputPath = RESOURCE_PATH + "output\\";
        String fromFile = RESOURCE_PATH + "input\\" + "eng.png";
        String expectedTxtFilePath = outputPath + "eng.png.txt";
        String lang = "eng";
        String ocrFormat = "txt";
        TestHelper.recursiveDelete(new File(expectedTxtFilePath));
        String args[] = { "--fromfile", fromFile, "--modeldir", MODEL_DIR_PATH,
                "--ocrformat", ocrFormat, "--todir", outputPath, "--lang", lang };
        Ocr.main(args);
        assertTrue("Text File should exist", TestHelper.doesFileExist(expectedTxtFilePath));
    }

    @AfterClass
    public static void tearDown() throws Exception {
    }
}