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

import com.infosys.ainauto.formatconverter.common.TestHelper;

@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class WordToPdfTest {

	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
	}

	// #TODO - Check if feature is valid or obsolete	
//	@Test
	public void testConvertFromWordToPdf() throws Exception {
		String wordFilePath = TestHelper.getFileFullPathFromClassPath("LoanNote.docx");
		// Remove leading slash from path e.g. /D:/abc.pdf
		wordFilePath = wordFilePath.substring(1);

		String pdfFilePath = wordFilePath.replace(".docx", ".pdf");

		// Delete PDF file if it exists
		TestHelper.deleteFile(pdfFilePath);

		WordToPdf.convertWordToPdf(wordFilePath, pdfFilePath, 60);
		assertTrue("PDF file should exist", TestHelper.doesFileExist(pdfFilePath));
	}

	@AfterClass
	public static void tearDown() throws Exception {
	}
}
