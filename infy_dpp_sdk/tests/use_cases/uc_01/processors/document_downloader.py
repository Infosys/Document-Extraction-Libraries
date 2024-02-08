# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import glob
import uuid
import shutil
from typing import List
import infy_dpp_sdk
from infy_dpp_sdk.data.document_data import DocumentData
from infy_dpp_sdk.data.processor_response_data import ProcessorResponseData

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


class FileUtil:
    """File Utility class"""
    @classmethod
    def get_files(cls, folderpath, file_format, recursive=False, sort_by_date=None):
        """Get files from folderpath with file_format"""
        found_files = []
        for file_type in str(file_format).split(","):
            found_files += glob.glob(
                f"{folderpath}/{file_type}", recursive=recursive)
        if sort_by_date:
            found_files.sort(key=sort_by_date)
        return found_files

    @classmethod
    def copy_file(cls, source_file_path, destination_folder_path):
        """Copy file from source_file_path to destination_file_path"""
        if not os.path.exists(destination_folder_path):
            os.makedirs(destination_folder_path, exist_ok=True)
        new_file_path = shutil.copy(source_file_path, destination_folder_path)
        return new_file_path


class StringUtil:
    """String Utility class"""
    @classmethod
    def get_uuid(cls):
        """Get uuid"""
        return str(uuid.uuid4())


class DocumentDownloaderV1(infy_dpp_sdk.interface.IProcessor):
    """Document downloader Processor Implementation class"""
    __PROCESSOR_CONTEXT_DATA_NAME = "DocumentDownloader"

    def do_execute(self, document_data: DocumentData,
                   context_data: dict, config_data: dict) -> ProcessorResponseData:
        raise NotImplementedError

    def do_execute_batch(self, document_data_list: List[DocumentData],
                         context_data_list: List[dict],
                         config_data: dict) -> List[ProcessorResponseData]:
        response_list = []
        _config_data = config_data.get("DocumentDownloader")
        files = FileUtil.get_files(_config_data.get("readPath"), ",".join(
            _config_data.get("filter").get("include")))
        _document_data_list = [self.__get_document_data(x) for x in files]
        _context_data_list = [self.__get_context_data() for x in files]

        for document_data, context_data in zip(_document_data_list, _context_data_list):
            work_folder_path = _config_data.get(
                'writePath') + f"/W-{StringUtil.get_uuid()}"
            new_file_path = FileUtil.copy_file(
                document_data.metadata.standard_data.filepath.value, work_folder_path)
            context_data[self.__PROCESSOR_CONTEXT_DATA_NAME] = {
                "work_file_path": new_file_path
            }
            response_data = infy_dpp_sdk.data.ProcessorResponseData(
                document_data=document_data, context_data=context_data)
            response_list.append(response_data)

        return response_list

    def __get_document_data(self, filepath):
        document_data = infy_dpp_sdk.data.DocumentData()
        document_data.document_id = StringUtil.get_uuid()
        metadata = infy_dpp_sdk.data.MetaData(
            standard_data=infy_dpp_sdk.data.StandardData(
                filepath=infy_dpp_sdk.data.ValueData(value=filepath)))
        document_data.metadata = metadata

        return document_data

    def __get_context_data(self):
        return {}
