# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for two stage question response parser provider class"""
import re
from ...interface.i_llm_response_parser_provider import ILLMResponseParserProvider


class TwoStageQuestionResParserProvider(ILLMResponseParserProvider):
    """Class for two stage question response parser provider"""

    def __init__(self):
        pass

    def parse_llm_response(self, llm_response_txt, input_que_type: dict, context: str) -> dict:
        """Parse the LLM response and return a questions_data """
        questions = re.split(r'Q\d+:', llm_response_txt)[1:]  # Skip the first empty element
        questions_data = {'question': [], 'type': [], 'answer_source': []}

        for q in questions:
            # Extract question text
            question = q.strip().split('Type:')[0].strip()

            # Extract type
            type_match = re.search(r'Type:\s*(\w+)', q)
            q_type = type_match.group(1) if type_match else None

            # Extract context support
            # support_match = re.search(
            # r'Support:\s*(.*?)(?=Q\d+:|$)', q, re.DOTALL)
            # support = support_match.group(1).strip() if support_match else None

            # Only add to result if none of the elements are None
            if question and q_type:
                questions_data['question'].append(question)
                questions_data['type'].append(q_type)
                # questions_data['answer_source'].append(support)

        questions_data['answer_source'].extend([context] * len(questions_data['question']))
        return questions_data
