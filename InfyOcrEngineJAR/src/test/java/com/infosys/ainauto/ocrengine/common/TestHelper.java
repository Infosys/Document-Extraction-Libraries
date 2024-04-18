/** =============================================================================================================== *
 * Copyright 2019 Infosys Ltd.                                                                                      *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */
package com.infosys.ainauto.ocrengine.common;

import java.io.File;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class TestHelper {

	public static String getFileFullPathFromClassPath(String fileName) throws Exception {
		String fileFullPath = "";
		try {
			ClassLoader classLoader = Thread.currentThread().getContextClassLoader();
			fileFullPath = decodeUrl(classLoader.getResource(fileName).getPath());
		} catch (Throwable th) {
			throw new Exception("Error while loading properties file", th);
		}
		return fileFullPath;
	}

	public static boolean doesFileExist(String fileName) {
		if (fileName == null || fileName.length() == 0) {
			return false;
		}
		return new File(fileName).exists();
	}

	public static void recursiveDelete(File file) {
		// to end the recursive loop
		if (!file.exists())
			return;

		// if directory, go inside and call recursively
		if (file.isDirectory()) {
			for (File f : file.listFiles()) {
				// call recursively
				recursiveDelete(f);
			}
		}
		file.delete();
	}

	public static boolean deleteFile(String fileName) {
		return new File(fileName).delete();
	}

	private static String decodeUrl(String urlString) throws Exception {
		return URLDecoder.decode(urlString, StandardCharsets.UTF_8.name());
	}

	public static List<String> getListOfFiles(String dir) {
		return Stream.of(new File(dir).listFiles())
				.filter(file -> !file.isDirectory())
				.map(File::getName)
				.collect(Collectors.toList());
	}
}
