# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                  #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import os
import json
import infy_dpp_sdk
from infy_dpp_sdk.data import *
from infy_dpp_segmentation.common.file_util import FileUtil
import infy_fs_utils

PROCESSEOR_CONTEXT_DATA_NAME = "save_chunk_data"


class SaveChunkDataParser(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        # self.__logger = LoggerFactory().get_logger()
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
        ).get_fs_logging_handler(infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        self.__file_sys_handler = self.get_fs_handler()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        processor_response_data = ProcessorResponseData()
        context_data = context_data if context_data else {}
        processor_config_data = config_data.get('SaveChunkDataParser', {})
        processor_data = {
            "document_data": document_data.json(), "context_data": context_data}
        # raw_data_dict = document_data.raw_data.dict()
        # segment_data_list = raw_data_dict.get('segment_data')
        chunked_file_root_path = processor_config_data.get(
            'chunked_files_root_path', '')
        bucket_name = chunked_file_root_path.split('/', 1)[0]
        server_folder = chunked_file_root_path.split('/', 1)[1]
        document_id = document_data.document_id
        if context_data.get('chunk_data_parser'):
            chunked_data_dict = context_data['chunk_data_parser']['page_segment_data']
            write_path = f"{chunked_file_root_path}/{document_id}/chunks"
            self.__file_sys_handler.create_folders(write_path)
            chunked_file_path_list = self._write_data(
                write_path, chunked_data_dict, 'txt')
            meta_data_dict = context_data['chunk_data_parser']['meta_data']
            chunked_file_meta_data_path_list = self._write_data(
                write_path, meta_data_dict, 'json')
        else:
            print('Please run create chunk processor')
            chunked_file_path_list = []

        # replacing the path as server path in context data
        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {'chunked_data_list': chunked_file_path_list,
                                                      "chunked_file_meta_data_list": chunked_file_meta_data_path_list}

        # Populate response data
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data
        return processor_response_data

    def _write_data(self, file_path, data, file_type):
        write_path_list = []
        for k, v in data.items():
            full_file_path = f'{file_path}/{k}.{file_type}'

            if file_type == 'json':
                content = json.dumps(v, indent=4)
            else:
                content = v
            try:
                self.__file_sys_handler.write_file(full_file_path, content)
                self.__logger.info(
                    f'File {full_file_path} written successfully')
                write_path_list.append(full_file_path)
            except Exception as e:
                self.__logger.error(
                    f'Error while writing data to {file_path} : {e}')
                raise e
        return write_path_list
