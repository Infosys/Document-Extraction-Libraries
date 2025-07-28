"""Base class for Evaluator config data"""
# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel


class BaseQnaGeneratorProviderConfigData(BaseModel):
    """Base class for QnA generator config data"""
    api_url: str = None
    model_name: str = None
    model_home_path: str = None
