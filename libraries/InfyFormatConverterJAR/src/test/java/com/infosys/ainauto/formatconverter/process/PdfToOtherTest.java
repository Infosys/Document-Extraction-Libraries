/** =============================================================================================================== *
 * Copyright 2019 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */
package com.infosys.ainauto.formatconverter.process;

import static org.junit.Assert.assertTrue;

import java.util.Arrays;
import java.util.stream.Stream;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.FixMethodOrder;
import org.junit.Test;
import org.junit.runners.MethodSorters;

import com.infosys.ainauto.formatconverter.common.Constants;
import com.infosys.ainauto.formatconverter.common.TestHelper;

@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class PdfToOtherTest {

	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
	}

	@Test
	public void testExtractImagesFromPdf() throws Exception {
		String pdfFileName = "pdfwithimages/sample1.pdf";
		String pdfFilePath = TestHelper.getFileFullPathFromClassPath(pdfFileName);
		String outputPath = "C:/Temp/format-converter-unit-test-output";

		String JPG_FILES_TO_EXPECT[] = { "1-1.jpg", "1-2.jpg", "2-1.jpg" };
		String PNG_FILES_TO_EXPECT[] = { "1-1.png", "1-2.png", "1-3.png", "2-1.png", "2-2.png", "2-3.png", "2-4.png" };

		String FILES_TO_EXPECT[] = Stream.concat(Arrays.stream(JPG_FILES_TO_EXPECT), Arrays.stream(PNG_FILES_TO_EXPECT))
				.toArray(String[]::new);

		// Delete output files if they exist
		for (String file : FILES_TO_EXPECT) {
			String fileFullPath = outputPath + "/" + file;
			TestHelper.deleteFile(fileFullPath);
		}

		PdfToOther.extractImagesFromPdf(pdfFilePath, outputPath, "jpg,png", Constants.DEFAULT_PAGES);

		for (String file : FILES_TO_EXPECT) {
			String fileFullPath = outputPath + "/" + file;
			assertTrue("File " + fileFullPath + " should exist", TestHelper.doesFileExist(fileFullPath));
		}
	}

	@AfterClass
	public static void tearDown() throws Exception {
	}
}
