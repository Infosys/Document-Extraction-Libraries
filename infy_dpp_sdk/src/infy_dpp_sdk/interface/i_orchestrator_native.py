# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from abc import ABC, abstractmethod
from typing import List

from ..data import ProcessorResponseData, DocumentData


class IOrchestratorNative(ABC):
    """Orchestrator Interface for native execution"""
    @abstractmethod
    def run_batch(self, document_data_list: List[DocumentData] = None, context_data_list: List[dict] = None) -> List[ProcessorResponseData]:
        """Run the pipeline"""
        raise NotImplementedError("run not implemented")

    @abstractmethod
    def pre_run_hook(self, processor_instance: object, config_data: dict,
                     processor_response_data_list: List[ProcessorResponseData]) -> (object, List[ProcessorResponseData]):
        """ Pre run hook for the processor """
        raise NotImplementedError("pre_run_hook not implemented")

    @abstractmethod
    def post_run_hook(self, processor_instance: object, config_data: dict,
                      processor_response_data_list: List[ProcessorResponseData],
                      new_processor_response_data_list: List[ProcessorResponseData]) -> List[ProcessorResponseData]:
        """ Post run hook for the processor """
        raise NotImplementedError("post_run_hook not implemented")
