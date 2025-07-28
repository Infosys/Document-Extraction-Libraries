# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import infy_dpp_sdk
import infy_fs_utils
from infy_dpp_sdk.data import *


class ChunkSaver:
    def __init__(self, file_sys_handler, logger, app_config):
        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = file_sys_handler

    def save_chunk_data(self, document_id, save_chunk_config, page_segment_data_dict, meta_data_dict):
        if page_segment_data_dict:
            chunked_data_dict = page_segment_data_dict
            chunked_file_root_path = save_chunk_config.get('chunks_path')
            write_path = f"{chunked_file_root_path}/{document_id}/chunks"
            self.__file_sys_handler.create_folders(write_path)
            chunked_file_path_list = self._write_data(
                write_path, chunked_data_dict, 'txt')
            chunked_file_meta_data_path_list = self._write_data(
                write_path, meta_data_dict, 'json')
        else:
            print('Chunk generation failed')
            chunked_file_path_list = []
            chunked_file_meta_data_path_list = []

        return chunked_file_path_list, chunked_file_meta_data_path_list

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
