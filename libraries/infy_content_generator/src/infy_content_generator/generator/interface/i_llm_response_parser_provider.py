# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for embedding provider interface class"""

import abc
from ...data.qna_data import QnaResponseData


class ILLMResponseParserProvider(metaclass=abc.ABCMeta):
    """Interface class for question answer generation provider"""
    @abc.abstractmethod
    def parse_llm_response(self, llm_response_txt, input_que_type: dict, context: str) -> QnaResponseData:
        """Parse the LLM response"""
        raise NotImplementedError
