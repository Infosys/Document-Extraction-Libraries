# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List
import uuid
try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel


class BaseLlmRequestData(BaseModel):
    """Base class for request to LLM"""
    # request_id: str = None
    prompt_template: str = None
    template_var_to_value_dict: dict = None


class BaseLlmResponseData(BaseModel):
    """Base class for response from LLM"""
    llm_request_txt: str = None
    llm_response_txt: str = None
    status_code : str = None
    status_message : str = None   


class BaseLlmResponseList(BaseModel):
    """Base class for batch response from LLM"""
    responses: List = [BaseLlmResponseData]
