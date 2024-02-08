# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import os
from typing import List
import infy_dpp_sdk
from infy_dpp_sdk.data import *
from infy_dpp_sdk.data.document_data import DocumentData
from infy_dpp_sdk.data.processor_response_data import ProcessorResponseData
from infy_dpp_core.common.file_system_manager import FileSystemManager


from infy_dpp_core.common.file_util import FileUtil
from infy_dpp_core.common.logger_factory import LoggerFactory

PROCESSEOR_CONTEXT_DATA_NAME = "request_closer"


class RequestCloser(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__logger = LoggerFactory().get_logger()
        self.__file_sys_handler = FileSystemManager().get_file_system_handler()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        response_data = infy_dpp_sdk.data.ProcessorResponseData(
            document_data=document_data, context_data=context_data)
        doc_id = document_data.document_id
        if not doc_id:
            return response_data
        processor_config_data = config_data.get('RequestCloser', {})

        # ------ Create output document directory --------------
        output_path = FileUtil.safe_file_path(
            f"{processor_config_data.get('output_root_path')}/D-{doc_id}")
        self.__file_sys_handler.create_folders(output_path)

        # ------ Move original input file to output location ---------
        original_file = document_data.metadata.standard_data.filepath.value
        storage_uri = FileUtil.safe_file_path(
            self.__file_sys_handler.get_storage_uri().split("://")[1])
        temp_original_file = FileUtil.safe_file_path(
            original_file).replace(storage_uri, '')
        self.__file_sys_handler.move_file(temp_original_file, output_path)

        # ------ Save document data in output location ------
        document_data_file = FileUtil.safe_file_path(
            f"{output_path}/document_data.json")
        self.__file_sys_handler.write_file(
            document_data_file, document_data.json(indent=4))

        # ----- Unlock queue file -----
        queue_data = processor_config_data.get('queue')
        if queue_data.get('enabled'):
            FileUtil.unlock_file(original_file, queue_data.get(
                'queue_root_path'), self.__file_sys_handler)

        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            "output_file_path": output_path
        }
        response_data.document_data = document_data
        response_data.context_data = context_data
        return response_data
