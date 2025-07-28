# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for Custom LLM provider"""
import uuid
import json
import logging
import traceback
import requests
import infy_fs_utils


class CustomLlmProvider():
    """Custom LLM provider"""

    def __init__(self) -> None:
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler():
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler().get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

    def fetch_answers(self, target_llm_config, dataset):
        """Fetches answers from the model."""
        try:
            total_records = len(dataset)
            fetched_ans_records = 0
            prompt_template = target_llm_config.prompt_template
            for counter, dataset_entry in enumerate(dataset, start=1):
                __context = dataset_entry.contexts[0]
                __question = dataset_entry.question
                combined_query = prompt_template.format(
                    context=__context, question=__question)
                response = self.__invoke_api(combined_query, target_llm_config)
                if target_llm_config.remove_prompt_from_response:
                    response = self.__remove_prompt(
                        response, combined_query)
                dataset_entry.answer = response
                fetched_ans_records = counter
                self.__logger.debug(
                    "Fetched answer for %s out of %s records.", fetched_ans_records, total_records)
        except Exception as e:
            self.__logger.exception(traceback.format_exc())
            raise e
        return response

    def __invoke_api(self, query, target_llm_config):
        url = target_llm_config.api_url
        response = ''
        request_id = str(uuid.uuid4())
        json_payload = self.__build_json_payload(query, target_llm_config)
        try:
            self.__logger.debug("REQUEST %s:%s ", request_id,
                                json.dumps(json_payload, indent=4))
            model_response = requests.post(
                url, json=json_payload, verify=False, timeout=180)
            if model_response.status_code == 200:
                ml_model_output = model_response.json()
                if len(ml_model_output) > 0:
                    if isinstance(ml_model_output, list):
                        ml_model_output = ml_model_output[0]
                    self.__logger.debug("RESPONSE %s:%s", request_id, json.dumps(
                        ml_model_output, indent=4))
                    response = ml_model_output['generated_text']
                    if not response:
                        raise Exception("Model has given empty responses")
            else:
                raise Exception(
                    f'Error in calling API {model_response.status_code}')
        except Exception as e:
            self.__logger .error('Error in calling API %s', e)
        return response

    def __build_json_payload(self, query, target_llm_config):
        json_payload = {}
        json_payload['inputs'] = query
        parameters = {}
        parameters['max_new_tokens'] = target_llm_config.max_tokens
        parameters['temperature'] = target_llm_config.temperature
        if target_llm_config.requires_num_return_sequences:
            parameters['num_return_sequences'] = target_llm_config.num_return_sequences
        parameters['do_sample'] = target_llm_config.do_sample
        json_payload['parameters'] = parameters
        return json_payload

    def __remove_prompt(self, answer, prompt):
        return answer[len(prompt):].strip()
