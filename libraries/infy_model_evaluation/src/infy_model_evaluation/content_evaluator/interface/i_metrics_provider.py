# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for embedding provider interface class"""

import abc
from typing import List
from ...data.content_evaluator_data import (
    ContentEvaluatorReqData, MetricsData)
from ...data.llm_data import LLMConfigData


class IMetricsProvider(metaclass=abc.ABCMeta):
    """Interface class for question answer generation provider"""

    def __init__(self, prompt_template_dict: dict):
        self.__prompt_template_dict = prompt_template_dict

    @abc.abstractmethod
    def calculate_metrics(self, content_evaluator_req_data: ContentEvaluatorReqData) -> MetricsData:
        """Evaluate the content and return the metrics based on model used"""
        raise NotImplementedError

    @abc.abstractmethod
    def set_llm_provider(self, llm_config_data_list: List[LLMConfigData]):
        """Set the LLM provider(s)"""
        raise NotImplementedError

    def get_prompt_template_dict(self) -> dict:
        """Get the prompt templates for the metrics"""
        # dict with name and prompt template content
        return self.__prompt_template_dict.copy()

    def set_prompt_template_dict(self, prompt_template_dict: dict):
        """Set the prompt templates for the metrics"""
        #  validation for extra keys in prompt_template_dict
        #  and raise exception if any extra key is present
        metrics_keys = set(self.__prompt_template_dict.keys())
        new_keys = set(prompt_template_dict.keys())
        if not new_keys.issubset(metrics_keys):
            print(f"ERROR: Invalid keys present in {prompt_template_dict}")
            raise Exception(f"Invalid keys present in {prompt_template_dict}")
        else:
            self.__prompt_template_dict.update(prompt_template_dict.copy())
