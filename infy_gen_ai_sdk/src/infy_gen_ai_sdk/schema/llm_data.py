# ===============================================================================================================#
# Copyright 2022 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from pydantic import BaseModel


class BaseLlmRequestData(BaseModel):
    """Base class for request to LLM"""
    prompt_template: str = None
    template_var_to_value_dict: dict = None


class BaseLlmResponseData(BaseLlmRequestData):
    """Base class for response from LLM"""
    llm_request_txt: str = None
    llm_response_txt: str = None
