# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for two stage qna strategy provider class"""
import os
from ....data.qna_data import BaseStrategyConfigData, QnaResponseData, QnaData
from ...interface.i_qna_strategy_provider import IQnaStrategyProvider
from ...interface.i_llm_response_parser_provider import ILLMResponseParserProvider
from ....llm.provider.chat_llm_provider import ChatLlmRequestData
from ..llm_response_parser.two_stage_question_parser import TwoStageQuestionResParserProvider


class TwoStageStrategyConfigData(BaseStrategyConfigData):
    """ Request data for QnA generation """
    que_type: dict


class TwoStageStrategyProvider(IQnaStrategyProvider):
    PROMPT_TEMPLATE_TYPE_QUESTION = "question"
    PROMPT_TEMPLATE_TYPE_ANSWER = "answer"
    __prompt_template_dict = {
        PROMPT_TEMPLATE_TYPE_QUESTION: None,
        PROMPT_TEMPLATE_TYPE_ANSWER: None
    }

    def __init__(self, strategy_config_data: TwoStageStrategyConfigData,
                 llm_response_parser: ILLMResponseParserProvider = None) -> None:

        self.__que_type_dict = strategy_config_data.que_type
        self.__prompt_template_dict[self.PROMPT_TEMPLATE_TYPE_QUESTION] = self.__get_prompt_template(
            self.PROMPT_TEMPLATE_TYPE_QUESTION)
        self.__prompt_template_dict[self.PROMPT_TEMPLATE_TYPE_ANSWER] = self.__get_prompt_template(
            self.PROMPT_TEMPLATE_TYPE_ANSWER)
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

    def generate_qna(self, context_list: list[str],  metadata: dict) -> QnaResponseData:
        """Generate Q&A for the provided text"""
        questions_data = self.__generate_questions(context_list, metadata)
        qna_data = self.__generate_answers(questions_data)

        qna_data = [QnaData(**{
            "type": qna_data['type'][i],
            "question": qna_data['question'][i],
            "answer": qna_data['answer'][i],
            "answer_source": qna_data['answer_source'][i],
            # "context":qna_data['context'][i],
        }) for i in range(len(qna_data['question']))
        ]
        return QnaResponseData(qna_data_list=qna_data)

    def __generate_questions(self, context_list: list[str], metadata: dict) -> dict:
        """Generate questions based on the context"""
        if len(context_list) > 1:
            raise ValueError(
                "The context list should only have one element in it")

        PROMPT_TEMPLATE = self.__prompt_template_dict[self.PROMPT_TEMPLATE_TYPE_QUESTION]
        llm_provider = list(self.__llm_provider_dict.values())[0]
        CONTEXT = context_list[0]

        temp_var_to_value_dict = {
            "context": CONTEXT,
            "que_type_and_count": self.__que_type_dict,
            "step": "question",
            "metadata": metadata
        }
        prompt_template = self.__fill_template(
            temp_var_to_value_dict, PROMPT_TEMPLATE)

        llm_response = llm_provider.get_llm_response(
            ChatLlmRequestData(
                **{
                    "prompt_template": prompt_template
                }
            ))

        if self.__llm_response_parser:
            questions_data = self.__llm_response_parser.parse_llm_response(
                llm_response.llm_response_txt, self.__que_type_dict, CONTEXT)
        else:
            llm_response_parser = TwoStageQuestionResParserProvider()
            questions_data = llm_response_parser.parse_llm_response(
                llm_response.llm_response_txt, self.__que_type_dict, CONTEXT)

        return questions_data

    def __generate_answers(self, questions_data: dict) -> dict:
        """Generate answers for the questions"""
        PROMPT_TEMPLATE = self.__prompt_template_dict[self.PROMPT_TEMPLATE_TYPE_ANSWER]
        llm_provider = list(self.__llm_provider_dict.values())[1]

        answers = []
        for question, context in zip(questions_data['question'], questions_data['answer_source']):

            temp_var_to_value_dict = {
                "context": context,
                "question": question,
                "step": "answer",
            }

            prompt_template = self.__fill_template(
                temp_var_to_value_dict, PROMPT_TEMPLATE)

            llm_response = llm_provider.get_llm_response(
                ChatLlmRequestData(
                    **{
                        "prompt_template": prompt_template,
                    }
                ))

            answer = llm_response.llm_response_txt.strip()
            answers.append(answer)

        questions_data['answer'] = answers
        return questions_data

    def __fill_template(self, temp_var_to_value_dict: dict, template: str) -> str:
        """Fill the template with the provided values"""

        step = temp_var_to_value_dict.get('step')
        if step == "question":
            __context = temp_var_to_value_dict.get('context')
            __que_type_dict = temp_var_to_value_dict.get('que_type_and_count')
            metadata_dict = temp_var_to_value_dict.get('metadata', None)
            __que_count = 0
            __que_type = ""
            if __que_type_dict:
                for key in __que_type_dict:
                    if __que_type_dict[key]['count'] > 0:
                        __que_count += __que_type_dict[key]['count']
                        if __que_type != "":
                            __que_type += ", "
                        __que_type += key

            # if not any(metadata_dict.values()):
            #     metadata_dict = None

            prompt_template = template.replace(
                '{context}', __context).replace(
                '{question_type}', __que_type).replace(
                '{question_count}', str(__que_count)).replace('{metadata}', str(metadata_dict))

            return prompt_template

        elif step == "answer":
            __context = temp_var_to_value_dict.get('context')
            __question = temp_var_to_value_dict.get('question')
            prompt_template = template.replace(
                '{context}', __context).replace('{question}', __question)

            return prompt_template

    def __get_prompt_template(self, prompt_type) -> str:
        """Return prompt template"""
        prompt_file_name = f'{prompt_type}_prompt.txt'
        prompt_file_path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(__file__)))), 'config', prompt_file_name)

        with open(prompt_file_path, 'r', encoding='utf-8') as file:
            prompt_template = file.read()
        return prompt_template
