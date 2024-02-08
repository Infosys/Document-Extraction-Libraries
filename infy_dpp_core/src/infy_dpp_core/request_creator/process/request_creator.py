# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
from typing import List
import infy_dpp_sdk
from infy_dpp_sdk.data import *
from infy_dpp_sdk.data.document_data import DocumentData
from infy_dpp_sdk.data.processor_response_data import ProcessorResponseData
from infy_dpp_core.common.file_system_manager import FileSystemManager


from infy_dpp_core.common.file_util import FileUtil
from infy_dpp_core.common.logger_factory import LoggerFactory

PROCESSEOR_CONTEXT_DATA_NAME = "request_creator"


class RequestCreator(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__logger = LoggerFactory().get_logger()
        self.__file_sys_handler = FileSystemManager().get_file_system_handler()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        response_list = self.__get_document_data(config_data)
        return response_list[0]

    def do_execute_batch(self, document_data_list: List[DocumentData], context_data_list: List[dict], config_data: dict) -> List[ProcessorResponseData]:
        """For do_execute_batch refer to the IProcessor interface. 
        Here overriding exclusively for request creator alone."""
        return self.__get_document_data(config_data)

    def __get_document_data(self, config_data: dict):
        response_list = []
        processor_config_data = config_data.get('RequestCreator', {})
        work_root_path = processor_config_data.get('work_root_path')
        queue_data = processor_config_data.get('queue')
        batch_size = processor_config_data.get('batch_size')

        for input_doc in self.__read_files(config_data, batch_size):
            documend_id = FileUtil.get_uuid()
            doc_dir_name = f"D-{documend_id}"
            self.__logger.info(f"Processing file {input_doc}")
            # ---- Check if file is already processed -----
            should_start_process = True
            if queue_data.get('enabled'):
                should_start_process = FileUtil.generate_file_lock(input_doc, queue_data.get('queue_root_path'),
                                                                   self.__file_sys_handler)
            if not should_start_process:
                continue
            # ---- Create file paths -----
            work_file = FileUtil.safe_file_path(
                f"{work_root_path}/{doc_dir_name}/{os.path.basename(input_doc)}")
            supporting_files = FileUtil.safe_file_path(f"{work_file}_files/")
            storage_uri = FileUtil.safe_file_path(
                self.__file_sys_handler.get_storage_uri().split("://")[1])
            temp_input_doc = FileUtil.safe_file_path(
                input_doc).replace(storage_uri, '')

            # ---- Create supporting files folder -----
            self.__file_sys_handler.create_folders(supporting_files)

            # ---- Copy input file to work folder -----
            self.__file_sys_handler.copy_file(temp_input_doc, work_file)

            # ---- Create response data -----
            metadata = infy_dpp_sdk.data.MetaData(
                standard_data=infy_dpp_sdk.data.StandardData(
                    filepath=infy_dpp_sdk.data.ValueData(value=input_doc)))
            document_data = infy_dpp_sdk.data.DocumentData(
                document_id=documend_id, metadata=metadata)
            context_data = {
                PROCESSEOR_CONTEXT_DATA_NAME: {
                    "work_file_path": work_file
                }
            }
            response_data = infy_dpp_sdk.data.ProcessorResponseData(
                document_data=document_data, context_data=context_data)
            response_list.append(response_data)

        if len(response_list) < 1:
            response_list.append(infy_dpp_sdk.data.ProcessorResponseData(
                document_data=infy_dpp_sdk.data.DocumentData(),
                context_data={}
            ))
        return response_list

    def __read_files(self, config_data: dict, batch_size: int) -> List[str]:
        req_config_data = config_data.get('RequestCreator', {})
        read_path = req_config_data.get('read_path')
        # TODO: [added by raj] add logic to include/exclude files
        found_files = self.__file_sys_handler.list_files1(read_path)
        if len(found_files) > 0:
            found_files = found_files[0:batch_size]
        else:
            self.__logger.info(f"No files found in {read_path}")
        return found_files
