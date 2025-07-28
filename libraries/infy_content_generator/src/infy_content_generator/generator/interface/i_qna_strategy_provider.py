# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for embedding provider interface class"""

import abc
from ...data.qna_data import QnaResponseData


class IQnaStrategyProvider(metaclass=abc.ABCMeta):
    """Interface class for question answer generation provider"""

    @abc.abstractmethod
    def set_llm_provider(self, providers: dict):
        """Set the LLM provider(s)"""
        raise NotImplementedError

    @abc.abstractmethod
    def set_prompt_template(self, prompt_template_dict: dict):
        """Set the prompt template(s)"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_prompt_template(self):
        """Get the prompt template(s)"""
        raise NotImplementedError

    @abc.abstractmethod
    def generate_qna(self, context_list:  list[str], metadata: dict = None) -> QnaResponseData:
        """Generate Q&A for the provided text"""
        raise NotImplementedError

    def fill_template(self, temp_var_to_value_dict: dict, PROMPT_TEMPLATE: str) -> str:
        """Fill the prompt template with the values"""
        CONTEXT = temp_var_to_value_dict["context"]
        que_type_and_count_dict = temp_var_to_value_dict["que_type_and_count"]

        _prompt_template = PROMPT_TEMPLATE.replace('{context}', CONTEXT)
        que_type_and_count_list = []
        if que_type_and_count_dict:
            for que_type_key, que_type_prop in que_type_and_count_dict.items():
                if que_type_prop.get('count') > 0:
                    que_type_and_count_list.append(
                        que_type_key + ' - ' + str(que_type_prop.get('count')))
        que_type_and_count_str = '\n'.join(que_type_and_count_list)
        if que_type_and_count_str:
            _prompt_template = _prompt_template.replace(
                '{que_type_and_count}', que_type_and_count_str)
        else:
            _prompt_template = _prompt_template.replace(
                '{que_type_and_count}', 'any - 3')

        return _prompt_template
