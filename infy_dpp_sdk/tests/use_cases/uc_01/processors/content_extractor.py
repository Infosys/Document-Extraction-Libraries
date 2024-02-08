# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import infy_dpp_sdk
from infy_dpp_sdk.data.document_data import DocumentData
from infy_dpp_sdk.data.processor_response_data import ProcessorResponseData

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
        with open(document_data.metadata.standard_data.filepath.value, encoding='utf-8') as f:
            content = f.read()
            text_data = infy_dpp_sdk.data.TextData(page=1, text=content)
            document_data.text_data = [text_data]

        context_data[self.__PROCESSOR_CONTEXT_DATA_NAME]: None

        response_data = infy_dpp_sdk.data.ProcessorResponseData(
            document_data=document_data, context_data=context_data)
        return response_data
