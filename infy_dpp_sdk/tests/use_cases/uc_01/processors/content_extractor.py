# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import infy_fs_utils
import infy_dpp_sdk
from infy_dpp_sdk.data import (DocumentData, ProcessorResponseData)

# Config data schema
PROCESSOR_CONFIG_DATA = {
    "ContentExtractor": {
    },
}


class ContentExtractorV1(infy_dpp_sdk.interface.IProcessor):
    """Content Extractor Processor class"""
    __PROCESSOR_CONTEXT_DATA_NAME = "ContentExtractor"

    def do_execute(self, document_data: DocumentData,
                   context_data: dict, config_data: dict) -> ProcessorResponseData:
        logger = self.get_logger()
        logger.debug("Entering")
        fs_handler: infy_fs_utils.interface.IFileSystemHandler = self.get_fs_handler()
        file_content = fs_handler.read_file(
            document_data.metadata.standard_data.filepath.value, encoding='utf-8')
        text_data = infy_dpp_sdk.data.TextData(page=1, text=file_content)
        document_data.text_data = [text_data]

        context_data[self.__PROCESSOR_CONTEXT_DATA_NAME]: None

        response_data = infy_dpp_sdk.data.ProcessorResponseData(
            document_data=document_data, context_data=context_data)
        logger.debug("Exiting")
        return response_data
