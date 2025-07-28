# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""
This class is the implementation for the process layer
"""

from .interface import IQnaStrategyProvider
from ..data.qna_data import QnaResponseData


class QnaGenerator():
    """Class for generation of questions and answers"""

    def __init__(self, qna_strategy_provider: IQnaStrategyProvider) -> None:
        self.__qna_strategy_provider = qna_strategy_provider

    def generate_qna(self, context_list: list[str], metadata: dict = None) -> QnaResponseData:
        """Generate qna for provided text."""

        qna_response_data = self.__qna_strategy_provider.generate_qna(
            context_list, metadata)

        return qna_response_data
