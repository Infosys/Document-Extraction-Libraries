# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Llama LLM provider"""
from infy_gen_ai_sdk.common.logger_factory import LoggerFactory
from infy_gen_ai_sdk.data.config_data import BaseLlmProviderConfigData
from infy_gen_ai_sdk.data.llm_data import BaseLlmRequestData, BaseLlmResponseData
from infy_gen_ai_sdk.llm.interface.i_llm_provider import ILlmProvider
from .tokenizer_service import TokenizerService
import requests
import json


class Llama27bLlmProviderConfigData(BaseLlmProviderConfigData):
    """Domain class"""
    inference_url:str = None
    max_new_tokens: int = None
    tiktoken_cache_dir: str = None
    temperature:int = None


class Llama27bLlmRequestData(BaseLlmRequestData):
    """Domain class"""


class Llama27bLlmResponseData(BaseLlmResponseData):
    """Domain class"""


class Llama27bLlmProvider(ILlmProvider):
    """Open AI LLM provider"""

    def __init__(self, config_data: Llama27bLlmProviderConfigData) -> None:
        self.__logger = LoggerFactory().get_logger()        
        self.__model_url = config_data.inference_url
        self.__max_new_tokens = config_data.max_new_tokens
        self.__tokenizer_ser_obj = TokenizerService(config_data.tiktoken_cache_dir)
        self.__temperature=config_data.temperature
        # if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler(infy_dpp_sdk.common.Constants.FSLH_DPP):
        #     self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
        #     ).get_fs_logging_handler(infy_dpp_sdk.common.Constants.FSLH_DPP).get_logger()        

    def get_llm_response(self, llm_request_data: Llama27bLlmRequestData) -> Llama27bLlmResponseData:
        try:
            llm_response_data = Llama27bLlmResponseData()            
            combined_text = llm_request_data.template_var_to_value_dict.get('context')
            query=llm_request_data.template_var_to_value_dict.get('question')
            template=llm_request_data.prompt_template
            llm_response_data.llm_response_txt,llm_response_data.llm_request_txt = self.__generate_answer(query,combined_text,template)
            
        except Exception as e:
            self.__logger.exception(e)
            raise e
        return llm_response_data
    def __generate_answer(self,query,context_text,prompt):
        combined_query = prompt.replace('{context}',context_text).replace('{question}',query)
        model_output = self.__invoke_api(combined_query)
        answer = self.__remove_query(model_output, combined_query)
        return answer,combined_query

    def __invoke_api(self, query):
        url = self.__model_url
        response = ''
        # Set the JSON payload data as a Python dictionary
        token_count = self.__tokenizer_ser_obj.count_tokens(query,TokenizerService.ENCODING_P50K_BASE)
        json_payload = {
            "inputs": query,
            "parameters": { 
                "max_new_tokens": self.__max_new_tokens-token_count,
                "temperature":  self.__temperature, 
                "num_return_sequences":1, 
                "do_sample": True 
            }
        }
        try:
            self.__logger.debug(json.dumps(json_payload,indent=4))
            model_response = requests.post(url, json=json_payload, verify=False,timeout=180)
            if model_response.status_code==200:
                self.__logger .info(f'API call to Ollama Inference model successfull')
                if len(model_response.json())>0:
                    response = model_response.json()[0]['generated_text']
                    if response:
                        self.__logger .info('Model answer has been detected')
                    else:
                        raise Exception("Model has given empty responses")    
            else:
                raise Exception(f'Error in calling API {model_response.status_code}')    
        except Exception as e:
            self.__logger .error(f'Error in calling API {e}')
        return response

    def __remove_query(self,answer, query):
        return answer[len(query):].strip()