# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List
import infy_dpp_sdk
from infy_dpp_sdk.data import (DocumentData, ProcessorResponseData)


class RequestCreatorPseudo(infy_dpp_sdk.interface.IProcessor):
    """Pseudo Request Creator Processor Implementation class"""
    __PROCESSOR_CONTEXT_DATA_NAME = "RequestCreatorPseudo"

    def do_execute(self, document_data: DocumentData,
                   context_data: dict, config_data: dict) -> ProcessorResponseData:
        raise NotImplementedError

    def do_execute_batch(self, document_data_list: List[DocumentData],
                         context_data_list: List[dict],
                         config_data: dict) -> List[ProcessorResponseData]:
        logger = self.get_logger()
        logger.debug("Entering")
        processor_response_data_list = []
        _document_data_list = [self.__get_document_data(x) for x in ["dummy"]]
        _context_data_list = [self.__get_context_data(
            context_data_list) for x in ["dummy"]]

        for document_data, context_data in zip(_document_data_list, _context_data_list):

            context_data[self.__PROCESSOR_CONTEXT_DATA_NAME] = {
                "work_file_path": ""
            }
            # Populate response data
            message_data = infy_dpp_sdk.data.MessageData()
            message_item_data = infy_dpp_sdk.data.MessageItemData(
                message_type=infy_dpp_sdk.data.MessageTypeEnum.INFO,
                message_code=infy_dpp_sdk.data.MessageCodeEnum.INFO_SUCCESS
            )
            message_data.messages.append(message_item_data)
            processor_response_data = infy_dpp_sdk.data.ProcessorResponseData(
                document_data=document_data, context_data=context_data,
                message_data=message_data)
            # To test scenario without message_data in response
            # processor_response_data = infy_dpp_sdk.data.ProcessorResponseData(
            #     document_data=document_data, context_data=context_data)

            # Add to overall list
            processor_response_data_list.append(processor_response_data)
        logger.debug("Exiting")
        return processor_response_data_list

    def __get_document_data(self, filepath):
        document_data = infy_dpp_sdk.data.DocumentData()
        metadata = infy_dpp_sdk.data.MetaData(
            standard_data=infy_dpp_sdk.data.StandardData(
                filepath=infy_dpp_sdk.data.ValueData(value=filepath)))
        document_data.metadata = metadata

        return document_data

    def __get_context_data(self, context_data_list):
        if not context_data_list:
            return {}
        if len(context_data_list) == 1:
            return context_data_list[0].copy()
