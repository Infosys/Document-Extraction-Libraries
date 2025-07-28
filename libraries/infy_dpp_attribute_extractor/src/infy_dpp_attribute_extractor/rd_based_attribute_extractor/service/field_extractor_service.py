# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import infy_dpp_sdk
import infy_fs_utils
from infy_field_extractor import text_extractor
from infy_field_extractor.providers.ocr_data_service_provider import OcrDataServiceProvider
from infy_field_extractor.providers.nativepdf_data_service_provider import NativePdfDataServiceProvider
from infy_dpp_attribute_extractor.common import FileUtil


class FieldExtractorService:
    def __init__(self, out_file_full_path):
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
        ).get_fs_logging_handler(infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.temp_path = out_file_full_path

    def call_text_extractor(self, img_path, label, bbox, ocr_parser_obj, scaling_factor,
                            page_no=None, provide_name='ocrTextParser'):
        field_list = [
            {
                "field_key": [label],
                "field_key_match": {"method": "normal", "similarityScore": 1},
                "field_value_bbox": bbox,
                "field_value_pos": "left"
            }
        ]
        config_params_dict = {
            'field_value_pos': "right",
            "page": page_no if page_no else {},
            "eliminate_list": [],
            "scaling_factor": scaling_factor,
            "within_bbox": []
        }

        output, file_data_list = None, []
        try:
            if provide_name == 'ocrTextParser':
                provider = OcrDataServiceProvider(
                    ocr_parser_obj, logger=self.__logger)
            if provide_name == 'nativePdfParser':
                provider = NativePdfDataServiceProvider()
                file_data_list = [{
                    # 'path': extract_props_obj.original_file,
                    'pages': [page_no]
                }]

            temp_folder_path = FileUtil.create_dirs_if_absent(
                f"{self.temp_path}/text_extractor")
            txt_extractor_obj = text_extractor.TextExtractor(
                provider, provider, temp_folder_path, self.__logger)

            output = txt_extractor_obj.extract_custom_fields(
                image_path=img_path,
                text_field_data_list=field_list,
                config_params_dict=config_params_dict,
                file_data_list=file_data_list
            )

            server_file_dir = os.path.dirname(temp_folder_path.replace('\\', '/').replace('//', '/').replace(
                self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
            local_dir = os.path.dirname(temp_folder_path)
            self._upload_data(f'{local_dir}', f'{server_file_dir}')
        except Exception as e:
            self.__logger.error(e)
        input_ocr = {"ocr_parser_object": f"{type(ocr_parser_obj)}",
                     "text_field_data_list": field_list,
                     "config_params_dict": config_params_dict,
                     "scaling_factor": scaling_factor,
                     "technique": provide_name}

        return {"input": input_ocr, "output": output}

    def _upload_data(self, local_file_path, server_file_path):
        try:
            self.__file_sys_handler.put_folder(
                local_file_path, server_file_path)
            self.__logger.info(
                f'Folder {local_file_path} uploaded successfully')
        except Exception as e:
            self.__logger.error(
                f'Error while uploading data to {server_file_path} : {e}')
            raise e
