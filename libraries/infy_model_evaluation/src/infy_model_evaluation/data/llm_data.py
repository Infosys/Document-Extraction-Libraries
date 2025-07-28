# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#
from typing import Dict, Any
try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel


class BaseLlmRequestData(BaseModel):
    """Base class for request to LLM"""
    prompt_template: str = None


class BaseLlmResponseData(BaseLlmRequestData):
    """Base class for response from LLM"""
    llm_request_txt: str = None
    llm_response_txt: str = None


class LLMProvidersData(BaseModel):
    llm_provider_obj: Any = None  # ILlmProvider
    llm_res_parser_obj: Any = None  # ILLMResponseParserProvider


class LLMConfigData(BaseModel):
    __root__: Dict[str, LLMProvidersData]
