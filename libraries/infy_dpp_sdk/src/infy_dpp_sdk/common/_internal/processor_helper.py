# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Processor Helper class"""
from ...data import (DocumentData, ProcessorResponseData, MessageData,
                     MessageItemData, MessageTypeEnum, MessageCodeEnum)


class ProcessorHelper():
    """Class for Processor Helper"""

    @classmethod
    def create_processor_response_data(cls, document_data: DocumentData,
                                       context_data: dict,
                                       exception: Exception) -> ProcessorResponseData:
        """Create Processor Response Data with exception"""
        message = f"UNHANDLED EXCEPTION => {exception}"
        message_data = MessageData()
        message_item_data = MessageItemData(
            message_type=MessageTypeEnum.ERROR,
            message_code=MessageCodeEnum.SERVER_ERR_UNHANDLED_EXCEPTION,
            message_text=message)
        message_data.messages.append(message_item_data)
        processor_response_data = ProcessorResponseData(
            document_data=document_data, context_data=context_data,
            message_data=message_data)
        return processor_response_data

    @classmethod
    def get_messages(cls, processor_response_data: ProcessorResponseData,
                     message_code_enum: MessageCodeEnum = None) -> list:
        """Get messages from Processor Response Data"""
        messages = []
        if processor_response_data.message_data and processor_response_data.message_data.messages:
            messages = processor_response_data.message_data.messages
            if message_code_enum:
                messages = [
                    x for x in messages if x.message_code == message_code_enum]
        return messages
