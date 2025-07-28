# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for LLM provider interface class"""


import abc
from ...data.llm_data import BaseLlmRequestData, BaseLlmResponseData


class ILlmProvider(metaclass=abc.ABCMeta):
    """Interface class for LLM provider"""

    def __init__(self, model_name: str) -> None:
        self._model_name = model_name

    @abc.abstractmethod
    def get_llm_response(self, llm_request_data: BaseLlmRequestData) -> BaseLlmResponseData:
        """Get response from LLM"""
        raise NotImplementedError

    def get_model_name(self) -> str:
        """Get the model name"""
        return self._model_name
