# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import infy_dpp_sdk
import infy_fs_utils
from ...common.file_util import FileUtil


class ReportMode:
    def __init__(self, PROCESSEOR_CONTEXT_DATA_NAME):
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager().get_fs_logging_handler(
            infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)
        self.PROCESSEOR_CONTEXT_DATA_NAME = PROCESSEOR_CONTEXT_DATA_NAME

    def get_report_mode_dir_created(self, input_files, work_root_path):
        response_list = []
        documend_id = FileUtil.get_uuid()
        doc_dir_name = f"D-{documend_id}"
        # ---- Create file paths -----
        work_folder = FileUtil.safe_file_path(
            f"{work_root_path}/{doc_dir_name}")
        supporting_files = FileUtil.safe_file_path(
            f"{work_folder}/reports/")
        # ---- Create supporting files folder -----
        self.__file_sys_handler.create_folders(supporting_files)

        for input_doc in input_files:
            # ---- Create file paths -----
            work_file = FileUtil.safe_file_path(
                f"{work_root_path}/{doc_dir_name}/{os.path.basename(input_doc)}")
            # storage_uri = FileUtil.safe_file_path(self.__file_sys_handler.get_storage_uri().split("://")[1])
            storage_uri = FileUtil.safe_file_path(
                self.__file_sys_handler.get_storage_root_uri().split("://")[1])
            temp_input_doc = FileUtil.safe_file_path(
                input_doc).replace(storage_uri, '')
            # ---- Copy input file to work folder -----
            self.__file_sys_handler.copy_file(
                temp_input_doc, work_file)

        # ---- Create response data -----
        metadata = infy_dpp_sdk.data.MetaData(
            standard_data=infy_dpp_sdk.data.StandardData(
                filepath=infy_dpp_sdk.data.ValueData(value=input_doc)))
        document_data = infy_dpp_sdk.data.DocumentData(
            document_id=documend_id, metadata=metadata)
        context_data = {
            self.PROCESSEOR_CONTEXT_DATA_NAME: {
                "work_file_path": work_folder
            }
        }
        message_data = infy_dpp_sdk.data.MessageData()
        response_data = infy_dpp_sdk.data.ProcessorResponseData(
            document_data=document_data, context_data=context_data)
        response_list.append(response_data)

        return response_list
