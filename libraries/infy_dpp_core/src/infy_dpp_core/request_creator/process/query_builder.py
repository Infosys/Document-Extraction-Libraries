# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import pandas as pd
import infy_dpp_sdk
import infy_fs_utils

from infy_dpp_core.common.file_util import FileUtil


class QueryBuilder:
    def __init__(self, from_data_file_config):
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager().get_fs_logging_handler(
            infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)

        self._from_data_file_config = from_data_file_config

    def get_excel_content(self, from_files_full_path, out_file_full_path):
        query_list = []
        try:
            # Load the Excel file into a DataFrame
            excel_data = pd.read_excel(from_files_full_path)
            total_question = len(excel_data.Question)
            # Convert the DataFrame to a JSON object
            # json_data = data.to_json(orient='records')
            if excel_data['Q_No'].duplicated().any():
                self.__logger.error(
                    f"Duplicate question numbers found in file {from_files_full_path}")
                return []
        except Exception as e:
            self.__logger.error(
                f"Error reading file {from_files_full_path} - {str(e)}")
            return
        for i in range(total_question):
            # future changes required for filter_metadata
            # to-do
            filter_metadata = {
                "doc_name": excel_data.at[i, 'Document_Name'] if not pd.isna(excel_data.at[i, 'Document_Name']) else ""}
            query = {
                # "attribute_key": excel_data['Q_No'][i],
                "attribute_key": "query1",
                "question": excel_data['Question'][i],
                "top_k": self._from_data_file_config.get("top_k"),
                "pre_filter_fetch_k": self._from_data_file_config.get("pre_filter_fetch_k"),
                "filter_metadata": filter_metadata
            }
            query_list.append(query)

        question_config_request_path = os.path.join(
            out_file_full_path, "question_config_request.json")
        FileUtil.save_to_json(
            question_config_request_path, query_list)

        # upload the json file to the work location
        server_file_dir = os.path.dirname(question_config_request_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), ''))
        local_dir = os.path.dirname(question_config_request_path)
        self._upload_data(f'{local_dir}', f'{server_file_dir}')

        # xlsx_json_data_path = xlsx_json_data_path.replace('\\', '/').replace('//', '/').replace(
        #     self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')
        question_config_request_path = question_config_request_path.replace('\\', '/').replace('//', '/').replace(
            self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"].replace('\\', '/').replace('//', '/'), '')

        return question_config_request_path

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
