/** =============================================================================================================== *
 * Copyright 2019 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */
package com.infosys.ainauto.formatconverter;

import static org.junit.Assert.assertTrue;

import java.io.File;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.stream.Stream;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.FixMethodOrder;
import org.junit.Test;
import org.junit.runners.MethodSorters;

import com.infosys.ainauto.formatconverter.common.TestHelper;

@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class ConverterTest {

	private static String RESOURCE_PATH = System.getProperty("user.dir") + "\\src\\test\\resources\\";;
	private static String UT_ROOT_PATH = TestHelper.getUnitTestDataFolderRootPath();

	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
	}

	// TODO Enable @Test to test methods. Due to absolute path used in test cases
	// disable it to avoid build time issue.

	 @Test
	public void testMainPdfToImage() throws Exception {
		String args[] = { "D:\\Play\\VBS\\Data.pdf" };
		Converter.main(args);
	}

	// @Test
	public void testMainPdfToImage1() throws Exception {
		
		String imagePath = RESOURCE_PATH + "sample";
		TestHelper.recursiveDelete(new File(imagePath));
		String pdfFilePath = RESOURCE_PATH + "sample.pdf";
		String args[] = { "pdfToImg", pdfFilePath };
		Converter.main(args);
		assertTrue("PDF file should exist", TestHelper.doesFileExist(imagePath));
	}

	// @Test
	public void testMainPdfToImage_DPI() throws Exception {
		
		String imagePath = RESOURCE_PATH + "sample";
		TestHelper.recursiveDelete(new File(imagePath));
		String pdfFilePath = RESOURCE_PATH + "sample.pdf";
		String args[] = { "pdfToImg", pdfFilePath, "400" };
		Converter.main(args);
		assertTrue("PDF file should exist", TestHelper.doesFileExist(imagePath));
	}

	// @Test
	public void testMainPdfToImage_OutPath_Page() throws Exception {
		
		String imagePath = RESOURCE_PATH + "sample";
		TestHelper.recursiveDelete(new File(imagePath));
		String pdfFilePath = RESOURCE_PATH + "sample.pdf";
		String args[] = { "pdfToImg", pdfFilePath, "400", RESOURCE_PATH, "2" };
		Converter.main(args);
		assertTrue("PDF file should exist", TestHelper.doesFileExist(imagePath));
	}

	// @Test
	public void testMainImageToPdf() throws Exception {
		
		
		String imagePath = RESOURCE_PATH + "sample\\2.jpg";
		String pdfFilePath = RESOURCE_PATH + "sample.pdf";
		String args[] = { "ImgToPdf", "--fromfile", imagePath, "--tofile", pdfFilePath, "--watermarktext",
				"NOT ORIGINAL" };
		Converter.main(args);
		assertTrue("PDF file should exist", TestHelper.doesFileExist(pdfFilePath));
	}

	// @Test
	public void testMainWordToPdf() throws Exception {
		String args[] = { "WORDTOPDF", "D:\\Play\\VBS\\Data.docx", "D:\\Play\\VBS\\Data.pdf", "60" };
		Converter.main(args);
	}
	
	// ############## PdfToMultiPdf ##############

	@Test
	public void testMainPdfToMultiPdf1() throws Exception {
		
		String pdfFilePath = TestHelper.getFileFullPathFromClassPath("sample.pdf");
		String outputFolderPath = pdfFilePath.substring(0, pdfFilePath.lastIndexOf("/")+1) + "/output";
		String baselineFolderPath = UT_ROOT_PATH + "/PdfToMultiPdf/uc01_baseline";
		
		TestHelper.recursiveDelete(new File(outputFolderPath));
		
		String[] argsCore = { "pdfToMultiPdf", "--fromfile", pdfFilePath, "--todir", outputFolderPath };
		String[] argsExtra = {};
		String[] args = Stream.concat(Arrays.stream(argsCore), Arrays.stream(argsExtra)).toArray(String[]::new);
		
		Converter.main(args);
		assertTrue("Expected files should exist", TestHelper.getListOfFiles(outputFolderPath).size() == TestHelper
				.getListOfFiles(baselineFolderPath).size());
		
	}

	@Test
	public void testMainPdfToMultiPdf2() throws Exception {
		
		String pdfFilePath = TestHelper.getFileFullPathFromClassPath("sample.pdf");
		String outputFolderPath = pdfFilePath.substring(0, pdfFilePath.lastIndexOf("/")+1) + "/output";
		String baselineFolderPath = UT_ROOT_PATH + "/PdfToMultiPdf/uc02_baseline";
		
		TestHelper.recursiveDelete(new File(outputFolderPath));
		
		String[] argsCore = { "pdfToMultiPdf", "--fromfile", pdfFilePath, "--todir", outputFolderPath };
		String[] argsExtra = { "--pages", "1-10"};
		String[] args = Stream.concat(Arrays.stream(argsCore), Arrays.stream(argsExtra)).toArray(String[]::new);
		
		Converter.main(args);
		assertTrue("Expected files should exist", TestHelper.getListOfFiles(outputFolderPath).size() == TestHelper
				.getListOfFiles(baselineFolderPath).size());
	}

	@Test
	public void testMainPdfToMultiPdf3() throws Exception {
		
		String pdfFilePath = TestHelper.getFileFullPathFromClassPath("sample.pdf");
		String outputFolderPath = pdfFilePath.substring(0, pdfFilePath.lastIndexOf("/")+1) + "/output";
		String baselineFolderPath = UT_ROOT_PATH + "/PdfToMultiPdf/uc03_baseline";
		
		TestHelper.recursiveDelete(new File(outputFolderPath));
		
		String[] argsCore = { "pdfToMultiPdf", "--fromfile", pdfFilePath, "--todir", outputFolderPath };
		String[] argsExtra = { "--pages", "2"};
		String[] args = Stream.concat(Arrays.stream(argsCore), Arrays.stream(argsExtra)).toArray(String[]::new);
		
		Converter.main(args);
		assertTrue("Expected files should exist", TestHelper.getListOfFiles(outputFolderPath).size() == TestHelper
				.getListOfFiles(baselineFolderPath).size());
	}
	
	// ############## RotatePdfPage ##############

	@Test
	public void testMainRotatePdfPage1() throws Exception {
		String pdfFilePath = TestHelper.getFileFullPathFromClassPath("sample.pdf");
		String outputFolderPath = pdfFilePath.substring(0, pdfFilePath.lastIndexOf("/")+1) + "/output";
		String baselineFolderPath = UT_ROOT_PATH + "/RotatePdfPage/uc01_baseline";
		
		TestHelper.recursiveDelete(new File(outputFolderPath));
		
		String[] argsCore = { "rotatePdfPage", "--fromfile", pdfFilePath, "--todir", outputFolderPath };
		String[] argsExtra = { "--pages", "1,2" , "--angles","90,180"};
		String[] args = Stream.concat(Arrays.stream(argsCore), Arrays.stream(argsExtra)).toArray(String[]::new);
		
		Converter.main(args);
		assertTrue("Expected files should exist", TestHelper.getListOfFiles(outputFolderPath).size() == TestHelper
				.getListOfFiles(baselineFolderPath).size());
	}

	// ############## PdfToTextBbox ##############
	
	@Test
	public void testPdfToTextBbox1() throws Exception {
		String pdfFilePath = UT_ROOT_PATH + "/Samples/swnlp.pdf";
		String outputFolderPath = UT_ROOT_PATH + "/PdfToTextBbox/uc01";
		String baselineFolderPath = UT_ROOT_PATH + "/PdfToTextBbox/uc01_baseline";
		
		TestHelper.recursiveDelete(new File(outputFolderPath));
		
		String[] argsCore = { "PdfToTextBbox", "--fromfile", pdfFilePath, "--todir", outputFolderPath };
		String[] argsExtra = { "--plotbbox", "True" };
		String[] args = Stream.concat(Arrays.stream(argsCore), Arrays.stream(argsExtra)).toArray(String[]::new);
		
		Converter.main(args);
		assertTrue("Expected files should exist", TestHelper.getListOfFiles(outputFolderPath).size() == TestHelper
				.getListOfFiles(baselineFolderPath).size());
	}
	
	@Test
	public void testPdfToTextBbox2() throws Exception {
		String pdfFilePath = UT_ROOT_PATH + "/Samples/page-14-17.pdf";
		String outputFolderPath = UT_ROOT_PATH + "/PdfToTextBbox/uc02";
		String baselineFolderPath = UT_ROOT_PATH + "/PdfToTextBbox/uc02_baseline";
		
		TestHelper.recursiveDelete(new File(outputFolderPath));
		
		String[] argsCore = { "PdfToTextBbox", "--fromfile", pdfFilePath, "--todir", outputFolderPath };
		String[] argsExtra = { "--plotbbox", "True" };
		String[] args = Stream.concat(Arrays.stream(argsCore), Arrays.stream(argsExtra)).toArray(String[]::new);
		
		Converter.main(args);
		assertTrue("Expected files should exist", TestHelper.getListOfFiles(outputFolderPath).size() == TestHelper
				.getListOfFiles(baselineFolderPath).size());
	}
	
	@Test
	public void testPdfToTextBbox3() throws Exception {
		String pdfFilePath = UT_ROOT_PATH + "/Samples/sports_statistics.pdf";
		String outputFolderPath = UT_ROOT_PATH + "/PdfToTextBbox/uc03";
		String baselineFolderPath = UT_ROOT_PATH + "/PdfToTextBbox/uc03_baseline";
		
		TestHelper.recursiveDelete(new File(outputFolderPath));
		
		String[] argsCore = { "PdfToTextBbox", "--fromfile", pdfFilePath, "--todir", outputFolderPath };
		String[] argsExtra = { "--plotbbox", "True" };
		String[] args = Stream.concat(Arrays.stream(argsCore), Arrays.stream(argsExtra)).toArray(String[]::new);
		
		Converter.main(args);
		assertTrue("Expected files should exist", TestHelper.getListOfFiles(outputFolderPath).size() == TestHelper
				.getListOfFiles(baselineFolderPath).size());
	}
		
	// ############## PdfToImageBbox ##############
	
	@Test
	public void testPdfToImageBbox1() throws Exception {
		String pdfFilePath = UT_ROOT_PATH + "/Samples/page-14-17.pdf";
		String outputFolderPath = UT_ROOT_PATH + "/PdfToImageBbox/uc01";
		String baselineFolderPath = UT_ROOT_PATH + "/PdfToImageBbox/uc01_baseline";
		
		TestHelper.recursiveDelete(new File(outputFolderPath));
		
		String[] argsCore = { "PdfToImageBbox", "--fromfile", pdfFilePath, "--todir", outputFolderPath };
		String[] argsExtra = { "--saveresource", "True", "--plotbbox", "True" };
		String[] args = Stream.concat(Arrays.stream(argsCore), Arrays.stream(argsExtra)).toArray(String[]::new);
		
		Converter.main(args);
		assertTrue("Expected files should exist", TestHelper.getListOfFiles(outputFolderPath).size() == TestHelper
				.getListOfFiles(baselineFolderPath).size());
	}
	//JP2 image conversion
	// @Test
	// public void testPdfToImageBbox2() throws Exception {
	// 	// System.out.println(System.getProperty("java.class.path"));
	// 	String pdfFilePath = "C:/DPP/infy_libraries_client/CONTAINER/data/temp/data/work/D-58f9cebe-dfd8-4235-bbc6-027f425fe189/TCS-ar-22_simple_7-8,10-14,33,83-84_1.pdf";
	// 	String outputFolderPath = "C:/DPP/infy_libraries_client/CONTAINER/data/temp/data/work/D-58f9cebe-dfd8-4235-bbc6-027f425fe189/TCS-ar-22_simple_7-8,10-14,33,83-84_1.pdf_files";
	// 	// String baselineFolderPath = UT_ROOT_PATH + "/PdfToImageBbox/uc01_baseline";
		
	// 	TestHelper.recursiveDelete(new File(outputFolderPath));
		
	// 	String[] argsCore = { "PdfToImageBbox", "--fromfile", pdfFilePath, "--todir", outputFolderPath };
	// 	String[] argsExtra = { "--dpi", "300","--saveresource", "True"};
	// 	String[] args = Stream.concat(Arrays.stream(argsCore), Arrays.stream(argsExtra)).toArray(String[]::new);
		
	// 	Converter.main(args);
	// 	// System.out.println("Expected files should exist" + TestHelper.getListOfFiles(outputFolderPath));
	// 	// assertTrue("Expected files should exist", TestHelper.getListOfFiles(outputFolderPath).size() == TestHelper
	// 	// 		.getListOfFiles(baselineFolderPath).size());
	// }
	@AfterClass
	public static void tearDown() throws Exception {
	}

}
