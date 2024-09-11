# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from pydantic import BaseModel


class BaseEmbeddingProviderConfigData(BaseModel):
    """Base class for embedding provider config data"""
    api_url: str = None
    model_name: str = None
    model_home_path: str = None


class BaseVectorDbProviderConfigData(BaseModel):
    """Base class for vector db provider config data"""


class BaseLlmProviderConfigData(BaseModel):
    """Base class for LLM provider config data"""
    api_url: str = None
    model_name: str = None
