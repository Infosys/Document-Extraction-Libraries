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
    def __init__(self):
        # self.__logger = LoggerFactory().get_logger()
        self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
        ).get_fs_logging_handler(infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        self.__app_config = infy_dpp_sdk.common.AppConfigManager().get_app_config()
        # self.__file_sys_handler = self.get_fs_handler()
        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)

    def save_chunk_data(self, page_segment_data_dict, document_id, save_chunk_config, meta_data_dict):
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
