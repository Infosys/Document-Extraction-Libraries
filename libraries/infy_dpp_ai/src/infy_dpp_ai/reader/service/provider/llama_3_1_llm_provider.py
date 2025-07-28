# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Llama LLM provider"""
import uuid
import json
import logging
import requests
import infy_fs_utils
import infy_dpp_sdk
from deprecated import deprecated
# from infy_gen_ai_sdk.common.logger_factory import LoggerFactory
from infy_gen_ai_sdk.schema.config_data import BaseLlmProviderConfigData
from infy_gen_ai_sdk.schema.llm_data import BaseLlmRequestData, BaseLlmResponseData
from infy_gen_ai_sdk.llm.interface.i_llm_provider import ILlmProvider


@deprecated(version='0.0.6', reason="This class is deprecated. Please use new class OpenAIFormatLlmProvider.")
class LlamaLlmProviderConfigData(BaseLlmProviderConfigData):
    """Domain class"""
    inference_url: str = None
    model: str = None
    deployment_name: str = None
    temperature: float = None  # 0.7
    top_p: float = None
    frequency_penalty: float = None
    presence_penalty: float = None
    max_tokens: int = None
    stop: str = None
    remove_query_from_response: bool = None


@deprecated(version='0.0.6', reason="This class is deprecated. Please use new class OpenAIFormatLlmProvider.")
class LlamaLlmRequestData(BaseLlmRequestData):
    """Domain class"""


@deprecated(version='0.0.6', reason="This class is deprecated. Please use new class OpenAIFormatLlmProvider.")
class LlamaLlmResponseData(BaseLlmResponseData):
    """Domain class"""


@deprecated(version='0.0.6', reason="This class is deprecated. Please use new class OpenAIFormatLlmProvider.")
class LlamaLlmProvider(ILlmProvider):
    """Llama LLM provider"""

    def __init__(self, config_data: LlamaLlmProviderConfigData, file_sys_handler, logger, app_config) -> None:
        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = file_sys_handler

        self.__model_url = config_data.inference_url
        self.__max_tokens = config_data.max_tokens
        self.__model = config_data.model
        self.__temperature = config_data.temperature
        self.__top_p = config_data.top_p
        self.__frequency_penalty = config_data.frequency_penalty
        self.__presence_penalty = config_data.presence_penalty
        self.__stop = config_data.stop

    def get_llm_response(self, llm_request_data: LlamaLlmRequestData) -> LlamaLlmResponseData:
        try:
            llm_response_data = LlamaLlmResponseData()
            combined_text = llm_request_data.template_var_to_value_dict.get(
                'context')
            query = llm_request_data.template_var_to_value_dict.get('question')
            template = llm_request_data.prompt_template
            llm_response_data.llm_response_txt, llm_response_data.llm_request_txt = self.__generate_answer(
                query, combined_text, template)
        except Exception as e:
            self.__logger.exception(e)
            raise e
        return llm_response_data

    def get_llm_response_batch(self, llm_request_data: LlamaLlmRequestData):
        pass

    def __generate_answer(self, query, context_text, prompt):
        combined_query = prompt.replace(
            '{context}', context_text).replace('{question}', query)
        model_output = self.__invoke_api(combined_query)
        return model_output, combined_query

    def __invoke_api(self, query):
        url = self.__model_url
        headers = {"X-Cluster": "H100"}
        response = ''
        request_id = str(uuid.uuid4())
        data = {
            "model": self.__model,
            "messages": self.__set_prompt(query),
            "max_tokens": self.__max_tokens,
            "temperature": self.__temperature,
            "top_p": self.__top_p,
            "frequency_penalty": self.__frequency_penalty,
            "presence_penalty": self.__presence_penalty,
            "stop": self.__stop
        }

        try:
            model_response = requests.post(
                url, headers=headers, data=json.dumps(data), verify=False, timeout=180)
            if model_response.status_code == 200:
                self.__logger .info(
                    'API call to %s Inference model successfull', self.__model)
                ml_model_output = model_response.json()

                if len(ml_model_output) > 0:
                    self.__logger.debug("RESPONSE %s:%s", request_id, json.dumps(
                        ml_model_output, indent=4))

                    response = ml_model_output.get(
                        'choices')[0].get('message').get('content')
                    if response:
                        self.__logger .info('Model answer has been detected')
                    else:
                        raise Exception("Model has given empty responses")
            else:
                raise Exception(
                    f'Error in calling API {model_response.status_code}')
        except Exception as e:
            self.__logger .error('Error in calling API %s', e)
        return response

    def __set_prompt(self, input_text):
        message = [
            {
                "role": "system",
                "content": "You are an AI Assistant that helps people find information.",
            },
            {"role": "user", "content": input_text},
        ]
        return message
