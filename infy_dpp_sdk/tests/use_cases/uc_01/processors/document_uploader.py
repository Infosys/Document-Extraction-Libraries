# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import infy_dpp_sdk
from infy_dpp_sdk.data.document_data import DocumentData
from infy_dpp_sdk.data.processor_response_data import ProcessorResponseData

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
        _config_data = config_data.get("DocumentUploader")
        output_folder_path = _config_data.get('writePath')
        os.makedirs(output_folder_path, exist_ok=True)
        output_file_path = output_folder_path + '/' + \
            document_data.metadata.standard_data.filename.value + '_document_data.json'
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(document_data.json(indent=4))
        context_data[self.__PROCESSEOR_CONTEXT_DATA_NAME] = {
            "save_file_path": output_file_path
        }
        response_data = infy_dpp_sdk.data.ProcessorResponseData(
            document_data=document_data, context_data=context_data)
        return response_data
