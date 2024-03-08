# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
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


from infy_dpp_core.common.file_util import FileUtil

PROCESSEOR_CONTEXT_DATA_NAME = "request_closer"


class RequestCloser(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__logger = self.get_logger()
        self.__file_sys_handler = self.get_fs_handler()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        response_data = infy_dpp_sdk.data.ProcessorResponseData(
            document_data=document_data, context_data=context_data)
        doc_id = document_data.document_id
        if not doc_id:
            return response_data
        processor_config_data = config_data.get('RequestCloser', {})
        work_root_path = processor_config_data.get('work_root_path')
        request_read_path = processor_config_data.get(
            'from_request_file').get('read_path')
        request_save_path = processor_config_data.get(
            'from_request_file').get('save_path')
        group_request_file = context_data.get(
            'request_creator').get('group_request_file')
        work_file_path = context_data.get(
            'request_creator').get('work_file_path')
        work_folder_path=os.path.dirname(work_file_path)
        request_file_path = f'{request_read_path}/{group_request_file}'
        group_id = group_request_file.replace('_group_request.json', '')
        sub_folder = f'{work_root_path}/queue/{group_id}'
        # ------ Create output document directory --------------
        output_path = FileUtil.safe_file_path(
            f"{processor_config_data.get('output_root_path')}/D-{doc_id}")
        self.__file_sys_handler.create_folders(output_path)

        # ------ Move original input file to output location ---------
        original_file = document_data.metadata.standard_data.filepath.value
        # storage_uri = FileUtil.safe_file_path(self.__file_sys_handler.get_storage_uri().split("://")[1])
        storage_uri = FileUtil.safe_file_path(
            self.__file_sys_handler.get_storage_root_uri().split("://")[1])
        temp_original_file = FileUtil.safe_file_path(
            original_file).replace(storage_uri, '')
        data_file_output_path = processor_config_data.get(
            'data_file').get('output_root_path')
        if data_file_output_path:
            self.__file_sys_handler.move_file(temp_original_file, output_path)

        # ------ Save document data in output location ------
        document_data_file = FileUtil.safe_file_path(
            f"{output_path}/document_data.json")
        self.__file_sys_handler.write_file(
            document_data_file, document_data.json(indent=4))

        # ----- Unlock queue file -----
        FileUtil.unlock_file(original_file, sub_folder,
                             self.__file_sys_handler)

        # ------ Move request file to complete location -------
        if self.__file_sys_handler.exists(sub_folder):
            total_hash_files = self.__file_sys_handler.list_files(sub_folder)
            if len(total_hash_files) == 0:
                self.__file_sys_handler.create_folders(request_save_path)
                self.__file_sys_handler.move_file(
                    request_file_path, request_save_path)
                FileUtil.delete_empty_dir(f'{storage_uri}/{sub_folder}')
        else:
            self.__file_sys_handler.create_folders(request_save_path)
            self.__file_sys_handler.move_file(
                request_file_path, request_save_path)
        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            "output_folder_path": output_path,
            "work_folder_path":work_folder_path
        }
        response_data.document_data = document_data
        response_data.context_data = context_data
        return response_data
