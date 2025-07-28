# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Open AI LLM provider"""

import logging
from openai import AzureOpenAI
import infy_fs_utils
from ...data.config_data import BaseLlmProviderConfigData
from ...data.llm_data import BaseLlmRequestData, BaseLlmResponseData
from ...llm.interface.i_llm_provider import ILlmProvider


class OpenAILlmProviderConfigData(BaseLlmProviderConfigData):
    """Domain class"""
    api_key: str = None
    api_version: str = None
    api_type: str = None
    deployment_name: str = None
    max_tokens: int = None
    temperature: int = None  # 0.7
    is_chat_model: bool = None
    top_p: float = None
    frequency_penalty: float = None
    presence_penalty: float = None
    stop: str = None


class OpenAILlmRequestData(BaseLlmRequestData):
    """Domain class"""


class OpenAILlmResponseData(BaseLlmResponseData):
    """Domain class"""


class OpenAILlmProvider(ILlmProvider):
    """Open AI LLM provider"""

    def __init__(self, config_data: OpenAILlmProviderConfigData) -> None:
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler():
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler().get_logger()
        else:
            self.__logger = logging.getLogger(__name__)
        service_config_data = {
            'api_key': config_data.api_key,
            'api_version': config_data.api_version,
            'azure_endpoint': config_data.api_url,
            'azure_deployment': config_data.deployment_name,
        }
        self.__llm_obj = AzureOpenAI(**service_config_data)
        self.__max_tokens = config_data.max_tokens
        self.__model = config_data.model_name
        self.__temperature = config_data.temperature
        self.__is_chat_model = config_data.is_chat_model
        self.__top_p = config_data.top_p
        self.__frequency_penalty = config_data.frequency_penalty
        self.__presence_penalty = config_data.presence_penalty
        self.__stop = config_data.stop
        super().__init__(config_data.model_name)

    def get_llm_response(self, llm_request_data: OpenAILlmRequestData) -> OpenAILlmResponseData:
        try:
            llm_response_data = OpenAILlmResponseData()
            llm_obj = self.__llm_obj
            prompt_template = llm_request_data.prompt_template

            # gpt4-8k,gpt-4-32k
            if (self.__is_chat_model):
                message_text = [
                    {"role": "system", "content": prompt_template}]
                response = llm_obj.chat.completions.create(
                    model=self.__model,
                    messages=message_text,
                    temperature=self.__temperature,
                    max_tokens=self.__max_tokens,
                    top_p=self.__top_p,
                    frequency_penalty=self.__frequency_penalty,
                    presence_penalty=self.__presence_penalty,
                    stop=self.__stop
                )
                llm_response_txt = response.choices[0].message.content
            else:
                # text-davinci-003
                params_not_required = [
                    'top_p', 'frequency_penalty', 'presence_penalty', 'stop']
                if self.__top_p or self.__frequency_penalty or self.__presence_penalty or self.__stop:
                    self.__logger.warning(
                        '%s params not required for this model', params_not_required)
                response = llm_obj.completions.create(
                    model=self.__model, prompt=prompt_template, max_tokens=self.__max_tokens)
                llm_response_txt = response.choices[0].text
            llm_response_data.llm_response_txt = llm_response_txt
        except Exception as e:
            self.__logger.exception(e)
            raise e
        return llm_response_data

    def get_model_name(self):
        return f"openai_{self._model_name}"
