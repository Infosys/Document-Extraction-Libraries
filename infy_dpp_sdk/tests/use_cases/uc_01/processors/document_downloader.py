# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import re
import uuid
from typing import List
import infy_fs_utils
import infy_dpp_sdk
from infy_dpp_sdk.data import (DocumentData, ProcessorResponseData)

# Config data schema
PROCESSOR_CONFIG_DATA = {
    "DocumentDownloader": {
        "readPath": "./data/input",
        "filter": {
            "include": ["*.pdf", "*.jpg"],
            "exclude": []
        },
        "writePath": "./data/work"
    }
}


class DocumentDownloaderV1(infy_dpp_sdk.interface.IProcessor):
    """Document downloader Processor Implementation class"""
    __PROCESSOR_CONTEXT_DATA_NAME = "DocumentDownloader"

    def do_execute(self, document_data: DocumentData,
                   context_data: dict, config_data: dict) -> ProcessorResponseData:
        raise NotImplementedError

    def do_execute_batch(self, document_data_list: List[DocumentData],
                         context_data_list: List[dict],
                         config_data: dict) -> List[ProcessorResponseData]:
        logger = self.get_logger()
        logger.debug("Entering")
        response_list = []
        _config_data = config_data.get("DocumentDownloader")
        fs_handler: infy_fs_utils.interface.IFileSystemHandler = self.get_fs_handler()
        files = fs_handler.list_files(_config_data.get("readPath"))
        files2 = []
        for file in files:
            for filter_pattern in _config_data.get("filter").get("include"):
                matches = re.match(f".{filter_pattern}", file)
                if matches:
                    files2.append(file)
        files = files2
        _document_data_list = [self.__get_document_data(x) for x in files]
        _context_data_list = [self.__get_context_data(
            context_data_list) for x in files]

        for document_data, context_data in zip(_document_data_list, _context_data_list):
            work_folder_path = _config_data.get(
                'writePath') + f"/W-{self.__get_uuid()}"
            fs_handler.create_folders(work_folder_path)
            new_file_path = fs_handler.copy_file(
                document_data.metadata.standard_data.filepath.value, work_folder_path)
            context_data[self.__PROCESSOR_CONTEXT_DATA_NAME] = {
                "work_file_path": new_file_path
            }
            response_data = infy_dpp_sdk.data.ProcessorResponseData(
                document_data=document_data, context_data=context_data)
            response_list.append(response_data)
        logger.debug("Exiting")
        return response_list

    def __get_document_data(self, filepath):
        document_data = infy_dpp_sdk.data.DocumentData()
        metadata = infy_dpp_sdk.data.MetaData(
            standard_data=infy_dpp_sdk.data.StandardData(
                filepath=infy_dpp_sdk.data.ValueData(value=filepath)))
        document_data.metadata = metadata

        return document_data

    def __get_context_data(self, context_data_list):
        if not context_data_list:
            return {}
        if len(context_data_list) == 1:
            return context_data_list[0].copy()

    def __get_uuid(self):
        """Get uuid"""
        return str(uuid.uuid4())
