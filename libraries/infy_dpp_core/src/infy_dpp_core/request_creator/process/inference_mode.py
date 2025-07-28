# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import infy_dpp_sdk
import infy_fs_utils
from ...common.file_util import FileUtil
from ...request_creator.process.query_builder import QueryBuilder


class InferenceMode:
    def __init__(self, PROCESSEOR_CONTEXT_DATA_NAME):
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager().get_fs_logging_handler(
            infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)
        self.PROCESSEOR_CONTEXT_DATA_NAME = PROCESSEOR_CONTEXT_DATA_NAME

    def get_inference_mode_dir_created(self, input_doc, from_data_file_config):
        def __get_temp_file_path(work_file_path):
            local_file_path = f'{self.__app_config["CONTAINER"]["APP_DIR_TEMP_PATH"]}/{work_file_path}'
            FileUtil.create_dirs_if_absent(os.path.dirname(local_file_path))
            with self.__file_sys_handler.get_file_object(work_file_path) as f:
                with open(local_file_path, "wb") as output:
                    output.write(f.read())
            return local_file_path

        response_list = []
        work_root_path = from_data_file_config.get('work_root_path')
        documend_id = FileUtil.get_uuid()
        doc_dir_name = f"D-{documend_id}"
        self.__logger.info("Processing file %s", input_doc)

        # ---- Create file paths -----
        work_file = FileUtil.safe_file_path(
            f"{work_root_path}/{doc_dir_name}/{os.path.basename(input_doc)}")
        supporting_files = FileUtil.safe_file_path(
            f"{work_file}_files/")
        # storage_uri = FileUtil.safe_file_path(self.__file_sys_handler.get_storage_uri().split("://")[1])
        storage_uri = FileUtil.safe_file_path(
            self.__file_sys_handler.get_storage_root_uri().split("://")[1])
        temp_input_doc = FileUtil.safe_file_path(
            input_doc).replace(storage_uri, '')

        # ---- Create supporting files folder -----
        self.__file_sys_handler.create_folders(
            supporting_files)

        # ---- Copy input file to work folder -----
        self.__file_sys_handler.copy_file(
            temp_input_doc, work_file)

        from_files_full_path = __get_temp_file_path(
            work_file)
        out_file_full_path = f'{from_files_full_path}_files'
        _, extension = os.path.splitext(
            from_files_full_path)
        question_config_request_path = ""
        if not os.path.exists(out_file_full_path):
            os.makedirs(out_file_full_path)
        if extension == ".xlsx":
            request_creator_inference_obj = QueryBuilder(
                from_data_file_config)
            question_config_request_path = request_creator_inference_obj.get_excel_content(
                from_files_full_path, out_file_full_path)
        # ---- Create response data -----
        metadata = infy_dpp_sdk.data.MetaData(
            standard_data=infy_dpp_sdk.data.StandardData(
                filepath=infy_dpp_sdk.data.ValueData(value=input_doc)))
        document_data = infy_dpp_sdk.data.DocumentData(
            document_id=documend_id, metadata=metadata)
        if question_config_request_path:
            context_data = {
                self.PROCESSEOR_CONTEXT_DATA_NAME: {
                    "work_file_path": work_file,
                    "question_config_request_file": question_config_request_path
                }
            }

        message_data = infy_dpp_sdk.data.MessageData()
        response_data = infy_dpp_sdk.data.ProcessorResponseData(
            document_data=document_data, context_data=context_data)
        response_list.append(response_data)
        return response_list
