# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import infy_dpp_sdk

# Config data schema
PROCESSOR_CONFIG_DATA = {
    "AttributeExtractor": {
        "required_tokens": [
            {
                "name": "Invoice No",
                "position": 7
            },
            {
                "name": "Invoice Date",
                "position": 14
            }
        ]
    },
}


class AttributeExtractorV1(infy_dpp_sdk.interface.IProcessor):
    """Document uploader Processor Implementation class"""
    __PROCESSOR_CONTEXT_DATA_NAME = "AttributeExtractor"

    def do_execute(self, document_data: infy_dpp_sdk.data.DocumentData,
                   context_data: dict, config_data: dict) -> infy_dpp_sdk.data.ProcessorResponseData:
        logger = self.get_logger()
        logger.debug("Entering")
        config_data = config_data.get("AttributeExtractor")

        processor_response_data = infy_dpp_sdk.data.ProcessorResponseData()

        # Extract attributes from word tokens available in context_data
        tokens = document_data.text_data[0].text.replace('\n', ' ').split(' ')
        tokens = [token for token in tokens if token]

        if not tokens:
            message_data = infy_dpp_sdk.data.MessageData("error",
                                                         "Tokens not found in context_data of ocr_generator")
            processor_response_data.message_data = []
            processor_response_data.message_data.append(message_data)
            processor_response_data.document_data = document_data
            return processor_response_data

        business_attributes = []
        for required_token in config_data.get('required_tokens', []):
            business_attribute_data = {
                'name': required_token['name'],
                'text': tokens[required_token['position']]
            }
            business_attributes.append(business_attribute_data)

        # Populate document data
        if not document_data.business_attribute_data:
            document_data.business_attribute_data = []
        document_data.business_attribute_data.extend(business_attributes)

        # Populate context data
        context_data[self.__PROCESSOR_CONTEXT_DATA_NAME] = None

        # Populate response data
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        logger.debug("Exiting")
        return processor_response_data
