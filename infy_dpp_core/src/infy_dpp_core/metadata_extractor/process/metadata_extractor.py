# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import infy_dpp_sdk
from infy_dpp_sdk.data import *
from infy_dpp_sdk.data.document_data import DocumentData
from infy_dpp_sdk.data.processor_response_data import ProcessorResponseData

from infy_dpp_core.common.file_system_manager import FileSystemManager
from infy_dpp_core.common.logger_factory import LoggerFactory


class MetadataExtractor(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__logger = LoggerFactory().get_logger()
        self.__file_sys_handler = FileSystemManager().get_file_system_handler()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        response_data = infy_dpp_sdk.data.ProcessorResponseData()
        # TODO: [added by raj] add logi to extract metadata
        response_data.document_data = document_data
        response_data.context_data = context_data
        return response_data
