# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from abc import ABC, abstractmethod
from typing import List

from ..data.document_data import DocumentData
from ..data.processor_response_data import ProcessorResponseData


class IProcessor(ABC):

    def do_execute_batch(self, document_data_list: List[DocumentData],
                         context_data_list: List[dict], config_data: dict) -> List[ProcessorResponseData]:
        """Run the processor in batch mode"""
        response_list: List[ProcessorResponseData] = []
        for document_data, context_data in zip(document_data_list, context_data_list):
            response_list.append(self.do_execute(
                document_data, context_data, config_data))
        return response_list

    # ------------------------abstractmethod---------------------------
    # These operations have to be implemented in subclasses.
    @abstractmethod
    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        """Run the processor"""
        raise NotImplementedError
