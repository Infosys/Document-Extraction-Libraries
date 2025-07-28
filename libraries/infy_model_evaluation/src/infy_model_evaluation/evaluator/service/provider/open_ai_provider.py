# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

"""Module for fetching answers using 'question' and 'context'."""

import logging
import traceback
from openai import AzureOpenAI
import infy_fs_utils


class OpenAIProvider():
    """Domain class"""

    def __init__(self) -> None:
        if infy_fs_utils.manager.FileSystemLoggingManager().has_fs_logging_handler():
            self.__logger = infy_fs_utils.manager.FileSystemLoggingManager(
            ).get_fs_logging_handler().get_logger()
        else:
            self.__logger = logging.getLogger(__name__)

    def fetch_answers(self, target_llm_config, dataset):
        """Fetches answers from the model."""
        try:
            client = AzureOpenAI(
                **{
                    "azure_endpoint": target_llm_config.api_url,
                    "api_key": target_llm_config.api_key,
                    "api_version": target_llm_config.api_version,
                    "azure_deployment": target_llm_config.deployment_name,
                })
            __model = target_llm_config.model_name
            __max_tokens = target_llm_config.max_tokens
            __temperature = target_llm_config.temperature
            prompt_template = target_llm_config.prompt_template
            __is_chat_model = target_llm_config.is_chat_model
            __top_p = target_llm_config.top_p
            __frequency_penalty = target_llm_config.frequency_penalty
            __presence_penalty = target_llm_config.presence_penalty
            __stop = target_llm_config.stop

            total_records = len(dataset)
            fetched_ans_records = 0
            if (__is_chat_model):
                for counter, dataset_entry in enumerate(dataset, start=1):
                    __context = dataset_entry.contexts[0]
                    __question = dataset_entry.question
                    start_phrase = prompt_template.format(
                        context=__context, question=__question)
                    message_text = [
                        {"role": "system", "content": start_phrase}]
                    response = client.chat.completions.create(
                        model=__model,
                        messages=message_text,
                        temperature=__temperature,
                        max_tokens=__max_tokens,
                        top_p=__top_p,
                        frequency_penalty=__frequency_penalty,
                        presence_penalty=__presence_penalty,
                        stop=__stop
                    )
                    dataset_entry.answer = response.choices[0].message.content
                    fetched_ans_records = counter
                    self.__logger.debug(
                        "Fetched answer for %s out of %s records.", fetched_ans_records, total_records)
            else:
                # text-davinci-003
                params_not_required = [
                    'top_p', 'frequency_penalty', 'presence_penalty', 'stop']
                if __top_p or __frequency_penalty or __presence_penalty or __stop:
                    self.__logger.warning(
                        '%s params not required for the model %s', params_not_required, __model)
                for counter, dataset_entry in enumerate(dataset, start=1):
                    __context = dataset_entry.contexts[0]
                    __question = dataset_entry.question
                    start_phrase = prompt_template.format(
                        context=__context, question=__question)
                    response = client.completions.create(
                        model=__model, prompt=start_phrase, max_tokens=__max_tokens)
                    dataset_entry.answer = response.choices[0].text
                    fetched_ans_records = counter
                    self.__logger.debug(
                        "Fetched answer for %s out of %s records.", fetched_ans_records, total_records)
            self.__logger.info(
                "Answers fetched for %s dataset records!", fetched_ans_records)
        except Exception as e:
            self.__logger.exception(traceback.format_exc())
            raise e
