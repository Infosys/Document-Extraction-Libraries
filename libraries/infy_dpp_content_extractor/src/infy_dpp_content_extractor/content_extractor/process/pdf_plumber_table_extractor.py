# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
from infy_dpp_content_extractor.content_extractor.service import PdfPlumberService
from infy_dpp_content_extractor.common.file_util import FileUtil


class PdfPlumberTableExtractor:
    def __init__(self, file_sys_handler, logger, app_config, text_provider_dict):
        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = file_sys_handler
        self.__text_provider_dict = text_provider_dict

    def get_tables_content(self, from_files_full_path, out_file_full_path) -> list:
        pdf_plumber_service_obj = PdfPlumberService(
            self.__logger,self.__app_config,self.__file_sys_handler, self.__text_provider_dict)
        tables_content_file_path = pdf_plumber_service_obj.get_tables_content(
            from_files_full_path, out_file_full_path)

        tables_content = FileUtil.load_json(tables_content_file_path)
        all_tables_empty = True
        # Iterate over each page in tables_content
        for page in tables_content:
            # Check if all tables are empty
            if any(page['tables']):
                all_tables_empty = False
                break
        if all_tables_empty:
            FileUtil.delete_file(tables_content_file_path)
            return ""

        # upload the json file to the work location
        server_file_dir = os.path.dirname(tables_content_file_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
        local_dir = os.path.dirname(tables_content_file_path)
        self._upload_data(f'{local_dir}', f'{server_file_dir}')

        table_content_file_path = tables_content_file_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')

        return table_content_file_path

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
