"""Base class for input dataset"""
# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List, Optional
try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel


class DatasetEntry(BaseModel):
    """Base class for dataset entry """
    question: str = None
    contexts: list = None
    ground_truth: str = None
    answer: Optional[str] = None
    additional_data: Optional[dict] = None


class EvaluatorDataset(BaseModel):
    """Base class for dataset """
    dataset: List[DatasetEntry] = None
