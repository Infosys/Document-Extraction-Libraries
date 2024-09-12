# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
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
        context_data_key = [x for x in config_data.keys(
        ) if x.startswith(self.__PROCESSOR_CONTEXT_DATA_NAME)][0]
        config_data = config_data.get(context_data_key)

        message_data = infy_dpp_sdk.data.MessageData()

        # Extract attributes from word tokens available in context_data
        tokens = document_data.text_data[0].text.replace('\n', ' ').split(' ')
        tokens = [token for token in tokens if token]

        if not tokens:
            message_item_data = infy_dpp_sdk.data.MessageItemData(
                message_type=infy_dpp_sdk.data.MessageTypeEnum.INFO,
                message_text="Tokens not found in context_data of ocr_generator")
            message_data.messages.append(message_item_data)
            processor_response_data = infy_dpp_sdk.data.ProcessorResponseData(
                document_data=document_data, context_data=context_data,
                message_data=message_data)
            return processor_response_data

        business_attributes = []
        for required_token in config_data.get('required_tokens', []):
            business_attribute_data = {
                'name': required_token['name'],
                'text': tokens[required_token['position']]
            }
            business_attributes.append(business_attribute_data)

        # Populate context data
        context_data[context_data_key] = business_attributes

        # Populate response data
        message_item_data = infy_dpp_sdk.data.MessageItemData(
            message_code=infy_dpp_sdk.data.MessageCodeEnum.INFO_SUCCESS,
            message_type=infy_dpp_sdk.data.MessageTypeEnum.INFO,
        )
        message_data.messages.append(message_item_data)
        processor_response_data = infy_dpp_sdk.data.ProcessorResponseData(
            document_data=document_data, context_data=context_data,
            message_data=message_data)

        # Error simulation - tamper with config_data to check for negative impact
        # NOTE: config_data is supposed to be a read-only object for the processor
        config_data['required_tokens'] = None

        logger.debug("Exiting")
        return processor_response_data
