# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import infy_dpp_sdk
from infy_dpp_sdk.data import *
from infy_dpp_sdk.data.document_data import DocumentData
from infy_dpp_sdk.data.processor_response_data import ProcessorResponseData


class MetadataExtractor(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__logger = self.get_logger()
        self.__file_sys_handler = self.get_fs_handler()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        response_data = infy_dpp_sdk.data.ProcessorResponseData()
        if not document_data.metadata:
            work_file_path = context_data.get('request_creator', {}).get(
                'work_file_path', None)
            root_path = self.__file_sys_handler.get_storage_root_uri().split(':', 1)[
                1].replace('//', '').lower()
            file_path = f'{root_path}/{work_file_path}'
            # add logi to extract metadata
            metadata = infy_dpp_sdk.data.MetaData(
                standard_data=infy_dpp_sdk.data.StandardData(
                    filepath=infy_dpp_sdk.data.ValueData(value=file_path)))
            document_data = infy_dpp_sdk.data.DocumentData(
                document_id=document_data.document_id, metadata=metadata)
        response_data.document_data = document_data
        response_data.context_data = context_data
        return response_data
