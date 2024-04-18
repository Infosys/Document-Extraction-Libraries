# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List
import infy_dpp_sdk
from infy_dpp_sdk.data import (DocumentData, ProcessorResponseData)

# Config data schema
PROCESSOR_CONFIG_DATA = {
    "DocumentDownloaderError": {
    }
}


class DocumentDownloaderErrorV1(infy_dpp_sdk.interface.IProcessor):
    """Document downloader processor for error simulation"""
    __PROCESSOR_CONTEXT_DATA_NAME = "DocumentDownloaderError"

    def do_execute(self, document_data: DocumentData,
                   context_data: dict, config_data: dict) -> ProcessorResponseData:
        raise NotImplementedError

    def do_execute_batch(self, document_data_list: List[DocumentData],
                         context_data_list: List[dict],
                         config_data: dict) -> List[ProcessorResponseData]:
        logger = self.get_logger()
        logger.debug("Entering")

        logger.debug("Exiting")
        raise ValueError(
            "This is a simulated error from DocumentDownloaderErrorV1.")
