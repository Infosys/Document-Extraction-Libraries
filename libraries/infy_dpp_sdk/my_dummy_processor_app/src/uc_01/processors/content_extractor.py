# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
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

        message_data = infy_dpp_sdk.data.MessageData()

        fs_handler: infy_fs_utils.interface.IFileSystemHandler = self.get_fs_handler()
        file_content = fs_handler.read_file(
            document_data.metadata.standard_data.filepath.value, encoding='utf-8')
        text_data = infy_dpp_sdk.data.TextData(page=1, text=file_content)
        document_data.text_data = [text_data]

        context_data[self.__PROCESSOR_CONTEXT_DATA_NAME] = file_content

        # Populate response data
        message_item_data = infy_dpp_sdk.data.MessageItemData(
            message_code=infy_dpp_sdk.data.MessageCodeEnum.INFO_SUCCESS,
            message_type=infy_dpp_sdk.data.MessageTypeEnum.INFO,
        )
        message_data.messages.append(message_item_data)
        processor_response_data = infy_dpp_sdk.data.ProcessorResponseData(
            document_data=document_data, context_data=context_data,
            message_data=message_data)

        logger.debug("Exiting")
        return processor_response_data
