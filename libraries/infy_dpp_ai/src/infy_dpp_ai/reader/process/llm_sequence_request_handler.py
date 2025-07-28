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
from .cache_manager import CacheManager
from ...common.string_util import StringUtil


class LLMSequenceRequestHandler:
    def __init__(self, file_sys_handler, logger, app_config, llm_provider, get_llm, get_llm_config, processor_config_data, cache_enabled, moderation_enabled, moderation_config, moderation_payload, response_validation):
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

    def get_response(self, request_data_list):
        response_list = []
        qr_attr_key = ''
        moderation_results = {}
        moderation_status = "PASSED"
        for request_data_dict in request_data_list:
            combined_text = request_data_dict.get(
                'template_var_to_value_dict').get('context')
            QUESTION = request_data_dict.get(
                'template_var_to_value_dict').get('question')
            PROMPT_TEMPLATE = request_data_dict.get('prompt_template')
            qr_attr_key = request_data_dict.pop('qr_attr_key', None)

            llm_request_data = infy_gen_ai_sdk.llm.provider.OpenAILlmRequestData(
                **request_data_dict)

            # CACHE HANDLING#
            if self.get_llm == 'openai':
                cache_rel_root_path = self.processor_config_data.get(
                    'llm').get('openai').get('cache').get('cache_root_path')
                cache_root_path = cache_rel_root_path
                config_params = {
                    "cache_enabled": self.cache_enabled,
                    "cache_path_root": cache_root_path
                }
                __cache_manager = CacheManager(
                    config_params, self.file_sys_handler, self.logger, self.app_config)
                __bucket_name = "openai"
                temp_folder_path = f'{cache_root_path}/temp/infy_model_service/{__bucket_name}'
                uuid = self.__get_uuid()
                temp_uuid_folder_path, _ = self.__create_uuid_dir(
                    temp_folder_path, uuid)
                combined_query_temp_file_path = f'{temp_uuid_folder_path}/llm_input_prompt.txt'
                self.__create_dirs_if_absent(
                    os.path.dirname(combined_query_temp_file_path))
                combined_query = PROMPT_TEMPLATE.replace(
                    '{context}', combined_text).replace('{question}', QUESTION)
                combined_query += f'  \n Temperature : {self.get_llm_config.get("temperature")}'
                self.file_sys_handler.write_file(
                    combined_query_temp_file_path, combined_query)
                cache_file_path = __cache_manager.get(
                    combined_query_temp_file_path, __bucket_name)
                if self.cache_enabled:
                    if cache_file_path:
                        for cache_file in self.file_sys_handler.list_files(cache_file_path, "*"):
                            if os.path.basename(cache_file) == 'llm_response.txt':
                                llm_response_txt = self.file_sys_handler.read_file(
                                    cache_file)
                                used_cache = True
                    else:
                        self.cache_enabled = False
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
                            llm_response_data: infy_gen_ai_sdk.llm.provider.OpenAILlmResponseData = self.llm_provider.get_llm_response(
                                llm_request_data)
                            llm_response_txt = llm_response_data.llm_response_txt
                            llm_response_json = StringUtil.parse_string_to_json(llm_response_txt)
                            expected_type = self.response_validation.get(
                                'type', 'string')
                            if expected_type == 'json':
                                if isinstance(llm_response_txt, str):
                                    try:
                                        llm_response_json = json.loads(
                                            llm_response_txt)
                                        break
                                    except json.JSONDecodeError:
                                        llm_attempts += 1
                                        continue
                                else:
                                    break
                    else:
                        llm_response_data: infy_gen_ai_sdk.llm.provider.OpenAILlmResponseData = self.llm_provider.get_llm_response(
                            llm_request_data)
                        llm_response_txt = llm_response_data.llm_response_txt
                        llm_response_json = StringUtil.parse_string_to_json(llm_response_txt)

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
            response_list.append({
                'qr_attr_key': qr_attr_key,
                'llm_response': llm_response_json,
                'llm_attempts': llm_attempts,
                'max_attempts': max_attempts,
                'moderation_results': moderation_results,
                'request_data_dict': request_data_dict
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
