# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import infy_table_extractor as ite
from infy_object_detector.detector.table_detector import TableDetector
from infy_object_detector.detector.provider.yolox_td_provider import YoloxTdProvider, \
    YoloxTdProviderConfigData, YoloxTdRequestData
from infy_object_detector.structure_recogniser.provider.bordered_table_tsr_provider import BorderedTableTsrProvider, \
    BorderedTableTsrProviderConfigData, BorderedTableTsrProviderRequestData
from infy_object_detector.detector.provider.docling_table_td_tsr_provider import DoclingTableTdTsrProvider, \
    DoclingTableTdTsrProviderConfigData, DoclingTableTdTsrProviderRequestData

LINE_DETECT_RGB = ite.interface.LineDetectionMethod.RGB_LINE_DETECT
LINE_DETECT_OPENCV = ite.interface.LineDetectionMethod.OPENCV_LINE_DETECT


class InfyObjectDetectorService:

    def __init__(self, logger, model_service_url, model_provider_class_name, model_provider_module_name,
                 text_provider_dict, out_file_full_path, line_detection_method=None, is_table_html_view=None):
        self.__logger = logger
        self.__ocr_engine_exe_dir_path = text_provider_dict.get(
            'properties', {}).get('ocr_engine_exe_dir_path', '')
        self.__ocr_engine_model_dir_path = text_provider_dict.get(
            'properties', {}).get('ocr_engine_model_dir_path', '')
        self.__tesseract_path = text_provider_dict.get(
            'properties', {}).get('tesseract_path', '')
        self.__model_name = text_provider_dict.get(
            'properties', {}).get('model_name', '')
        self.__class_name = model_provider_class_name
        self.__module_name = model_provider_module_name
        self.__is_table_html_view = is_table_html_view

        line_detect = LINE_DETECT_RGB
        if line_detection_method == 'OPENCV_LINE_DETECT':
            line_detect = LINE_DETECT_OPENCV
        self.__config_param_dict = {
            'col_header': {
                'use_first_row': True,
                'values': []
            },
            'line_detection_method': [line_detect]
        }

        if self.__class_name == "YoloxTdProvider":
            self.__td = TableDetector(
                YoloxTdProvider(
                    YoloxTdProviderConfigData(
                        model_service_url=model_service_url
                    )
                )
            )
        elif self.__class_name == "DoclingTableTdTsrProvider":
            self.__td = TableDetector(
                DoclingTableTdTsrProvider(
                    DoclingTableTdTsrProviderConfigData(
                        model_service_url=model_service_url,
                        is_table_html_view=self.__is_table_html_view
                    )
                )
            )

        self.__tsr_provider = BorderedTableTsrProvider(
            BorderedTableTsrProviderConfigData(
                ocr_engine_exe_dir_path=self.__ocr_engine_exe_dir_path,
                ocr_engine_model_dir_path=self.__ocr_engine_model_dir_path,
                temp_folder_path=out_file_full_path,
                config_param_dict=self.__config_param_dict,
                model_path=self.__tesseract_path,
                model_name=self.__model_name,
            )
        )

    def detect_table(self, image_file_full_path_list) -> list:
        td_response_list = []
        for image_file_full_path in image_file_full_path_list:
            try:
                if self.__class_name == "YoloxTdProvider":
                    td_response = self.__td.detect_table(
                        YoloxTdRequestData(
                            **{
                                "image_file_path": image_file_full_path
                            }
                        ))
                elif self.__class_name == "DoclingTableTdTsrProvider":
                    td_response = self.__td.detect_table(
                        DoclingTableTdTsrProviderRequestData(
                            **{
                                "image_file_path": image_file_full_path
                            }
                        ))
            except Exception as e:
                print(f"Error occurred while detecting table: {e}")
                self.__logger.error(
                    f"Error occurred while detecting table: {e}")
                continue
            td_response = td_response.dict()
            td_response['image'] = os.path.basename(image_file_full_path)
            td_response_list.append(td_response)
        return td_response_list

    def extract_table_content(self, img_file_path, table_bbox) -> list:

        table_request_data = BorderedTableTsrProviderRequestData(
            image_file_path=img_file_path, bbox=table_bbox)
        response = self.__tsr_provider.extract_table_data(
            table_request_data)

        return response.dict()
