# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for LLM provider interface class"""


import abc
from ...schema.llm_data import BaseLlmRequestData, BaseLlmResponseData


class ILlmProvider(metaclass=abc.ABCMeta):
    """Interface class for LLM provider"""

    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def get_llm_response(self, llm_request_data: BaseLlmRequestData) -> BaseLlmResponseData:
        """Get response from LLM"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_llm_response_batch(self, llm_request_data_list: BaseLlmRequestData) -> BaseLlmResponseData:
        """Get response from LLM"""
        raise NotImplementedError
