# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import infy_dpp_sdk
import infy_fs_utils
from ...common.file_util import FileUtil


class ContentEvaluationMode:
    def __init__(self, PROCESSEOR_CONTEXT_DATA_NAME):
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager().get_fs_logging_handler(
            infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)
        # self.__file_sys_handler = self.get_fs_handler()
        # self.__app_config = self.get_app_config()
        # self.__logger = self.get_logger()
        self.PROCESSEOR_CONTEXT_DATA_NAME = PROCESSEOR_CONTEXT_DATA_NAME

        # self._from_data_file_config = from_data_file_config

    def get_content_eval_mode_dir_created(self, input_files, work_root_path):
        response_list = []
        if input_files and work_root_path:
            document_id = FileUtil.get_uuid()
            doc_dir_name = f"D-{document_id}"
            # ---- Create file paths -----
            work_folder_root_path = FileUtil.safe_file_path(
                f"{work_root_path}/{doc_dir_name}")
            self.__file_sys_handler.create_folders(work_folder_root_path)

            metric_folder_path = FileUtil.safe_file_path(
                f"{work_root_path}/{doc_dir_name}/metric")
            self.__file_sys_handler.create_folders(metric_folder_path)

            result_folder_path = FileUtil.safe_file_path(
                f"{work_folder_root_path}/result")
            self.__file_sys_handler.create_folders(result_folder_path)

            report_folder_path = FileUtil.safe_file_path(
                f"{work_folder_root_path}/report")
            self.__file_sys_handler.create_folders(report_folder_path)

            for input_doc in input_files:
                self.__logger.info(f"Processing file {input_doc}")
                _, extension = os.path.splitext(input_doc)
                if extension == ".xlsx":
                    # ---- Create file paths -----
                    work_file = FileUtil.safe_file_path(
                        f"{work_folder_root_path}/{os.path.basename(input_doc)}")
                    supporting_files_folder = FileUtil.safe_file_path(
                        f"{work_file}_files/")
                    storage_uri = FileUtil.safe_file_path(
                        self.__file_sys_handler.get_storage_root_uri().split("://")[1])
                    temp_input_doc = FileUtil.safe_file_path(
                        input_doc).replace(storage_uri, '')
                    # ---- Create supporting files folder -----
                    self.__file_sys_handler.create_folders(
                        supporting_files_folder)
                    # ---- Copy input file to work folder -----
                    self.__file_sys_handler.copy_file(
                        temp_input_doc, work_file)
                # ---- Create response data -----
            metadata = infy_dpp_sdk.data.MetaData(
                standard_data=infy_dpp_sdk.data.StandardData(
                    filepath=infy_dpp_sdk.data.ValueData(value=input_doc)))
            document_data = infy_dpp_sdk.data.DocumentData(
                document_id=document_id, metadata=metadata)
            context_data = {
                self.PROCESSEOR_CONTEXT_DATA_NAME: {
                    "work_file_path": work_file,
                    "metric_folder_path": metric_folder_path,
                    "result_folder_path": result_folder_path,
                    "report_folder_path": report_folder_path
                }
            }
            message_data = infy_dpp_sdk.data.MessageData()
            response_data = infy_dpp_sdk.data.ProcessorResponseData(
                document_data=document_data, context_data=context_data)
            response_list.append(response_data)

        return response_list
