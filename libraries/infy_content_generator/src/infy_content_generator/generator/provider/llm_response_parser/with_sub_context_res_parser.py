# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for without subcontext response parser provider class"""
from ...interface.i_llm_response_parser_provider import ILLMResponseParserProvider
from ....data.qna_data import QnaData, QnaResponseData


class WithSubContextResParserProvider(ILLMResponseParserProvider):
    """Class for withsubcontext response parser provider"""

    def __init__(self):
        pass

    def parse_llm_response(self, llm_response_txt, input_que_type: dict, context: str) -> QnaResponseData:
        """Parse the LLM response and return a QnaData """
        q_type_list = [
            q_type_key for q_type_key in input_que_type.keys()]
        # Split the input string into blocks
        blocks = llm_response_txt.strip().split('\n\n')

        # Initialize an empty list to hold the Q&A data
        qna_list = []

        # Process each block
        for block in blocks:
            lines = block.split('\n')
            if len(lines) < 4:
                continue
            question = lines[0].replace('QUESTION: ', '').strip()
            answer = lines[1].replace('ANSWER: ', '').strip()
            q_type = lines[2].replace('TYPE: ', '').strip()
            source = lines[3].replace('SOURCE: ', '').strip()

            # Matching the case of q_type
            for q_type_key in q_type_list:
                if q_type_key.lower() == q_type.lower():
                    q_type = q_type_key
                    break
            # Construct a dictionary for the current Q&A block
            qna_dict = QnaData(**{
                'type': q_type,
                'question': question,
                'answer': answer,
                'answer_source': source
            })

            # Append the dictionary to the list
            qna_list.append(qna_dict)

        qna_response_data = QnaResponseData(
            qna_data_list=qna_list)
        return qna_response_data
