# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import infy_dpp_sdk
import infy_fs_utils
import infy_table_extractor as ite

LINE_DETECT_RGB = ite.interface.LineDetectionMethod.RGB_LINE_DETECT
LINE_DETECT_OPENCV = ite.interface.LineDetectionMethod.OPENCV_LINE_DETECT


class InfyTableExtractorService:

    def __init__(self, text_provider_dict, out_file_full_path, line_detection_method=None):
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager().get_fs_logging_handler(
            infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()

        provider = ""
        if text_provider_dict.get('provider_name') == 'tesseract_ocr_provider':
            TESSERACT_PATH = text_provider_dict.get(
                'properties').get('tesseract_path', '')
            provider = ite.bordered_table_extractor.providers.TesseractDataServiceProvider(
                TESSERACT_PATH)

        if text_provider_dict.get('provider_name') == 'infy_ocr_engine_provider':
            INFY_OCR_ENGINE_HOME = text_provider_dict.get(
                'properties').get('ocr_engine_exe_dir_path', '')
            MODEL_DIR_PATH = text_provider_dict.get(
                'properties').get('ocr_engine_model_dir_path', '')
            provider = ite.bordered_table_extractor.providers.InfyOcrEngineDataServiceProvider(
                INFY_OCR_ENGINE_HOME, MODEL_DIR_PATH)

        line_detect = LINE_DETECT_RGB
        if line_detection_method == 'OPENCV_LINE_DETECT':
            line_detect = LINE_DETECT_OPENCV
        self.config_param_dict = {
            'col_header': {
                'use_first_row': True,
                'values': []
            },
            'line_detection_method': [line_detect]
        }
        self.table_extractor_object = ite.bordered_table_extractor.BorderedTableExtractor(
            provider, provider, out_file_full_path, self.__logger, True)

    def extract_table_content(self, img_file_path, table_bbox) -> list:

        result = self.table_extractor_object.extract_all_fields(
            img_file_path, within_bbox=table_bbox, config_param_dict=self.config_param_dict)

        return result
