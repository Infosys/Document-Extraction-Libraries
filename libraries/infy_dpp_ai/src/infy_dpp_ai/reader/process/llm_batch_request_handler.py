# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import os
import uuid
from infy_dpp_sdk.data import *
import infy_gen_ai_sdk
from infy_dpp_ai.reader.service.provider.moderator import Moderator
from ...common.string_util import StringUtil


class LLMBatchRequestHandler:
    def __init__(self, file_sys_handler, logger, app_config, llm_provider, get_llm, get_llm_config, processor_config_data, cache_enabled, moderation_enabled, moderation_config, moderation_payload, response_validation, batch_size):
        self.file_sys_handler = file_sys_handler
        self.logger = logger
        self.app_config = app_config
        self.llm_provider = llm_provider
        self.get_llm = get_llm
        self.get_llm_config = get_llm_config
        self.processor_config_data = processor_config_data
        self.cache_enabled = cache_enabled
        self.moderation_enabled = moderation_enabled
        self.moderation_config = moderation_config
        self.moderation_payload = moderation_payload
        self.response_validation = response_validation
        self.batch_size = batch_size

    def get_response(self, request_data_list):
        response_list, llm_response_json_list, llm_request_data_list, qr_attr_keys, request_dict_list = [], [], [], [], []
        moderation_status = "PASSED"
        moderation_results = {}

        for request_data in request_data_list:
            qr_attr_key = request_data.pop('qr_attr_key', None)
            qr_attr_keys.append(qr_attr_key)
            request_dict_list.append(request_data)
            llm_request_data = infy_gen_ai_sdk.llm.provider.OpenAILlmRequestData(
                **request_data)
            llm_request_data_list.append(llm_request_data)

        if not self.cache_enabled:
            if self.moderation_enabled:
                moderator = Moderator()
                prompt = self.__build_prompt(llm_request_data)
                self.moderation_payload['Prompt'] = prompt
                moderation_results = moderator.perform_moderation_checks(
                    self.moderation_config, self.moderation_payload)
                moderation_status = moderation_results.get(
                    'summary').get('status')
            if moderation_status == "PASSED":
                # Step 3 - Fire query to LLM
                if self.response_validation.get('enabled', False):
                    max_attempts = self.response_validation.get(
                        'total_attempts', 1)
                    llm_attempts = 1
                    while llm_attempts <= max_attempts:
                        llm_response_json_list = []
                        llm_response_data_list: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = self.llm_provider.get_llm_response_batch(
                            llm_request_data_list)
                        success = True
                        for llm_response_data in llm_response_data_list:
                            llm_response_txt = llm_response_data.llm_response_txt
                            llm_response_json = StringUtil.parse_string_to_json(llm_response_txt)
                            expected_type = self.response_validation.get(
                                'type', 'string')
                            if expected_type == 'json':
                                if isinstance(llm_response_txt, str):
                                    try:
                                        llm_response_json = json.loads(
                                            llm_response_txt)
                                    except json.JSONDecodeError:
                                        llm_attempts += 1
                                        success = False
                                        llm_response_json_list.append(
                                            llm_response_txt)
                                        break
                                else:
                                    break
                            llm_response_json_list.append(
                                llm_response_json)
                        if success:
                            break
                else:
                    llm_response_data_list: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = self.llm_provider.get_llm_response_batch(
                        llm_request_data_list)
                    for llm_response_data in llm_response_data_list:
                        llm_response_txt = llm_response_data.llm_response_txt
                        llm_response_json = StringUtil.parse_string_to_json(llm_response_txt)
                        llm_response_json_list.append(llm_response_json)

                if self.moderation_enabled:
                    self.moderation_payload['Prompt'] = llm_response_txt
                    moderation_results = moderator.perform_moderation_checks(
                        self.moderation_config, self.moderation_payload)
                    moderation_status = moderation_results.get(
                        'summary').get('status')
                if moderation_status != "PASSED":
                    llm_response_txt = "ANSWER FAILED MODERATION CHECKS"
                # Save response to cache only if self.get_llm == 'openai'
                if self.get_llm == 'openai':
                    result_temp_file_path = f'{temp_uuid_folder_path}/llm_response.txt'
                    self.file_sys_handler.write_file(
                        result_temp_file_path, llm_response_txt)
                    __cache_manager.add(combined_query_temp_file_path, [
                                        result_temp_file_path], __bucket_name)
                    for temp_files in self.file_sys_handler.list_files(temp_uuid_folder_path, "*"):
                        self.file_sys_handler.delete_file(
                            temp_files)
            else:
                llm_response_txt = "FAILED MODERATION CHECKS"
                self.logger.debug("Moderation Results :%s", json.dumps(
                    moderation_results, indent=4))
            # answer = llm_response_json
            for idx, llm_response_json in enumerate(llm_response_json_list):
                response_list.append({
                    'qr_attr_key': qr_attr_keys[idx],
                    'llm_response': llm_response_json,
                    'llm_attempts': llm_attempts,
                    'max_attempts': max_attempts,
                    'moderation_results': moderation_results,
                    'request_data_dict': request_dict_list[idx]
                })

        return response_list

    def __get_uuid(self):
        return str(uuid.uuid4())

    def __create_uuid_dir(self, work_input_location, uuid=None):
        if not uuid:
            uuid = self.__get_uuid()
        work_input_location = self.__create_dirs_if_absent(
            work_input_location + "/" + uuid)
        return work_input_location, uuid

    def __create_dirs_if_absent(self, dir_path):
        if not self.file_sys_handler.exists(dir_path):
            self.file_sys_handler.create_folders(dir_path)
        return dir_path

    def __build_prompt(self, llm_request_data):
        context = llm_request_data.template_var_to_value_dict.get(
            'context')
        question = llm_request_data.template_var_to_value_dict.get('question')
        prompt_template = llm_request_data.prompt_template
        prompt = prompt_template.replace(
            '{context}', context).replace('{question}', question)
        prompt = self.__remove_prompt_template(prompt_template, prompt)
        return prompt

    def __remove_prompt_template(self, prompt_template, prompt):
        return prompt[len(prompt_template):].strip()
