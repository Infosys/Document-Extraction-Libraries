# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for zero short qna strategy provider class"""
import os
from ....data.qna_data import BaseStrategyConfigData, QnaResponseData, QnaData
from ...interface.i_qna_strategy_provider import IQnaStrategyProvider
from ...interface.i_llm_response_parser_provider import ILLMResponseParserProvider
from ....llm.provider.custom_llm_provider import CustomLlmRequestData
from ..llm_response_parser.without_sub_context_res_parser import WithoutSubContextResParserProvider
from ..llm_response_parser.with_sub_context_res_parser import WithSubContextResParserProvider


class ZeroShotPairStrategyConfigData(BaseStrategyConfigData):
    """ Request data for QnA generation """
    que_type: dict
    with_sub_context: bool


class ZeroShotPairStrategyProvider(IQnaStrategyProvider):
    """OpenAI embedding provider"""
    PROMPT_TEMPLATE_TYPE_WITHOUT_SUBCONTEXT = "without_sub_context"
    PROMPT_TEMPLATE_TYPE_WITH_SUBCONTEXT = "with_sub_context"
    __prompt_template_dict = {
        PROMPT_TEMPLATE_TYPE_WITHOUT_SUBCONTEXT: None,
        PROMPT_TEMPLATE_TYPE_WITH_SUBCONTEXT: None
    }

    def __init__(self, strategy_config_data: ZeroShotPairStrategyConfigData, llm_response_parser: ILLMResponseParserProvider = None) -> None:

        self.__que_type_dict = strategy_config_data.que_type
        self.__with_sub_context = strategy_config_data.with_sub_context
        self.__prompt_template_dict[self.PROMPT_TEMPLATE_TYPE_WITHOUT_SUBCONTEXT] = self.__get_prompt_template(
            self.PROMPT_TEMPLATE_TYPE_WITH_SUBCONTEXT)
        self.__prompt_template_dict[self.PROMPT_TEMPLATE_TYPE_WITH_SUBCONTEXT] = self.__get_prompt_template(
            self.PROMPT_TEMPLATE_TYPE_WITH_SUBCONTEXT)
        self.__llm_response_parser = llm_response_parser

    def set_llm_provider(self, providers: dict):
        """Set the LLM provider(s)"""
        self.__llm_provider_dict = providers

    def set_prompt_template(self, prompt_template_dict: dict):
        """Set the prompt template(s)"""
        self.__prompt_template_dict = prompt_template_dict

    def get_prompt_template(self):
        """Get the prompt template(s)"""
        return self.__prompt_template_dict

    def generate_qna(self, context_list: list[str], metadata: dict) -> QnaResponseData:
        """Generate Q&A for the provided text"""
        if self.__with_sub_context:
            qna_response_data = self.__generate_qna_with_subcontext(
                context_list)
        else:
            qna_response_data = self.__generate_qna_without_subcontext(
                context_list)
        return qna_response_data

    def __generate_qna_without_subcontext(self, context_list: list[str]) -> QnaResponseData:
        """Generate Q&A for the provided text"""
        if len(context_list) > 1:
            raise ValueError(
                "The context list should only have one element in it")
        PROMPT_TEMPLATE = self.__prompt_template_dict[self.PROMPT_TEMPLATE_TYPE_WITHOUT_SUBCONTEXT]

        llm_provider = [
            llm_provider for llm_provider in self.__llm_provider_dict.values()][0]
        CONTEXT = context_list[0]

        temp_var_to_value_dict = {
            "context": CONTEXT,
            "que_type_and_count": self.__que_type_dict
        }
        prompt_template = self.fill_template(
            temp_var_to_value_dict, PROMPT_TEMPLATE)

        llm_response = llm_provider.get_llm_response(
            CustomLlmRequestData(
                **{
                    "prompt_template": prompt_template
                }
            ))
        if self.__llm_response_parser:
            qna_response_data = self.__llm_response_parser.parse_llm_response(
                llm_response.llm_response_txt, self.__que_type_dict, CONTEXT)
        else:
            llm_response_parser = WithoutSubContextResParserProvider()
            qna_response_data = llm_response_parser.parse_llm_response(
                llm_response.llm_response_txt, self.__que_type_dict, CONTEXT)
        return qna_response_data

    def __generate_qna_with_subcontext(self, context_list: list[str]) -> QnaResponseData:
        """Generate Q&A for the provided text"""
        if len(context_list) > 1:
            raise ValueError(
                "The context list should only have one element in it")

        PROMPT_TEMPLATE = self.__prompt_template_dict[self.PROMPT_TEMPLATE_TYPE_WITH_SUBCONTEXT]
        llm_provider = [
            llm_provider for llm_provider in self.__llm_provider_dict.values()][0]
        CONTEXT = context_list[0]

        temp_var_to_value_dict = {
            "context": CONTEXT,
            "que_type_and_count": self.__que_type_dict
        }
        prompt_template = self.fill_template(
            temp_var_to_value_dict, PROMPT_TEMPLATE)

        llm_response = llm_provider.get_llm_response(
            CustomLlmRequestData(
                **{
                    "prompt_template": prompt_template
                }
            ))
        if self.__llm_response_parser:
            qna_response_data = self.__llm_response_parser.parse_llm_response(
                llm_response.llm_response_txt, self.__que_type_dict, CONTEXT)
        else:
            llm_response_parser = WithSubContextResParserProvider()
            qna_response_data = llm_response_parser.parse_llm_response(
                llm_response.llm_response_txt,  self.__que_type_dict, CONTEXT)

        return qna_response_data

    def __get_prompt_template(self, prompt_type) -> str:
        """Return prompt template without sub context"""
        prompt_template = ""
        if prompt_type == self.PROMPT_TEMPLATE_TYPE_WITHOUT_SUBCONTEXT:
            # Construct the path to the custom_llm_prompt.txt file
            prompt_file_path = os.path.join(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(__file__)))), 'config', 'custom_llm_prompt.txt')
        else:
            # Construct the path to the openai_prompt.txt file
            prompt_file_path = os.path.join(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(__file__)))), 'config', 'openai_prompt.txt')

        # Open and read the prompt file
        with open(prompt_file_path, 'r', encoding='utf-8') as file:
            prompt_template = file.read()
        return prompt_template
