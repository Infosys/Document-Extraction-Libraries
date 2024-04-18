/** =============================================================================================================== *
 * Copyright 2024 Infosys Ltd.                                                                                    *
 * Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at    *
 * http://www.apache.org/licenses/ 
 * ================================================================================================================ *
 */

package com.infosys.ainauto.ocrengine;

import java.io.File;
import java.util.LinkedHashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.infosys.ainauto.ocrengine.common.CommonUtil;
import com.infosys.ainauto.ocrengine.common.Constants;
import com.infosys.ainauto.ocrengine.model.SwitchData;
import com.infosys.ainauto.ocrengine.process.TesseractHandler;

public class Ocr {

    // Create logs folder before instantiating logger object
    static {
        new File("./logs").mkdirs();
    }

    private static final Logger LOGGER = LoggerFactory.getLogger(Ocr.class);
    private static String HELP_TEXT = "";

    static {
        HELP_TEXT = new String(CommonUtil.readResourceFile(("README.TXT")));
    }

    private enum EnumSwitchName {
        FROM_FILE("fromfile"), MODEL_DIR("modeldir"), TO_DIR("todir"), LANGUAGE("lang"),
        OCR_FORMAT("ocrformat");

        private String propertyValue;

        private EnumSwitchName(String s) {
            propertyValue = s;
        }

        public String getValue() {
            return propertyValue;
        }
    }

    public static void main(String[] args) {
        try {
            boolean isShowHelpText = false;
            if (args.length > 0) {
                Map<String, String> switchMap = getSwitchMap(args);
                validateSwitches(switchMap);
                SwitchData switchData = getSwitchData(switchMap);
                TesseractHandler.extractText(switchData);
            } else {
                isShowHelpText = true;
            }
            if (isShowHelpText) {
                CommonUtil.returnResultToCaller(HELP_TEXT);
            }
        } catch (Exception ex) {
            LOGGER.error("Error occurred in main method.", ex);
            CommonUtil.returnResultToCaller("Error occurred in main method. Please refer to log file for details.");
        }
    }

    private static Map<String, String> getSwitchMap(String[] tokens) {
        Map<String, String> switchMap = new LinkedHashMap<String, String>();
        for (int i = 0; i < tokens.length; i++) {
            if (tokens[i].startsWith(Constants.SWITCH_PREFIX)) {
                String switchName = tokens[i].substring(Constants.SWITCH_PREFIX.length());
                String switchValue = "";
                if (((i + 1) < tokens.length) && !tokens[i + 1].startsWith(Constants.SWITCH_PREFIX)) {
                    switchValue = tokens[i + 1];
                    i++;
                }
                switchMap.put(switchName, switchValue);
            }
        }
        return switchMap;
    }

    private static void validateSwitches(Map<String, String> switchMap) throws Exception {
        for (Map.Entry<String, String> entry : switchMap.entrySet()) {
            if (entry.getValue() == "") {
                throw new Exception("Value not provided for --" + entry.getKey());
            }
        }
    }

    private static SwitchData getSwitchData(Map<String, String> switchMap) {
        SwitchData switchData = new SwitchData();

        switchData.setFromFile(switchMap.getOrDefault(EnumSwitchName.FROM_FILE.getValue(), ""));
        switchData.setModelDirPath(switchMap.getOrDefault(EnumSwitchName.MODEL_DIR.getValue(), ""));
        switchData.setLanguage(switchMap.getOrDefault(EnumSwitchName.LANGUAGE.getValue(), Constants.LANGUAGE_ENG));
        switchData.setToDir(switchMap.getOrDefault(EnumSwitchName.TO_DIR.getValue(), null));
        switchData.setOcrFormat(switchMap.getOrDefault(EnumSwitchName.OCR_FORMAT.getValue(), "txt"));

        return switchData;
    }
}
