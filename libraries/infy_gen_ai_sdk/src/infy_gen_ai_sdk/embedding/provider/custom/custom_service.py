# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import logging
from typing import List
import requests

import infy_fs_utils
from ....common.singleton import Singleton
from ....common import Constants


class CustomService(metaclass=Singleton):
    """Wrapper class for Custom Embedding Provider"""

    def __init__(self, api_key: str, endpoint: str = None) -> None:
        if not endpoint:
            raise ValueError(
                'Endpoint should be provided')
        self.__api_key = api_key
        self.__endpoint = endpoint

    def generate_embedding(self, text) -> dict:
        """Generate embedding for given text using Custom Embedding Provider"""
        if self.__endpoint:
            result = self.__call_remote(text)
        return result

    def __call_remote(self, text: str) -> List[float]:
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler():
            __logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler().get_logger()
        else:
            __logger = logging.getLogger(__name__)

        result = {
            'embedding': [],
            'size': 0,
            'error_message': None
        }

        headers = {
            'Content-Type': 'application/json',
        }

        data_raw = {
            'inputs': [text]
        }
        try:
            response = requests.post(
                self.__endpoint, headers=headers, json=data_raw, timeout=120, verify=False)
            if response.status_code == 200:
                content = json.loads(response.content.decode("utf-8"))
                result['embedding'] = content[0]
                result['size'] = len(content[0])
            else:
                message = f'Error in calling API {response.status_code}'
                result['error_message'] = message
                __logger.error(message)
        except Exception as ex:
            message = f'Error occurred while calling API. Error: {str(ex)}'
            result['error_message'] = message
            __logger.exception(message)
        return result
