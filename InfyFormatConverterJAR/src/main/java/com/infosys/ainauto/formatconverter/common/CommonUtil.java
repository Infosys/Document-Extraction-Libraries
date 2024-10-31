/** =============================================================================================================== *
 * Copyright 2021 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */

package com.infosys.ainauto.formatconverter.common;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.StringWriter;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import javax.json.Json;
import javax.json.JsonArray;
import javax.json.JsonObject;
import javax.json.JsonStructure;
import javax.json.JsonWriter;
import javax.json.JsonWriterFactory;
import javax.json.stream.JsonGenerator;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Utility class for common/generic tasks.
 *
 */
public class CommonUtil {

	private static final Logger LOGGER = LoggerFactory.getLogger(CommonUtil.class);
	public static final int PATH_TOKEN_PARENT = 0;
	public static final int PATH_TOKEN_FILE_NAME = 1;
	public static final int PATH_TOKEN_FILE_EXT = 2;

	public static byte[] readFile(String filePath) {
		File file = new File(filePath);
		byte[] data = {};
		try (FileInputStream fis = new FileInputStream(file)) {
			data = new byte[(int) file.length()];
			fis.read(data);
		} catch (IOException e) {
			LOGGER.error("File read operation failed", e);
		}
		return data;
	}

	public static String getFileFullPathFromClassPath(String fileName) throws Exception {
		String fileFullPath = "";
		try {
			ClassLoader classLoader = Thread.currentThread().getContextClassLoader();

			fileFullPath = classLoader.getResource(fileName).getPath();
		} catch (Throwable th) {
			throw new Exception("Error while loading properties file", th);
		}
		return fileFullPath;
	}

	public static String readResourceFile(String fileName) {
		if (fileName == null || fileName.length() == 0) {
			return "";
		}
		StringBuilder out = new StringBuilder();
		try {
			if (!fileName.startsWith("/")) {
				fileName = "/" + fileName;
			}
			InputStream in = CommonUtil.class.getResourceAsStream(fileName);
			BufferedReader reader = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8));

			String line;
			while ((line = reader.readLine()) != null) {
				out.append(line).append("\n");
			}
			reader.close();
		} catch (IOException e) {
			LOGGER.error("Error occurred in readResourceFile()", e);
		}
		return out.toString();
	}

	public static boolean saveAsFile(String fileFullPath, String content) {
		byte data[] = content.getBytes(StandardCharsets.UTF_8);
		boolean isSuccess = true;
		try (FileOutputStream out = new FileOutputStream(fileFullPath)) {
			out.write(data);
		} catch (IOException e) {
			isSuccess = false;
			LOGGER.error("Error occurred in saveFile()", e);
		}
		return isSuccess;
	}

	/**
	 * Tokenize a file full path to parent, file name and extension
	 * 
	 * @param fileFullPath
	 * @return
	 */
	public static String[] getPathTokens(String fileFullPath) {
		File file = new File(fileFullPath);
		int extIndex = file.getName().lastIndexOf(".");
		String fileName = file.getName().substring(0, extIndex);
		String fileExtension = file.getName().substring(extIndex + 1);
		String[] pathtokens = { file.getParent(), fileName, fileExtension };

		return pathtokens;
	}

	public static boolean createDirsRecursively(String dirPath) {
		File outPathDir = new File(dirPath);
		if (!outPathDir.exists()) {
			return outPathDir.mkdirs();
		}
		return false;
	}

	public static String getActualOutputDirPath(String outputDirPath, String origFilePath, boolean isIncludeFileName) {
		// If out path not provided then consider the input file path to it.
		String outputDirPath1 = outputDirPath;
		if (outputDirPath1 == null) {
			String[] pathTokens = CommonUtil.getPathTokens(origFilePath);
			if (isIncludeFileName) {
				outputDirPath1 = pathTokens[CommonUtil.PATH_TOKEN_PARENT] + "/"
						+ pathTokens[CommonUtil.PATH_TOKEN_FILE_NAME] + '.' + pathTokens[CommonUtil.PATH_TOKEN_FILE_EXT]
						+ "_files";
			} else {
				outputDirPath1 = pathTokens[CommonUtil.PATH_TOKEN_PARENT];
			}
		}
		return outputDirPath1;
	}

	/**
	 * This method returns the result of a CLI call by simply printing the result to
	 * the console
	 * 
	 * @param result
	 */
	public static void returnResultToCaller(Object obj) {
		if (obj instanceof List) {
			List<?> list = (ArrayList<?>) obj;
			for (Object listItem : list) {
				System.out.println(listItem);
			}
			return;
		}
		System.out.println(obj);
	}

	/**
	 * This method converts a JSON structure to a pretty JSON string
	 * 
	 * @param jsonStructure
	 * @return
	 */
	public static String getPrettyJson(JsonStructure jsonStructure) {
		Map<String, Boolean> config = new HashMap<String, Boolean>();
		config.put(JsonGenerator.PRETTY_PRINTING, true);

		JsonWriterFactory writerFactory = Json.createWriterFactory(config);
		StringWriter stringWriter = new StringWriter();
		JsonWriter jsonWriter = writerFactory.createWriter(stringWriter);

		if (jsonStructure instanceof JsonArray) {
			jsonWriter.writeArray((JsonArray) jsonStructure);
		} else if (jsonStructure instanceof JsonObject) {
			jsonWriter.writeObject((JsonObject) jsonStructure);
		}
		jsonWriter.close();

		return stringWriter.toString().trim();
	}

	/**
	 * This method calculates the scale factor given dimensions of base document and
	 * another document
	 * 
	 * @param baseWidth
	 * @param baseHeight
	 * @param newWidth
	 * @param newHeight
	 * @return
	 */
	public static float getConversionRatio(float baseWidth, float baseHeight, float newWidth, float newHeight) {
		float conversionRatio = 1;
		if (baseWidth > 0 && baseHeight > 0) {
			conversionRatio = Math.min(newWidth / baseWidth, newHeight / baseHeight);
		}
		return conversionRatio;
	}

	/**
	 * This method rounds off a given value to the specified decimal places
	 * @param value
	 * @param places
	 * @return
	 */
	public static float roundOff(double value, int places) {
		BigDecimal bd = new BigDecimal(Double.toString(value));
		bd = bd.setScale(places, RoundingMode.HALF_UP);
	    return bd.floatValue();
	}
	
	/**
	 * This method calculates page numbers given the requirement in range or CSV.
	 * @param pages
	 * @param maxPages
	 * @return
	 */
	public static List<Integer> getPageNumbers(String pages, int maxPages) {
		List<Integer> pageNumList = new ArrayList<>();

		// If page numbers were not specified by caller, then populate with full list of
		// page numbers
		if (pages.equalsIgnoreCase(Constants.DEFAULT_PAGES)) {
			pageNumList = IntStream.rangeClosed(1, maxPages).boxed().collect(Collectors.toList());
		} else {
			for (String token : Arrays.asList(pages.split(","))) {
				if (token.contains(Constants.RANGE_SEPARATOR)) {
					String subTokens[] = token.split(Constants.RANGE_SEPARATOR);
					int from = 1;
					int to = maxPages;
					if (subTokens[0].length() > 0) {
						from = Integer.valueOf(subTokens[0]);
					}
					// If second sub-token exists and is not empty
					if (subTokens.length > 1 && subTokens[1].length() > 0) {
						to = Integer.valueOf(subTokens[1]);
					}
					pageNumList.addAll(IntStream.rangeClosed(from, to).boxed().collect(Collectors.toList()));
				} else {
					pageNumList.add(Integer.valueOf(token));
				}
			}
		}

		// Remove duplicates
		pageNumList = pageNumList.stream().distinct().collect(Collectors.toList());
		// Remove values greater than max page num
		pageNumList.removeIf(x -> x > maxPages);
		return pageNumList;
	}
}
