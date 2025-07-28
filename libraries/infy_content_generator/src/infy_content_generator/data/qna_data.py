# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel


class QnaData(BaseModel):
    """Class for storing question answer data"""
    type: str
    question: str
    answer: str
    answer_source: str


class QnaResponseData(BaseModel):
    """Response data class for QnA generation"""
    qna_data_list: list[QnaData]


class BaseStrategyConfigData(BaseModel):
    """ Strategy configuration data class"""
