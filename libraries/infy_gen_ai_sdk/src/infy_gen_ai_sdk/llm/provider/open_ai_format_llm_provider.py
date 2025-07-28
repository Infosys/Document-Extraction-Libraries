# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Open AI Format LLM provider"""
import logging
import os
from typing import List
import infy_fs_utils
import litellm
from ...schema.config_data import BaseLlmProviderConfigData
from ...schema.llm_data import BaseLlmRequestData, BaseLlmResponseData
from ...llm.interface.i_llm_provider import ILlmProvider


class OpenAIFormatLlmProviderConfigData(BaseLlmProviderConfigData):
    """Domain class"""
    api_url: str = None
    api_key: str = None
    user_id: str = None
    model_name: str = None
    deployment_name: str = None
    max_tokens: int = None
    temperature: float = None
    top_p: float = None
    frequency_penalty: float = None
    presence_penalty: float = None
    stop: str = None
    timeout: int = None


class OpenAIFormatLlmRequestData(BaseLlmRequestData):
    """Domain class"""


class OpenAIFormatLlmResponseData(BaseLlmResponseData):
    """Domain class"""


class OpenAIFormatLlmProvider(ILlmProvider):
    """Open AI Format LLM provider"""

    def __init__(self, config_data: OpenAIFormatLlmProviderConfigData) -> None:
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler():
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler().get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

        self.__api_key = config_data.api_key
        self.__api_url = config_data.api_url
        self.__user_id = config_data.user_id
        self.__model_name = config_data.model_name
        self.__deployment_name = config_data.deployment_name
        self.__max_tokens = config_data.max_tokens
        self.__temperature = config_data.temperature
        self.__top_p = config_data.top_p
        self.__frequency_penalty = config_data.frequency_penalty
        self.__presence_penalty = config_data.presence_penalty
        self.__stop = config_data.stop
        self.__timeout = config_data.timeout

    def get_llm_response(self, llm_request_data: OpenAIFormatLlmRequestData) -> OpenAIFormatLlmResponseData:
        try:
            llm_response_data = OpenAIFormatLlmResponseData()
            prompt_template = llm_request_data.prompt_template
            __context = llm_request_data.template_var_to_value_dict.get(
                'context')
            __question = llm_request_data.template_var_to_value_dict.get(
                'question')
            if __context and __question:
                start_phrase = prompt_template.format(
                    context=__context, question=__question)
            else:
                start_phrase = prompt_template
            message_text = [{"role": "user", "content": start_phrase}]

            if self.__api_key:
                os.environ["AZURE_API_KEY"] = self.__api_key
            if self.__user_id:
                extra_headers = {
                    'Content-Type': 'application/json',
                    'X-User-Id': self.__user_id,
                    'api_key': f'Bearer {self.__api_key}'
                }
            else:
                extra_headers = {
                    'Content-Type': 'application/json',
                    'api_key': f'Bearer {self.__api_key}'
                }

            response = litellm.completion(
                model=self.__model_name,
                deployment_id=self.__deployment_name,
                api_base=self.__api_url,
                messages=message_text,
                max_tokens=self.__max_tokens,
                temperature=self.__temperature,
                top_p=self.__top_p,
                frequency_penalty=self.__frequency_penalty,
                presence_penalty=self.__presence_penalty,
                stop=self.__stop,
                timeout=self.__timeout,
                extra_headers=extra_headers
            )
        
            if hasattr(response, 'status_code') and hasattr(response, 'message'):
                llm_response_data.llm_response_txt = ''
                llm_response_data.llm_request_txt = message_text
                llm_response_data.status_code = response.status_code
                llm_response_data.status_message = response.message
            else:
                llm_response_txt = response['choices'][0]['message']['content']
                llm_response_data.llm_response_txt = llm_response_txt
                llm_response_data.llm_request_txt = message_text
                llm_response_data.status_code = ''
                llm_response_data.status_message = ''
                
        except Exception as e:
            self.__logger.exception(e)
            raise e
        return llm_response_data

    def get_llm_response_batch(self, llm_request_data_list: List[OpenAIFormatLlmRequestData]) -> OpenAIFormatLlmResponseData:
        try:
            llm_response_data = OpenAIFormatLlmResponseData()
            message_text = []
            for llm_request_data in llm_request_data_list:
                prompt_template = llm_request_data.prompt_template
                __context = llm_request_data.template_var_to_value_dict.get(
                    'context')
                __question = llm_request_data.template_var_to_value_dict.get(
                    'question')
                if __context and __question:
                    start_phrase = prompt_template.format(
                        context=__context, question=__question)
                else:
                    start_phrase = prompt_template

                message_text.append(
                    [{"role": "user", "content": start_phrase}])

            if self.__api_key:
                os.environ["AZURE_API_KEY"] = self.__api_key

            if self.__user_id:
                extra_headers = {
                    'Content-Type': 'application/json',
                    'X-User-Id': self.__user_id,
                    'api_key': f'Bearer {self.__api_key}'
                }
            else:
                extra_headers = {
                    'Content-Type': 'application/json',
                    'api_key': f'Bearer {self.__api_key}'
                }

            response_list = litellm.batch_completion(
                model=self.__model_name,
                deployment_id=self.__deployment_name,
                api_base=self.__api_url,
                messages=message_text,
                max_tokens=self.__max_tokens,
                temperature=self.__temperature,
                top_p=self.__top_p,
                frequency_penalty=self.__frequency_penalty,
                presence_penalty=self.__presence_penalty,
                stop=self.__stop,
                extra_headers=extra_headers
            )

            llm_response_data_list = []
            for idx, response in enumerate(response_list):
                if hasattr(response, 'status_code') and hasattr(response, 'message'):
                    llm_response_data.llm_response_txt = ''
                    llm_response_data.llm_request_txt = ''
                    llm_response_data.status_code = response.status_code
                    llm_response_data.status_message = response.message
                else:
                    llm_response_txt = response['choices'][0]['message']['content']
                    llm_response_data = OpenAIFormatLlmResponseData(
                        llm_response_txt=llm_response_txt)
                    llm_response_data.llm_request_txt = message_text[idx]
                    llm_response_data.status_code = ''
                    llm_response_data.status_message = ''
                    
                llm_response_data_list.append(llm_response_data)

        except Exception as e:
            self.__logger.exception(e)
            raise e
        return llm_response_data_list
