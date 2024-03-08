# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
import json
import infy_fs_utils
import infy_dpp_sdk
from infy_dpp_sdk.data import (DocumentData, ProcessorResponseData)


class MyProcessor(infy_dpp_sdk.interface.IProcessor):
    """Content Extractor Processor class"""
    __PROCESSOR_CONTEXT_DATA_NAME = "my_processor"

    def do_execute(self, document_data: DocumentData,
                   context_data: dict, config_data: dict) -> ProcessorResponseData:
        logger = self.get_logger()
        logger.debug("Entering")
        logger.debug("Before"+json.dumps(context_data,indent=4))
        context_data[self.__PROCESSOR_CONTEXT_DATA_NAME]= {"msg":"Hello world"}
        logger.debug("After"+json.dumps(context_data,indent=4))
        response_data = infy_dpp_sdk.data.ProcessorResponseData(
            document_data=document_data, context_data=context_data)
        logger.debug("Exiting")
        return response_data
