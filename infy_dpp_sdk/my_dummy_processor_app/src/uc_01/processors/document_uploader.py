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
    "DocumentUploader": {
        "writePath": "./data/output"
    }
}


class DocumentUploaderV1(infy_dpp_sdk.interface.IProcessor):
    """Document uploader Processor Implementation class"""
    __PROCESSEOR_CONTEXT_DATA_NAME = "DocumentUploader"

    def do_execute(self, document_data: DocumentData,
                   context_data: dict, config_data: dict) -> ProcessorResponseData:
        logger = self.get_logger()
        logger.debug("Entering")

        message_data = infy_dpp_sdk.data.MessageData()

        _config_data = config_data.get("DocumentUploader")
        fs_handler: infy_fs_utils.interface.IFileSystemHandler = self.get_fs_handler()
        output_folder_path = _config_data.get('writePath')
        fs_handler.create_folders(output_folder_path)
        output_file_path = output_folder_path + '/' + \
            document_data.metadata.standard_data.filename.value + '_document_data.json'
        fs_handler.write_file(
            output_file_path, document_data.json(indent=4), encoding='utf-8')
        context_data[self.__PROCESSEOR_CONTEXT_DATA_NAME] = {
            "save_file_path": output_file_path
        }
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
