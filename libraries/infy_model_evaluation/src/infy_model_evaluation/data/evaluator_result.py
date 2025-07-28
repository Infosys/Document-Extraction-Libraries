"""Base class for evaluation output"""
# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List, Optional
try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel


class EvaluatorResultEntry(BaseModel):
    """Base class for evaluation result """
    question: str = None
    contexts: list = None
    ground_truth: str = None
    answer: str = None
    additional_data: dict = None
    metrics: list


class EvaluatorResult(BaseModel):
    """Base class for evaluation result """
    result: Optional[List[EvaluatorResultEntry]] = None
