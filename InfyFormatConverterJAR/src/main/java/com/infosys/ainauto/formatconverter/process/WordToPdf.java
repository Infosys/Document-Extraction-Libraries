/** =============================================================================================================== *
 * Copyright 2020 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */

package com.infosys.ainauto.formatconverter.process;

import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.nio.file.Paths;
import java.util.concurrent.TimeUnit;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class WordToPdf {

	private static final Logger LOGGER = LoggerFactory.getLogger(WordToPdf.class);
	private static final String SCRIPT_MACRO_EXECUTOR_RELATIVE_PATH = "scripts/MsMacroExecutor.vbs";
	private static String scriptMacroExecutorFilePath = "";

	static {
		scriptMacroExecutorFilePath = getFileFullPathFromClassPath(SCRIPT_MACRO_EXECUTOR_RELATIVE_PATH);
		LOGGER.info("VB Script - Macro Executor Path={}", scriptMacroExecutorFilePath);
	}

	public static void convertWordToPdf(String wordFilePath, String pdfFilePath, int timeOutInSecs) throws Exception {
		long startTime = System.nanoTime();
		try {
			String commandToExecute = "wscript " + scriptMacroExecutorFilePath + " " + wrapInQuotes(wordFilePath) + " "
					+ wrapInQuotes(pdfFilePath);
			LOGGER.debug(commandToExecute);
			Process process = Runtime.getRuntime().exec(commandToExecute);
			if (!process.waitFor(timeOutInSecs, TimeUnit.SECONDS)) {
				LOGGER.error("Waiting time elapsed before the subprocess has exited");
			}
		} catch (IOException | InterruptedException ex) {
			throw new Exception("Error occurred while converting MS WORD to PDF", ex);
		}
		double timeElapsed = (System.nanoTime() - startTime) / 1000000000.0;
		LOGGER.info("Time taken for converting {} to {} is {} secs", wordFilePath, pdfFilePath, timeElapsed);
	}

	private static String wrapInQuotes(String str) {
		return "\"" + str + "\"";
	}

	private static String getFileFullPathFromClassPath(String fileName) {
		String fileFullPath = "";
		try {
			// 1st method to get full path
			ClassLoader classLoader = Thread.currentThread().getContextClassLoader();
			URL url = classLoader.getResource(fileName);
			if (url != null) {
				fileFullPath = Paths.get(url.toURI()).toFile().getPath();
				LOGGER.debug("fileFullPath={}", fileFullPath);
				return fileFullPath;
			}
			// 2nd method to get full path
			File file = new File(fileName);
			fileFullPath = file.getAbsolutePath();
			LOGGER.debug("fileFullPath={}", fileFullPath);

		} catch (Throwable th) {
			LOGGER.error("Unable to get file full path from classpath", th);
		}
		return fileFullPath;
	}
}
