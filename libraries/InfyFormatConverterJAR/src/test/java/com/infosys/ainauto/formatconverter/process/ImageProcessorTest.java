/** =============================================================================================================== *
 * Copyright 2019 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */
package com.infosys.ainauto.formatconverter.process;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.FixMethodOrder;
import org.junit.Test;
import org.junit.runners.MethodSorters;

import com.infosys.ainauto.formatconverter.common.TestHelper;

@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class ImageProcessorTest {

	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
	}


	@Test
	public void testPlotBboxAndSaveACopy() throws Exception {
		String imageReadPath = TestHelper.getFileFullPathFromClassPath("bordered-table-01.jpg");
		String hocrFilePath = TestHelper.getFileFullPathFromClassPath("bordered-table-01.jpg[psm=03].hocr");
		String outputDir = "C:/Temp/format-converter-unit-test-output";
		
		
		ImageProcessor.plotBboxAndSaveACopy(imageReadPath, hocrFilePath, outputDir);
	}
	
	@AfterClass
	public static void tearDown() throws Exception {
	}
}
