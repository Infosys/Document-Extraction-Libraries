# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import time
import json
import logging
from typing import List
import requests
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    # Ignore optional dependency load error
    pass

import infy_fs_utils
from ....common.singleton import Singleton
from ....common import Constants


class StService(metaclass=Singleton):
    """Wrapper class for Sentence Transformer library"""

    def __init__(self, model_name: str, model_home_path: str = None, base_url: str = None) -> None:
        if not model_home_path and not base_url:
            raise ValueError(
                'Either model_home_path or base_url should be provided')
        self.__base_url = base_url
        model_to_obj_dict = {}
        overall_elapsed_time = 0
        if model_name and model_home_path:
            start_time = time.time()
            model_path = model_home_path+'/'+model_name
            model_to_obj_dict[model_name] = SentenceTransformer(model_path)
            elapsed_time = round(time.time() - start_time, 3)
            print(f'Load time for model {model_name}: {elapsed_time} secs')
            overall_elapsed_time += elapsed_time
        self.__model_to_obj_dict = model_to_obj_dict

    def generate_embedding(self, text, model_name) -> dict:
        """Generate embedding for given text using Sentence Transformer model"""
        if self.__base_url:
            result = self.__call_remote(text, model_name)
        else:
            result = self.__call_local(text, model_name)
        return result

    def __call_local(self, text: str, model_name: str) -> dict:
        result = {
            'embedding': [],
            'size': 0,
            'error_message': None,
            'model_name': model_name
        }
        model_obj = self.__model_to_obj_dict.get(model_name, None)
        if not model_obj:
            result['error_message'] = f'Model not found: {model_name}'
        else:
            embedding_as_numpy = model_obj.encode(text)
            embedding_as_list = embedding_as_numpy.astype(float).tolist()
            result['embedding'] = embedding_as_list
            result['size'] = len(embedding_as_list)

        return result

    def __call_remote(self, text: str, model_name: str) -> List[float]:
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler(
                Constants.FSLH_GEN_AI_SDK):
            __logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler(Constants.FSLH_GEN_AI_SDK).get_logger()
        else:
            __logger = logging.getLogger(__name__)

        result = {
            'embedding': [],
            'size': 0,
            'error_message': None,
            'model_name': model_name
        }

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        json_data = {
            'text': text,
            'modelName': model_name
        }
        try:
            response = requests.post(
                self.__base_url, headers=headers, json=json_data, timeout=120)
            if response.status_code == 200:
                content = json.loads(response.content.decode("utf-8"))
                if content.get('responseCde') == 0:
                    content_response = content.get('response')
                    result['embedding'] = content_response.get('embedding')
                    result['size'] = content_response.get('size')
                else:
                    result['error_message'] = f'Error in API response {content.get("responseMsg")}'

            else:
                message = f'Error in calling API {response.status_code}'
                result['error_message'] = message
                __logger.error(message)
        except Exception as ex:
            message = f'Error occurred while calling API. Error: {str(ex)}'
            result['error_message'] = message
            __logger.exception(message)
        return result
