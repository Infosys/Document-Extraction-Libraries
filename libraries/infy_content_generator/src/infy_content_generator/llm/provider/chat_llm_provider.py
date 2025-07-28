# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for OpenAI embedding provider class"""

import logging
import json
import requests
from ..interface.i_llm_provider import ILlmProvider
from ...data.llm_data import BaseLlmRequestData, BaseLlmResponseData
from ...data.config_data import BaseLlmProviderConfigData


class ChatLlmProviderConfigData(BaseLlmProviderConfigData):
    """Domain class"""
    api_url: str
    model_name: str
    headers: dict = None
    json_payload: dict = None


class ChatLlmRequestData(BaseLlmRequestData):
    """Domain class"""


class ChatLlmResponseData(BaseLlmResponseData):
    """Domain class"""


class ChatLlmProvider(ILlmProvider):

    def __init__(self, config_data: ChatLlmProviderConfigData) -> None:
        self.__api_url = config_data.api_url
        self.__headers = config_data.headers
        self.__model = config_data.model_name
        self.__json_payload = config_data.json_payload
        self.__verify_ssl = False
        self.__logger = logging.getLogger(__name__)
        super().__init__(config_data.model_name)

    def get_llm_response(self,  llm_request_data: ChatLlmRequestData) -> ChatLlmResponseData:
        """Generate QnA pairs for given text"""
        llm_response_data = ChatLlmResponseData()
        prompt_template = llm_request_data.prompt_template

        message = [
            {
                "role": "system",
                "content": "You are an AI Assistant that helps people find information.",
            },
            {
                "role": "user",
                "content": prompt_template
            },
        ]

        json_payload = self.__json_payload.copy()
        json_payload['messages'] = message
        response = None
        try:
            self.__logger.debug(json.dumps(json_payload, indent=4))
            model_response = requests.post(
                self.__api_url, headers=self.__headers, json=json_payload, verify=self.__verify_ssl, timeout=180)
            if model_response.status_code == 200:
                ml_model_output = model_response.json()

                if len(ml_model_output) > 0:
                    if isinstance(ml_model_output, list):
                        ml_model_output = ml_model_output[0]
                    self.__logger.debug(json.dumps(
                        ml_model_output, indent=4))
                    response = ml_model_output["choices"][0]["message"]["content"]
                    if response:
                        self.__logger .info('Model answer has been detected')
                    else:
                        raise Exception("Model has given empty responses")
            else:
                raise Exception(
                    f'Error in calling API {model_response.status_code}')
        except Exception as e:
            self.__logger .error('Error in calling API %s', e)
        llm_response_data.llm_response_txt = response

        return llm_response_data

    def get_model_name(self):
        return f"custom_{self._model_name}"
