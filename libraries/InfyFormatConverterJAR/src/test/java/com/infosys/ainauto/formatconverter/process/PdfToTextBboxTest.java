/** =============================================================================================================== *
 * Copyright 2019 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */
package com.infosys.ainauto.formatconverter.process;

import static org.junit.Assert.assertTrue;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.FixMethodOrder;
import org.junit.Test;
import org.junit.runners.MethodSorters;

import com.infosys.ainauto.formatconverter.common.Constants;
import com.infosys.ainauto.formatconverter.common.TestHelper;
import com.infosys.ainauto.formatconverter.model.SwitchData;

@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class PdfToTextBboxTest {

	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
	}

	@Test
	public void testPlotBboxAndSaveACopy() throws Exception {
		String pdfFileName = "native-sample-1.pdf";
		String pdfPath = TestHelper.getFileFullPathFromClassPath(pdfFileName);
		String outputPath = "C:/Temp/format-converter-unit-test-output";

		SwitchData switchData = new SwitchData();
		switchData.setFromFile(pdfPath);
		switchData.setToDir(outputPath);
		switchData.setPlotBbox(true);
		switchData.setPages(Constants.DEFAULT_PAGES);

		String expectedJsonFilePath = outputPath + "/" + pdfFileName.replace(".pdf", "_bbox.json");
		String expectedPdfWithBboxFilePath = outputPath + "/" + pdfFileName.replace(".pdf", "_bbox.pdf");
		
		// Delete output files if they exist
		TestHelper.deleteFile(expectedJsonFilePath);
		TestHelper.deleteFile(expectedPdfWithBboxFilePath);

		PdfToTextBbox.convertPdfToTextBbox(switchData);

		assertTrue("Json file should exist", TestHelper.doesFileExist(expectedJsonFilePath));
		assertTrue("PDF with bbox file should exist", TestHelper.doesFileExist(expectedPdfWithBboxFilePath));
	}

	@AfterClass
	public static void tearDown() throws Exception {
	}
}
