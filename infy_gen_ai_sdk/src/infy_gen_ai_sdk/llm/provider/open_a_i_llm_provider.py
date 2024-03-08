# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Open AI LLM provider"""

from langchain.llms import AzureOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from infy_gen_ai_sdk.common.logger_factory import LoggerFactory
from infy_gen_ai_sdk.data.config_data import BaseLlmProviderConfigData
from infy_gen_ai_sdk.data.llm_data import BaseLlmRequestData, BaseLlmResponseData
from infy_gen_ai_sdk.llm.interface.i_llm_provider import ILlmProvider


class OpenAILlmProviderConfigData(BaseLlmProviderConfigData):
    """Domain class"""
    api_key: str = None
    api_version: str = None
    api_type: str = None
    deployment_name: str = None
    max_tokens: int = None
    temperature:int = None #0.7


class OpenAILlmRequestData(BaseLlmRequestData):
    """Domain class"""


class OpenAILlmResponseData(BaseLlmResponseData):
    """Domain class"""


class OpenAILlmProvider(ILlmProvider):
    """Open AI LLM provider"""

    def __init__(self, config_data: OpenAILlmProviderConfigData) -> None:
        self.__logger = LoggerFactory().get_logger()
        service_config_data = {
            'openai_api_key': config_data.api_key,
            'openai_api_version': config_data.api_version,
            'openai_api_base': config_data.api_url,
            'openai_api_type': config_data.api_type,
            'model_name': config_data.model_name,
            'deployment_name': config_data.deployment_name,
            'max_tokens': config_data.max_tokens,
            'temperature':config_data.temperature
        }
        self.__llm_obj = AzureOpenAI(**service_config_data)

    def get_llm_response(self, llm_request_data: OpenAILlmRequestData) -> OpenAILlmResponseData:
        try:
            llm_response_data = OpenAILlmResponseData()
            llm_obj = self.__llm_obj
            variable_to_value_dict = llm_request_data.template_var_to_value_dict
            variable_list = list(variable_to_value_dict.keys())
            prompt_template_obj = PromptTemplate(template=llm_request_data.prompt_template,
                                                 input_variables=variable_list)

            # This is done just to get the flattened LLM request text
            llm_request_txt = prompt_template_obj.format(
                **variable_to_value_dict)
            llm_response_data.llm_request_txt = llm_request_txt

            llm_chain = LLMChain(prompt=prompt_template_obj, llm=llm_obj)
            llm_response_txt = llm_chain.run(**variable_to_value_dict)

            llm_response_data.llm_response_txt = llm_response_txt
        except Exception as e:
            self.__logger.exception(e)
            raise e
        return llm_response_data
