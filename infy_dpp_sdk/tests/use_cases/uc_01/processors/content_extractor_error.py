# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import infy_dpp_sdk
from infy_dpp_sdk.data import (DocumentData, ProcessorResponseData)

# Config data schema
PROCESSOR_CONFIG_DATA = {
    "ContentExtractorError": {
    },
}


class ContentExtractorErrorV1(infy_dpp_sdk.interface.IProcessor):
    """Content Extractor processor for error simulation"""
    __PROCESSOR_CONTEXT_DATA_NAME = "ContentExtractorError"

    def do_execute(self, document_data: DocumentData,
                   context_data: dict, config_data: dict) -> ProcessorResponseData:
        logger = self.get_logger()
        logger.debug("Entering")

        logger.debug("Exiting")
        raise ValueError(
            "This is a simulated error from ContentExtractorErrorV1.")
