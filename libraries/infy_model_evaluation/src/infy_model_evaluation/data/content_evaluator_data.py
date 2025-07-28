"""Base class for evaluation output"""
# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
from typing import Dict, Union
try:
    from pydantic.v1 import BaseModel, root_validator
except ImportError:
    from pydantic import BaseModel
    from pydantic.class_validators import root_validator


class ContentEvaluatorReqData(BaseModel):
    """Base class for evaluation result """
    question: str = None
    contexts: str = None
    answer: str = None


class MetricsData(BaseModel):
    """Class to define the metrics data.

    Attributes:
        metrics (Dict[str, float]): A dictionary containing metric names as keys and their corresponding values as floats.
    """
    # __root__: Dict[str, float]
    __root__: Dict[str, Union[float, str]]

    @root_validator(pre=True)
    def check_reason_keys(cls, values):
        root_values = values.get('__root__', {})
        float_keys = [key for key, value in root_values.items()
                      if isinstance(value, float)]
        for key in float_keys:
            reason_key = f"{key}_reason"
            if reason_key not in root_values:
                raise ValueError(f"Missing reason key for {key}")
        return values

    # class Config:
    #     extra = Extra.allow


class ContentEvaluatorResData(BaseModel):
    """Content Evaluator Response Data class
    """
    metrics: MetricsData = None
