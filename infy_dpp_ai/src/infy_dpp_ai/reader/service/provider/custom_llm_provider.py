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
# from infy_gen_ai_sdk.common.logger_factory import LoggerFactory
from infy_gen_ai_sdk.schema.config_data import BaseLlmProviderConfigData
from infy_gen_ai_sdk.schema.llm_data import BaseLlmRequestData, BaseLlmResponseData
from infy_gen_ai_sdk.llm.interface.i_llm_provider import ILlmProvider
from .tokenizer_service import TokenizerService


class CustomLlmProviderConfigData(BaseLlmProviderConfigData):
    """Domain class"""
    inference_url: str = None
    tiktoken_cache_dir: str = None
    remove_query_from_response: bool = None
    verify_ssl: bool = True


class CustomLlmRequestData(BaseLlmRequestData):
    """Domain class"""


class CustomLlmResponseData(BaseLlmResponseData):
    """Domain class"""


class CustomLlmProvider(ILlmProvider):
    """Open AI LLM provider"""

    def __init__(self, config_data: CustomLlmProviderConfigData, json_payload_dict: dict, custom_llm_name: str) -> None:
        # self.__logger = LoggerFactory().get_logger()
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler(infy_dpp_sdk.common.Constants.FSLH_DPP):
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler(infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()
        else:
            self.__logger = logging.getLogger(__name__)
        self.__model_url = config_data.inference_url
        self.remove_query_from_response = config_data.remove_query_from_response
        self.__tokenizer_ser_obj = TokenizerService(
            config_data.tiktoken_cache_dir)
        self.__json_payload = json_payload_dict
        self.custom_llm_name = custom_llm_name
        self.verify_ssl = config_data.verify_ssl

    def get_llm_response(self, llm_request_data: CustomLlmRequestData) -> CustomLlmResponseData:
        try:
            llm_response_data = CustomLlmResponseData()
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

    def __generate_answer(self, query, context_text, prompt):
        combined_query = prompt.replace(
            '{context}', context_text).replace('{question}', query)
        model_output = self.__invoke_api(combined_query)
        if self.remove_query_from_response:
            answer = self.__remove_query(model_output, combined_query)
            return answer, combined_query
        return model_output, combined_query

    def __invoke_api(self, query):
        url = self.__model_url
        response = ''
        request_id = str(uuid.uuid4())
        token_count = self.__tokenizer_ser_obj.count_tokens(
            query, TokenizerService.ENCODING_P50K_BASE)
        json_payload = self.__json_payload.copy()
        for jp_key, jp_val in json_payload.items():
            if jp_val == "{query}":
                json_payload[jp_key] = query
        try:
            self.__logger.debug("REQUEST %s:%s ", request_id,
                                json.dumps(json_payload, indent=4))
            model_response = requests.post(
                url, json=json_payload, verify=self.verify_ssl, timeout=180)
            if model_response.status_code == 200:
                self.__logger .info(
                    'API call to %s Inference model successfull', self.custom_llm_name)
                ml_model_output = model_response.json()

                if len(ml_model_output) > 0:
                    if isinstance(ml_model_output, list):
                        ml_model_output = ml_model_output[0]
                    self.__logger.debug("RESPONSE %s:%s", request_id, json.dumps(
                        ml_model_output, indent=4))
                    response = ml_model_output['generated_text']
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

    def __remove_query(self, answer, query):
        return answer[len(query):].strip()
