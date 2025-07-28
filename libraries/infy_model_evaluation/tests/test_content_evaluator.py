# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Testing module"""

import os
import time
import json
import pytest
import pandas as pd
import infy_model_evaluation
import infy_gen_ai_sdk
from infy_model_evaluation.common.file_util import FileUtil


@pytest.fixture(scope='module', autouse=True)
def setup() -> str:
    """Initialization method"""
    pass


def test_eval_qna_truthdata_racar(setup):
    """This is a qna evaluation Test method"""

    content_evaluator_req_data = infy_model_evaluation.data.ContentEvaluatorReqData(
        **{
            "question": "What is the iconic tower in Paris that was built for the 1889 World’s Fair?",
            "contexts": "Paris, often referred to as the City of Light, is celebrated for its rich history and cultural heritage. The Eiffel Tower, an iconic symbol, attracts millions of visitors each year with its breathtaking views and romantic allure. The city is also home to the stunning Notre-Dame Cathedral, a masterpiece of Gothic architecture that has stood for centuries. With its charming streets, world-class museums like the Louvre, and vibrant café culture, Paris offers an enchanting experience for everyone. The Seine River, winding through the city, adds to its timeless beauty, making it a dream destination for travelers worldwide.",
            "answer": "Eiffel."
        }
    )
    llm_provider = infy_model_evaluation.llm.provider.OpenAILlmProvider(
        infy_model_evaluation.llm.provider.OpenAILlmProviderConfigData(
            **{
                "api_type": "azure",
                "api_url": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
                "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
                "api_version": "2024-02-15-preview",
                "model_name": "gpt-4",
                "deployment_name": "gpt4",
                "max_tokens": 300,
                'temperature': 0.1,
                "is_chat_model": True,
                "top_p": 0.95,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "stop": None
            })
    )
    llm_res_parser_obj = infy_model_evaluation.llm.provider.JSONResponseParser()
    llm_provider_data = infy_model_evaluation.data.llm_data.LLMProvidersData(**{
        "llm_provider_obj": llm_provider,
        "llm_res_parser_obj": llm_res_parser_obj
    })

    llm_config_data_list = [infy_model_evaluation.data.llm_data.LLMConfigData(
        __root__={"openai_llm_provider": llm_provider_data})]

    metric_provider_obj1 = infy_model_evaluation.content_evaluator.RACARProvider(
        llm_config_data_list)

    metric_provider_obj_list = [metric_provider_obj1]
    qna_evaluator_obj = infy_model_evaluation.content_evaluator.QnaEvaluator(
        metric_provider_obj_list)
    response_metrics_data = qna_evaluator_obj.evaluate(
        content_evaluator_req_data)
    print(response_metrics_data.json())
    output_file_path = f"C:/temp/{os.path.basename(os.path.dirname(__file__))}/qna_metrics_racar.json"
    FileUtil.create_dirs_if_absent(os.path.dirname(output_file_path))
    FileUtil.write_to_file(
        json.dumps(response_metrics_data.dict().get("metrics")), output_file_path)


def test_eval_qna_truthdata_racar_3(setup):
    """This is a qna evaluation Test method to demonstrate modification of the prompt template dict"""

    content_evaluator_req_data = infy_model_evaluation.data.ContentEvaluatorReqData(
        **{
            "question": "What is the iconic tower in Paris that was built for the 1889 World’s Fair?",
            "contexts": "Paris, often referred to as the City of Light, is celebrated for its rich history and cultural heritage. The Eiffel Tower, an iconic symbol, attracts millions of visitors each year with its breathtaking views and romantic allure. The city is also home to the stunning Notre-Dame Cathedral, a masterpiece of Gothic architecture that has stood for centuries. With its charming streets, world-class museums like the Louvre, and vibrant café culture, Paris offers an enchanting experience for everyone. The Seine River, winding through the city, adds to its timeless beauty, making it a dream destination for travelers worldwide.",
            "answer": "Eiffel."
        }
    )
    llm_provider = infy_model_evaluation.llm.provider.OpenAILlmProvider(
        infy_model_evaluation.llm.provider.OpenAILlmProviderConfigData(
            **{
                "api_type": "azure",
                "api_url": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
                "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
                "api_version": "2024-02-15-preview",
                "model_name": "gpt-4",
                "deployment_name": "gpt4",
                "max_tokens": 1000,
                'temperature': 0.1,
                "is_chat_model": True,
                "top_p": 0.95,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "stop": None
            })
    )
    llm_res_parser_obj = infy_model_evaluation.llm.provider.JSONResponseParser()
    llm_provider_data = infy_model_evaluation.data.llm_data.LLMProvidersData(**{
        "llm_provider_obj": llm_provider,
        "llm_res_parser_obj": llm_res_parser_obj
    })

    llm_config_data_list = [infy_model_evaluation.data.llm_data.LLMConfigData(
        __root__={"openai_llm_provider": llm_provider_data})]

    # prompt_file_dir_path = f"{os.path.dirname(os.path.dirname(__file__))}/data/sample/config/prompt_templates/racar_prompts"
    metric_provider_obj1 = infy_model_evaluation.content_evaluator.RACARProvider(
        llm_config_data_list)
    prompt_template_dict = metric_provider_obj1.get_prompt_template_dict()
    print(json.dumps(prompt_template_dict, indent=4))
    # Template changed to 10-12 just to test custom prompt in prompt_template_dict
    PROMPT_AGNOSTICISM = """
    Given a context and question, evaluate how much the question relies on specific context details versus requiring analytical thinking and external knowledge. Return a score from 10-12, where:
    - Score 10: Highly context-dependent, requires specific details from the context
    - Score 11: Requires both context and basic analytical thinking/background knowledge
    - Score 12: Requires comprehensive understanding and significant analytical thinking

    For example, questions asking about specific details mentioned in the context should receive a score of 10. Questions requiring interpretation of context information should receive a score of 11. Questions requiring synthesis of context with broader knowledge should receive a score of 12.

    context: {context}
    question: {question}
    Output: [score]
    """
    prompt_template_dict["agnosticism"] = PROMPT_AGNOSTICISM
    metric_provider_obj1.set_prompt_template_dict(prompt_template_dict)
    metric_provider_obj_list = [metric_provider_obj1]
    qna_evaluator_obj = infy_model_evaluation.content_evaluator.QnaEvaluator(
        metric_provider_obj_list)
    response_metrics_data = qna_evaluator_obj.evaluate(
        content_evaluator_req_data)
    print(response_metrics_data.json())
    output_file_path = f"C:/temp/{os.path.basename(os.path.dirname(__file__))}/qna_metrics_racar_3.json"
    FileUtil.create_dirs_if_absent(os.path.dirname(output_file_path))
    FileUtil.write_to_file(
        json.dumps(response_metrics_data.dict().get("metrics")), output_file_path)


def test_eval_qna_truthdata_qaeval(setup):
    """This is a qna evaluation Test method"""

    content_evaluator_req_data = infy_model_evaluation.data.ContentEvaluatorReqData(
        **{
            "question": "What is the iconic tower in Paris that was built for the 1889 World’s Fair?",
            "contexts": "Paris, often referred to as the City of Light, is celebrated for its rich history and cultural heritage. The Eiffel Tower, an iconic symbol, attracts millions of visitors each year with its breathtaking views and romantic allure. The city is also home to the stunning Notre-Dame Cathedral, a masterpiece of Gothic architecture that has stood for centuries. With its charming streets, world-class museums like the Louvre, and vibrant café culture, Paris offers an enchanting experience for everyone. The Seine River, winding through the city, adds to its timeless beauty, making it a dream destination for travelers worldwide.",
            "answer": "Eiffel."
        }
    )
    llm_provider = infy_model_evaluation.llm.provider.OpenAILlmProvider(
        infy_model_evaluation.llm.provider.OpenAILlmProviderConfigData(
            **{
                "api_type": "azure",
                "api_url": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
                "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
                "api_version": "2024-02-15-preview",
                "model_name": "gpt-4",
                "deployment_name": "gpt4",
                "max_tokens": 1000,
                'temperature': 0.1,
                "is_chat_model": True,
                "top_p": 0.95,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "stop": None
            })
    )

    llm_res_parser_obj = infy_model_evaluation.llm.provider.JSONResponseParser()
    llm_provider_data = infy_model_evaluation.data.llm_data.LLMProvidersData(**{
        "llm_provider_obj": llm_provider,
        "llm_res_parser_obj": llm_res_parser_obj
    })

    llm_config_data_list = [infy_model_evaluation.data.llm_data.LLMConfigData(
        __root__={"openai_llm_provider": llm_provider_data})]

    metric_provider_obj1 = infy_model_evaluation.content_evaluator.QAEvalProvider(
        llm_config_data_list)
    print(json.dumps(metric_provider_obj1.get_prompt_template_dict(), indent=4))
    metric_provider_obj_list = [metric_provider_obj1,]
    qna_evaluator_obj = infy_model_evaluation.content_evaluator.QnaEvaluator(
        metric_provider_obj_list)
    response_metrics_data = qna_evaluator_obj.evaluate(
        content_evaluator_req_data)
    print(response_metrics_data.json())


def test_eval_qna_truthdata_qaeval_3(setup):
    """This is a qna evaluation Test method to demonstrate modification of the prompt template dict"""

    content_evaluator_req_data = infy_model_evaluation.data.ContentEvaluatorReqData(
        **{
            "question": "What is the iconic tower in Paris that was built for the 1889 World’s Fair?",
            "contexts": "Paris, often referred to as the City of Light, is celebrated for its rich history and cultural heritage. The Eiffel Tower, an iconic symbol, attracts millions of visitors each year with its breathtaking views and romantic allure. The city is also home to the stunning Notre-Dame Cathedral, a masterpiece of Gothic architecture that has stood for centuries. With its charming streets, world-class museums like the Louvre, and vibrant café culture, Paris offers an enchanting experience for everyone. The Seine River, winding through the city, adds to its timeless beauty, making it a dream destination for travelers worldwide.",
            "answer": "Eiffel."
        }
    )
    llm_provider = infy_model_evaluation.llm.provider.OpenAILlmProvider(
        infy_model_evaluation.llm.provider.OpenAILlmProviderConfigData(
            **{
                "api_type": "azure",
                "api_url": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
                "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
                "api_version": "2024-02-15-preview",
                "model_name": "gpt-4",
                "deployment_name": "gpt4",
                "max_tokens": 1000,
                'temperature': 0.1,
                "is_chat_model": True,
                "top_p": 0.95,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "stop": None
            })
    )
    llm_res_parser_obj = infy_model_evaluation.llm.provider.JSONResponseParser()

    llm_provider_data = infy_model_evaluation.data.llm_data.LLMProvidersData(**{
        "llm_provider_obj": llm_provider,
        "llm_res_parser_obj": llm_res_parser_obj
    })

    llm_config_data_list = [infy_model_evaluation.data.llm_data.LLMConfigData(
        __root__={"openai_llm_provider": llm_provider_data})]

    metric_provider_obj1 = infy_model_evaluation.content_evaluator.QAEvalProvider(
        llm_config_data_list)
    print(json.dumps(metric_provider_obj1.get_prompt_template_dict(), indent=4))
    prompt_template_dict = metric_provider_obj1.get_prompt_template_dict()
    # Template changed to 10-12 just to test custom prompt in prompt_template_dict
    PROMPT_REASONING = """
        To what extent does the question require reasoning or knowledge beyond the given context?

        context: {context}
        question: {question}

        Rate on a scale of 10-12 where:
        10: Question does not require any reasoning or specialized knowledge to answer - can be answered directly from context or surface-level information.
        11: Question requires basic logical thought process to connect a few elements from the context.
        12: Question requires significant logical or mathematical reasoning / domain knowledge to formulate an appropriate answer.

        OUTPUT REQUIREMENTS:
        Return a JSON object with exactly two fields: 'score' and 'reasons'
        The 'score' field must be an integer between 10-12
        The 'reasons' field must explain why this specific score was assigned
        Your entire response must be valid JSON

        Example output format:
        {
            "score": 10,
            "reasons": "The question can be answered directly from the context without any additional reasoning or knowledge. The answer is straightforward and does not require any logical thought process."
        }
        """
    prompt_template_dict["reasoning_depth"] = PROMPT_REASONING
    metric_provider_obj1.set_prompt_template_dict(prompt_template_dict)
    metric_provider_obj_list = [metric_provider_obj1]
    qna_evaluator_obj = infy_model_evaluation.content_evaluator.QnaEvaluator(
        metric_provider_obj_list)
    response_metrics_data = qna_evaluator_obj.evaluate(
        content_evaluator_req_data)
    print(response_metrics_data.json())
    output_file_path = f"C:/temp/{os.path.basename(os.path.dirname(__file__))}/qna_metrics_qaeval_3.json"
    FileUtil.create_dirs_if_absent(os.path.dirname(output_file_path))
    FileUtil.write_to_file(
        json.dumps(response_metrics_data.dict().get("metrics"), indent=4), output_file_path)


def test_eval_qna_truthdata_racar_2(setup):
    """This Test method is for qna evaluation from xlsx file"""
    response_metrics_data_list = []
    qna_xlsx_file_path = f"{os.path.dirname(os.path.dirname(__file__))}/data/sample/input/question_data.xlsx"
    # Read the Excel file
    df = pd.read_excel(qna_xlsx_file_path)
    # Loops through each row and pass required columns
    for index, row in df.iterrows():
        q_no = row['Q_No']
        question = row['Question']
        answer = row['Ground_Truth']
        contexts = row['Answer_source']
        content_evaluator_req_data = infy_model_evaluation.data.ContentEvaluatorReqData(
            **{
                "question": question,
                "contexts": contexts,
                "answer": answer
            }
        )
        llm_provider = infy_model_evaluation.llm.provider.OpenAILlmProvider(
            infy_model_evaluation.llm.provider.OpenAILlmProviderConfigData(
                **{
                    "api_type": "azure",
                    "api_url": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
                    "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
                    "api_version": "2024-02-15-preview",
                    "model_name": "gpt-4",
                    "deployment_name": "gpt4",
                    "max_tokens": 300,
                    'temperature': 0.1,
                    "is_chat_model": True,
                    "top_p": 0.95,
                    "frequency_penalty": 0,
                    "presence_penalty": 0,
                    "stop": None
                })
        )
        llm_res_parser_obj = infy_model_evaluation.llm.provider.JSONResponseParser()
        llm_provider_data = infy_model_evaluation.data.llm_data.LLMProvidersData(**{
            "llm_provider_obj": llm_provider,
            "llm_res_parser_obj": llm_res_parser_obj
        })

        llm_config_data_list = [infy_model_evaluation.data.llm_data.LLMConfigData(
            __root__={"openai_llm_provider": llm_provider_data})]

        metric_provider_obj1 = infy_model_evaluation.content_evaluator.RACARProvider(
            llm_config_data_list)

        metric_provider_obj_list = [metric_provider_obj1,]
        qna_evaluator_obj = infy_model_evaluation.content_evaluator.QnaEvaluator(
            metric_provider_obj_list)
        response_metrics_data = qna_evaluator_obj.evaluate(
            content_evaluator_req_data)
        response_metrics_data_dict = response_metrics_data.dict().get("metrics")
        response_metrics_data_dict['Q_No'] = q_no
        response_metrics_data_list.append(response_metrics_data_dict)
    output_file_path = f"C:/temp/{os.path.basename(os.path.dirname(__file__))}/qna_metrics_racar_2.json"
    FileUtil.create_dirs_if_absent(os.path.dirname(output_file_path))
    FileUtil.write_to_file(
        json.dumps(response_metrics_data_list, indent=4), output_file_path)


def test_eval_qna_truthdata_qaeval_2(setup):
    """This Test method is for qna evaluation from xlsx file"""
    response_metrics_data_list = []
    qna_xlsx_file_path = f"{os.path.dirname(os.path.dirname(__file__))}/data/sample/input/question_data.xlsx"
    # Read the Excel file
    df = pd.read_excel(qna_xlsx_file_path)
    # Loops through each row and pass required columns
    for index, row in df.iterrows():
        q_no = row['Q_No']
        question = row['Question']
        answer = row['Ground_Truth']
        contexts = row['Answer_source']
        content_evaluator_req_data = infy_model_evaluation.data.ContentEvaluatorReqData(
            **{
                "question": question,
                "contexts": contexts,
                "answer": answer
            }
        )
        llm_provider = infy_model_evaluation.llm.provider.OpenAILlmProvider(
            infy_model_evaluation.llm.provider.OpenAILlmProviderConfigData(
                **{
                    "api_type": "azure",
                    "api_url": os.environ['AZURE_OPENAI_SERVER_BASE_URL'],
                    "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
                    "api_version": "2024-02-15-preview",
                    "model_name": "gpt-4",
                    "deployment_name": "gpt4",
                    "max_tokens": 300,
                    'temperature': 0.1,
                    "is_chat_model": True,
                    "top_p": 0.95,
                    "frequency_penalty": 0,
                    "presence_penalty": 0,
                    "stop": None
                })
        )
        llm_res_parser_obj = None
        llm_provider_data = infy_model_evaluation.data.llm_data.LLMProvidersData(**{
            "llm_provider_obj": llm_provider,
            "llm_res_parser_obj": llm_res_parser_obj
        })

        llm_config_data_list = [infy_model_evaluation.data.llm_data.LLMConfigData(
            __root__={"openai_llm_provider": llm_provider_data})]

        metric_provider_obj1 = infy_model_evaluation.content_evaluator.QAEvalProvider(
            llm_config_data_list)

        metric_provider_obj_list = [metric_provider_obj1,]
        qna_evaluator_obj = infy_model_evaluation.content_evaluator.QnaEvaluator(
            metric_provider_obj_list)
        response_metrics_data = qna_evaluator_obj.evaluate(
            content_evaluator_req_data)
        response_metrics_data_dict = response_metrics_data.dict().get("metrics")
        response_metrics_data_dict['Q_No'] = q_no
        response_metrics_data_list.append(response_metrics_data_dict)
    output_file_path = f"C:/temp/{os.path.basename(os.path.dirname(__file__))}/qna_metrics_qaeval_2.json"
    FileUtil.create_dirs_if_absent(os.path.dirname(output_file_path))
    FileUtil.write_to_file(
        json.dumps(response_metrics_data_list, indent=4), output_file_path)


# def test_eval_qna_truthdata_qaeval_4(setup):
#     """This Test method is for qna evaluation from xlsx file with Custom model"""
#     response_metrics_data_list = []
#     qna_xlsx_file_path = f"{os.path.dirname(os.path.dirname(__file__))}/data/sample/input/question_data.xlsx"
#     # Read the Excel file
#     df = pd.read_excel(qna_xlsx_file_path)
#     # Loops through each row and pass required columns
#     for index, row in df.iterrows():
#         q_no = row['Q_No']
#         question = row['Question']
#         answer = row['Ground_Truth']
#         contexts = row['Answer_source']
#         content_evaluator_req_data = infy_model_evaluation.data.ContentEvaluatorReqData(
#             **{
#                 "question": question,
#                 "contexts": contexts,
#                 "answer": answer
#             }
#         )

#         llm_provider = infy_model_evaluation.llm.provider.CustomLlmProvider(
#             infy_model_evaluation.llm.provider.CustomLlmProviderConfigData(
#                 **{
#                     "api_url": os.environ['CUSTOM_LLM_MIXTRAL_INFERENCE_URL'],
#                     "model_name": 'mixtral8x7b-instruct',
#                     "json_payload": {
#                         "inputs": "",
#                         "parameters": {
#                             "max_new_tokens": 1000,
#                             "temperature": 0.1,
#                             "do_sample": True
#                         }
#                     }
#                 }
#             ))

#         llm_res_parser_obj = None
#         llm_provider_data = infy_model_evaluation.data.llm_data.LLMProvidersData(**{
#             "llm_provider_obj": llm_provider,
#             "llm_res_parser_obj": llm_res_parser_obj
#         })

#         llm_config_data_list = [infy_model_evaluation.data.llm_data.LLMConfigData(
#             __root__={"custom_llm_provider": llm_provider_data})]

#         metric_provider_obj1 = infy_model_evaluation.content_evaluator.QAEvalProvider(
#             llm_config_data_list)

#         metric_provider_obj_list = [metric_provider_obj1,]
#         qna_evaluator_obj = infy_model_evaluation.content_evaluator.QnaEvaluator(
#             metric_provider_obj_list)
#         response_metrics_data = qna_evaluator_obj.evaluate(
#             content_evaluator_req_data)
#         response_metrics_data_dict = response_metrics_data.dict().get("metrics")
#         response_metrics_data_dict['Q_No'] = q_no
#         response_metrics_data_list.append(response_metrics_data_dict)
#     output_file_path = f"C:/temp/{os.path.basename(os.path.dirname(__file__))}/qna_metrics_qaeval_4.json"
#     FileUtil.create_dirs_if_absent(os.path.dirname(output_file_path))
#     FileUtil.write_to_file(
#         json.dumps(response_metrics_data_list, indent=4), output_file_path)


def test_eval_qna_truthdata_qaeval_5(setup):
    """This Test method is for qna evaluation from xlsx file with LLMA Custom model"""
    response_metrics_data_list = []
    qna_xlsx_file_path = f"{os.path.dirname(os.path.dirname(__file__))}/data/sample/input/question_data.xlsx"
    # Read the Excel file
    df = pd.read_excel(qna_xlsx_file_path)
    # Loops through each row and pass required columns
    for index, row in df.iterrows():
        q_no = row['Q_No']
        question = row['Question']
        answer = row['Ground_Truth']
        contexts = row['Answer_source']
        content_evaluator_req_data = infy_model_evaluation.data.ContentEvaluatorReqData(
            **{
                "question": question,
                "contexts": contexts,
                "answer": answer
            }
        )

        llm_provider = infy_model_evaluation.llm.provider.ChatLlmProvider(
            infy_model_evaluation.llm.provider.ChatLlmProviderConfigData(
                **{
                    "api_url": os.environ['CUSTOM_LLM_LLAMA_3_1_INFERENCE_URL'],
                    "model_name": 'Meta-Llama-3.3-70B-Instruct',
                    "headers":  {"X-Cluster": "H100"},
                    "json_payload": {
                        "model": "/models/Meta-Llama-3.3-70B-Instruct",
                        "max_tokens": 1000,
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "stop": None,
                        "presence_penalty": 0,
                        "frequency_penalty": 0,
                    }
                }
            ))

        llm_res_parser_obj = None
        llm_provider_data = infy_model_evaluation.data.llm_data.LLMProvidersData(**{
            "llm_provider_obj": llm_provider,
            "llm_res_parser_obj": llm_res_parser_obj
        })

        llm_config_data_list = [infy_model_evaluation.data.llm_data.LLMConfigData(
            __root__={"custom_llm_provider": llm_provider_data})]

        metric_provider_obj1 = infy_model_evaluation.content_evaluator.QAEvalProvider(
            llm_config_data_list)

        metric_provider_obj_list = [metric_provider_obj1,]
        qna_evaluator_obj = infy_model_evaluation.content_evaluator.QnaEvaluator(
            metric_provider_obj_list)
        response_metrics_data = qna_evaluator_obj.evaluate(
            content_evaluator_req_data)
        response_metrics_data_dict = response_metrics_data.dict().get("metrics")
        response_metrics_data_dict['Q_No'] = q_no
        response_metrics_data_list.append(response_metrics_data_dict)
    output_file_path = f"C:/temp/{os.path.basename(os.path.dirname(__file__))}/qna_metrics_qaeval_5.json"
    FileUtil.create_dirs_if_absent(os.path.dirname(output_file_path))
    FileUtil.write_to_file(
        json.dumps(response_metrics_data_list, indent=4), output_file_path)


def test_eval_qna_truthdata_qaeval_racar_proxy_open_ai_gpt4(setup):
    """This Test method is for qna evaluation from xlsx file with Proxy call for model: OpenAI GPT-4"""
    response_metrics_data_list = []
    qna_xlsx_file_path = f"{os.path.dirname(os.path.dirname(__file__))}/data/sample/input/question_data.xlsx"
    # Read the Excel file
    df = pd.read_excel(qna_xlsx_file_path)
    # Loops through each row and pass required columns
    xlx_row_count = 0
    start_time = time.time()
    llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
        **{
            "api_url": os.environ['INFY_AICLOUD_SERVICE_URL'],
            "api_key": os.environ['AZURE_OPENAI_SECRET_KEY'],
            "model_name": "gpt-4-32k_2",
            "deployment_name": "gpt-4-32k_2",
            "max_tokens": 1000,
            'temperature': 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None
        })
    llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
        llm_provider_config_data)

    llm_res_parser_obj = None
    llm_provider_data = infy_model_evaluation.data.llm_data.LLMProvidersData(**{
        "llm_provider_obj": llm_provider,
        "llm_res_parser_obj": llm_res_parser_obj
    })
    llm_config_data_list = [infy_model_evaluation.data.llm_data.LLMConfigData(
        __root__={"proxy_open_ai_llm_provider": llm_provider_data})]

    metric_provider_obj1 = infy_model_evaluation.content_evaluator.QAEvalProvider(
        llm_config_data_list)
    metric_provider_obj2 = infy_model_evaluation.content_evaluator.RACARProvider(
        llm_config_data_list)

    metric_provider_obj_list = [metric_provider_obj1, metric_provider_obj2]
    qna_evaluator_obj = infy_model_evaluation.content_evaluator.QnaEvaluator(
        metric_provider_obj_list)
    for index, row in df.iterrows():
        xlx_row_count += 1
        q_no = row['Q_No']
        question = row['Question']
        answer = row['Ground_Truth']
        contexts = row['Answer_source']
        content_evaluator_req_data = infy_model_evaluation.data.ContentEvaluatorReqData(
            **{
                "question": question,
                "contexts": contexts,
                "answer": answer
            }
        )
        response_metrics_data = qna_evaluator_obj.evaluate(
            content_evaluator_req_data)
        response_metrics_data_dict = response_metrics_data.dict().get("metrics")
        response_metrics_data_dict['Q_No'] = q_no
        response_metrics_data_list.append(response_metrics_data_dict)
    elapsed_time = round((time.time() - start_time), 2)
    print(
        f"Total time taken for {xlx_row_count} rows: {elapsed_time} sec")
    print(
        f"Time take for each record: {(elapsed_time)/xlx_row_count} sec")
    output_file_path = f"C:/temp/{os.path.basename(os.path.dirname(__file__))}/qna_metrics_qaeval_racar_proxy_openai_gpt4.json"
    FileUtil.create_dirs_if_absent(os.path.dirname(output_file_path))
    FileUtil.write_to_file(
        json.dumps(response_metrics_data_list, indent=4), output_file_path)
    print("Output file path: ", output_file_path)
