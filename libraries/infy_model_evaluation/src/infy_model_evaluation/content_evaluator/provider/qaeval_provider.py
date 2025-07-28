# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

from typing import List
import logging
import traceback
import concurrent.futures
import infy_gen_ai_sdk
from ...data import ContentEvaluatorReqData, MetricsData
from ...content_evaluator import IMetricsProvider
from ...data.llm_data import LLMConfigData
# from ...llm.provider import OpenAILlmRequestData
from ...common.app_config_manager import AppConfigManager
from ...llm.provider.json_res_parser_provider import JSONResponseParser


class QAEvalProvider(IMetricsProvider):
    """Enhanced Metrics Provider implementing custom evaluation criteria"""
    __REASONING_DEPTH_PROMPT_FILE_PATH = "/prompt_templates/qaeval/reasoning_depth.txt"
    __CONTEXT_COVERAGE_PROMPT_FILE_PATH = "/prompt_templates/qaeval/context_coverage.txt"
    __GROUNDEDNESS_PROMPT_FILE_PATH = "/prompt_templates/qaeval/groundedness.txt"
    __ANSWERABILITY_PROMPT_FILE_PATH = "/prompt_templates/qaeval/answerability.txt"

    def __init__(self, llm_config_data_list: List[LLMConfigData]) -> None:
        self.__logger = logging.getLogger(__name__)
        self.set_llm_provider(llm_config_data_list)
        app_config_folder_path = AppConfigManager().get_app_config_folder()
        metric_prompts = {
            "reasoning_depth": self.__get_file_content(
                f'{app_config_folder_path}/{self.__REASONING_DEPTH_PROMPT_FILE_PATH}'),
            "context_coverage": self.__get_file_content(
                f'{app_config_folder_path}/{self.__CONTEXT_COVERAGE_PROMPT_FILE_PATH}'),
            "groundedness": self.__get_file_content(
                f'{app_config_folder_path}/{self.__GROUNDEDNESS_PROMPT_FILE_PATH}'),
            "answerability": self.__get_file_content(
                f'{app_config_folder_path}/{self.__ANSWERABILITY_PROMPT_FILE_PATH}')
        }
        super().__init__(metric_prompts)

    def set_llm_provider(self, llm_config_data_list: List[LLMConfigData]) -> None:
        """Set the LLM provider(s)"""
        self.__llm_config_data_list = llm_config_data_list

    def calculate_metrics(self, content_evaluator_req_data: ContentEvaluatorReqData) -> MetricsData:
        """Calculate all metrics for the given content"""
        try:
            llm_providers_obj, llm_parser_obj = self.__get_llm_components()
            metrics_data_dict = {}
            list_count = len(self.get_prompt_template_dict().items())
            with concurrent.futures.ThreadPoolExecutor(max_workers=list_count) as executor:
                futures = []
                for metric_name, prompt_template in self.get_prompt_template_dict().items():
                    futures.append(executor.submit(self.__llm_call_and_parse,
                                                   content_evaluator_req_data, prompt_template,
                                                   llm_providers_obj, llm_parser_obj, metric_name))
                for future in concurrent.futures.as_completed(futures):
                    parsed_response = future.result()
                    if parsed_response is not None:
                        metrics_data_dict.update(parsed_response)

            metrics_data = MetricsData(__root__=metrics_data_dict)

        except Exception as e:
            self.__logger.exception(traceback.format_exc())
            raise e

        return metrics_data

    def __llm_call_and_parse(self, content_evaluator_req_data, prompt_template,
                             llm_providers_obj, llm_parser_obj, metric_name):
        prompt = self.__fill_template(
            content_evaluator_req_data, prompt_template
        )
        llm_response = llm_providers_obj.get_llm_response(infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmRequestData(
            **{
                "prompt_template": prompt,
                "template_var_to_value_dict": {
                    'context': None,
                    'question': None}
            }
        ))

        if llm_parser_obj:
            parsed_response = llm_parser_obj.parse_llm_response(
                llm_response, metric_name)
        else:
            llm_response_parser = JSONResponseParser()
            parsed_response = llm_response_parser.parse_llm_response(
                llm_response, metric_name)
        return parsed_response

    def __get_llm_components(self):
        """Get both the OpenAI LLM provider and response parser from config"""
        for llm_config_data_obj in self.__llm_config_data_list:
            llm_config_data = llm_config_data_obj.dict().get("__root__")
            for llm_provider_name, llm_providers_data in llm_config_data.items():
                if llm_provider_name:  # == "openai_llm_provider":
                    llm_provider = llm_providers_data.get("llm_provider_obj")
                    llm_parser = llm_providers_data.get(
                        "llm_res_parser_obj", None)
                    # llm_request_data_class=llm_providers_data.get(
                    #    "llm_request_data_class")
                    if llm_provider:
                        return llm_provider, llm_parser
                    else:
                        raise ValueError(
                            "Missing LLM provider in configuration")
        raise ValueError("OpenAI LLM provider not found in configuration")

    def __fill_template(self, content_evaluator_req_data: ContentEvaluatorReqData, prompt_template: str) -> str:
        """Fill the prompt template with the values"""
        template_vars = {
            '{question}': content_evaluator_req_data.question,
            '{context}': content_evaluator_req_data.contexts,
            '{answer}': content_evaluator_req_data.answer
        }

        # Handle QA pairs if needed
        if '{qa_pairs}' in prompt_template:
            qa_pairs = f"{content_evaluator_req_data.question}\nAnswer: {content_evaluator_req_data.answer}"
            template_vars['{qa_pairs}'] = qa_pairs

        # Only replace variables that exist in the template
        filled_prompt = prompt_template
        for var, value in template_vars.items():
            if var in filled_prompt:
                filled_prompt = filled_prompt.replace(
                    var, str(value) if value is not None else '')

        return filled_prompt

    def __get_file_content(self, prompt_file_path: str) -> str:
        """Return prompt template from file"""
        try:
            with open(prompt_file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError as e:
            self.__logger.error("Prompt file not found: %s", prompt_file_path)
            raise e
