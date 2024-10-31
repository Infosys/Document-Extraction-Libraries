# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                  #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import infy_dpp_sdk
import infy_fs_utils
from infy_dpp_content_extractor.common.file_util import FileUtil
from infy_dpp_content_extractor.content_extractor.service import YoloxTableDetectorService
from infy_dpp_content_extractor.content_extractor.service import InfyTableExtractorService


class YoloxTableExtactor():
    def __init__(self, model_provider_dict, text_provider_dict, line_detection_method=None):
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager().get_fs_logging_handler(
            infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)

        self.__model_path = model_provider_dict.get(
            'properties').get('yolox_model_home', '')
        if self.__model_path == '':
            raise Exception(
                'YOLOX model path is not configured in the config file')
        self.__model_name = model_provider_dict.get(
            'properties').get('model_name', '')
        if self.__model_name == '':
            raise Exception(
                'YOLOX model name is not configured in the config file')
        self.text_provider_dict = text_provider_dict
        self.line_detection_method = line_detection_method

    def get_tables_content(self, images_file_path_list, from_files_full_path, out_file_full_path, table_debug) -> list:
        def __get_temp_file_path(work_file_path):
            local_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{work_file_path}'
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            with self.__file_sys_handler.get_file_object(work_file_path) as f:
                with open(local_file_path, "wb") as output:
                    output.write(f.read())
            return local_file_path

        # Table detection
        file_full_path_list = []
        for image_path in images_file_path_list:
            file_full_path_list.append(__get_temp_file_path(image_path))

        yolox_table_detector_service_obj = YoloxTableDetectorService(
            self.__model_path, self.__model_name)
        page_tables_bbox_list = yolox_table_detector_service_obj.detect_table(
            file_full_path_list, table_debug)
        if not page_tables_bbox_list:
            self.__logger.info("No tables detected in the input images")
            return [], []
        else:
            self.__logger.debug("Table/s detected in PDF file by YOLOX model")

        # Table content extraction
        tables_detected_list = []
        table_detected_file_path_list = []
        results_list = []
        infy_table_extractor_service_obj = InfyTableExtractorService(
            self.text_provider_dict, out_file_full_path, self.line_detection_method)
        for page_tables in page_tables_bbox_list:
            tables_data_list = []
            file_name = page_tables.get("image") + "_yolox.json"
            page_tables['page'] = page_tables.get(
                "image").replace(".jpg", "")
            for image_path in images_file_path_list:
                if page_tables['image'] == os.path.basename(image_path):
                    page_tables['image'] = image_path
                    break
            table_detected_file_path = os.path.join(
                out_file_full_path, file_name)
            tables_detected_list.append(page_tables)
            FileUtil.save_to_json(table_detected_file_path, page_tables)
            table_detected_file_path = table_detected_file_path.replace('\\', '/').replace('//', '/').replace(
                self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')
            table_detected_file_path_list.append(table_detected_file_path)

            table_number = 1
            for token in page_tables.get('tokens'):
                table_bbox = []
                table_bbox.append(token['bbox'][0])
                table_bbox.append(token['bbox'][1])
                table_bbox.append(token['bbox'][2] - token['bbox'][0])
                table_bbox.append(token['bbox'][3] - token['bbox'][1])
                img_file_path = __get_temp_file_path(page_tables.get('image'))
                result = infy_table_extractor_service_obj.extract_table_content(
                    img_file_path, table_bbox)
                table_data = {
                    "table_id": f"p{page_tables.get('page')}_tb{table_number}",
                    "bbox":  token['bbox'],
                    "data": result['fields'][0].get('table_value'),
                    "debug_path": result['fields'][0].get('debug_path')
                }
                table_number += 1
                tables_data_list.append(table_data)

            if tables_data_list:
                table_dict = {
                    "page_number": int(page_tables.get('page')),
                    "page_width": page_tables.get('width'),
                    "page_height": page_tables.get('height'),
                    "tables": tables_data_list
                }
                results_list.append(table_dict)

        output_file_path = os.path.join(
            out_file_full_path, f"{os.path.basename(from_files_full_path)}_yolox.json")
        FileUtil.save_to_json(output_file_path, tables_detected_list)

        img_yolox_infy_table_extractor_path = os.path.join(
            out_file_full_path, f"{os.path.basename(from_files_full_path)}_img_yolox_infy_table_extractor.json")
        FileUtil.save_to_json(
            img_yolox_infy_table_extractor_path, results_list)

        server_file_dir = os.path.dirname(img_yolox_infy_table_extractor_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
        local_dir = os.path.dirname(img_yolox_infy_table_extractor_path)
        self._upload_data(f'{local_dir}', f'{server_file_dir}')

        table_content_file_path = img_yolox_infy_table_extractor_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')
        return table_content_file_path, table_detected_file_path_list

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
