# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import os
import re
import copy
import uuid
import infy_dpp_sdk
from infy_dpp_sdk.data import *
import infy_gen_ai_sdk
import infy_fs_utils

from infy_dpp_ai.reader.service.provider.moderator import Moderator
from .cache_manager import CacheManager
from ..service.provider.custom_llm_provider import CustomLlmProvider, CustomLlmProviderConfigData
from ..service.provider.llama_3_1_llm_provider import LlamaLlmProvider, LlamaLlmProviderConfigData
PROCESSEOR_CONTEXT_DATA_NAME = "reader"

# class ReaderProcessor():


class Reader(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self.__file_sys_handler: infy_fs_utils.interface.IFileSystemHandler = self.get_fs_handler()
        self.__logger = self.get_logger()
        if not infy_fs_utils.manager.FileSystemManager().has_fs_handler(infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK):
            infy_fs_utils.manager.FileSystemManager().add_fs_handler(
                infy_fs_utils.provider.FileSystemHandler(
                    self.__file_sys_handler.get_storage_config_data()),
                infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK)
        client_config_data_dict = infy_dpp_sdk.ClientConfigManager().get().dict()
        client_config_data = infy_gen_ai_sdk.ClientConfigData(
            **client_config_data_dict)
        infy_gen_ai_sdk.ClientConfigManager().load(client_config_data)

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        processor_response_data = infy_dpp_sdk.data.ProcessorResponseData()
        __processor_config_data = config_data.get('Reader', {})
        document_id = document_data.document_id
        vector_storage = ""
        sparse_storage = ""
        get_llm = ""
        get_llm_config = {}
        used_cache = False
        moderation_config = {}
        moderation_payload = {}
        moderation_results = {}
        moderation_status = "PASSED"
        moderation_enabled = False
        vector_enabled = False
        sparse_enabled = False
        rrf_enabled = False

        for key, value in __processor_config_data.items():
            if key == 'llm':
                for e_key, e_val in value.items():
                    if e_key == 'openai':
                        if e_val.get('enabled'):
                            get_llm = e_key
                            get_llm_config = e_val.get('configuration')
                            break
                    if e_key == 'llama-3-1':
                        if e_val.get('enabled'):
                            get_llm = e_key
                            get_llm_config = e_val.get('configuration')
                            break
                    elif e_key == 'custom':
                        for custom_llm_key, custom_llm_val in e_val.items():
                            if custom_llm_val.get('enabled'):
                                get_llm = e_key
                                get_llm_config = custom_llm_val.get(
                                    'configuration')
                                json_payload_dict = custom_llm_val.get(
                                    'json_payload')
                                custom_llm_name = custom_llm_key
                                break
            if key == 'storage':
                for storage_key, storage_value in value.items():
                    if storage_key == 'vectordb':
                        for e_key, e_val in storage_value.items():
                            if e_key and e_val.get('enabled'):
                                vector_enabled = True
                                vector_storage = e_key
                                vector_storage_config = e_val.get(
                                    'configuration')
                                # encoded_files_root_path= get_storage_config.get("encoded_files_root_path")
                                # chunked_files_root_path= get_storage_config.get("chunked_files_root_path")

                    if storage_key == 'sparseindex':
                        for e_key, e_val in storage_value.items():
                            if e_key and e_val.get('enabled'):
                                sparse_enabled = True
                                sparse_storage = e_key

            if key == 'moderation':
                moderation_enabled = value.get('enabled')
                if moderation_enabled:
                    moderation_config = value.get('configuration')
                    moderation_payload = value.get('json_payload')

            if key == 'hybrid_search':
                for hybrid_key, hybrid_value in value.items():
                    if hybrid_key == 'rrf':
                        if hybrid_value.get('enabled'):
                            rrf_enabled = True

        # Step 1 - Choose LLM provider
        model_name = ''
        vector_types = ['faiss']
        sparse_types = ['bm25s', 'infy_db_service']
        if get_llm == 'openai' and (vector_storage in vector_types or sparse_storage in sparse_types):
            os.environ["TIKTOKEN_CACHE_DIR"] = get_llm_config['tiktoken_cache_dir']
            llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAILlmProviderConfigData(
                **get_llm_config)
            llm_provider = infy_gen_ai_sdk.llm.provider.OpenAILlmProvider(
                llm_provider_config_data)
            cache_enabled = __processor_config_data.get('llm').get('openai'
                                                                   ).get('cache').get('enabled')
            model_name = llm_provider_config_data.deployment_name
        if get_llm == 'custom' and (vector_storage in vector_types or sparse_storage in sparse_types):
            llm_provider_config_data = CustomLlmProviderConfigData(
                **get_llm_config)
            llm_provider = CustomLlmProvider(
                llm_provider_config_data, json_payload_dict, custom_llm_name)
            cache_enabled = False
            model_name = custom_llm_name
        if get_llm == 'llama-3-1' and (vector_storage in vector_types or sparse_storage in sparse_types):
            llm_provider_config_data = LlamaLlmProviderConfigData(
                **get_llm_config)
            llm_provider = LlamaLlmProvider(
                llm_provider_config_data)
            cache_enabled = False
            model_name = llm_provider_config_data.deployment_name
        context_data = context_data if context_data else {}
        # QUERY RETRIEVER VALIDATION  HANDLED#
        if context_data.get('query_retriever').get('error'):
            processor_response_data.message_data = [MessageData(type="ERROR",
                                                                message=context_data.get('query_retriever').get('error'))]
            processor_response_data.document_data = document_data
            processor_response_data.context_data = context_data
            return processor_response_data
        # QUERY RETRIEVER VALIDATION END#
        data_ret_queries_list = context_data.get(
            'query_retriever').get('queries')

        # Step 2 - Prepare data
        reader_input_list = __processor_config_data['inputs']
        named_propt_temp_dict = __processor_config_data['named_prompt_templates']
        named_context_templates_dict = __processor_config_data['named_context_templates']
        output_list = []
        for query in data_ret_queries_list:
            self.__logger.info(f'...Question...{query["question"]}')
            QUESTION = query["question"]
            qr_attr_key = query['attribute_key']
            top_k_matches_list = []

            top_k_len = len(query['top_k_matches'])
            if top_k_len > 1 and sum([vector_enabled, sparse_enabled]) >= 2 and rrf_enabled:
                key_to_use = 'rrf'
            elif top_k_len >= 1 and vector_enabled and not sparse_enabled:
                key_to_use = 'vectordb'
            elif top_k_len >= 1 and vector_enabled and sparse_enabled and not rrf_enabled:
                key_to_use = 'vectordb'
            elif top_k_len >= 1 and sparse_enabled and not vector_enabled:
                key_to_use = 'sparseindex'

            for item in query['top_k_matches']:
                if key_to_use in item:
                    top_k_matches_list.extend(item[key_to_use])
                else:
                    continue
            # Combining text logic
            combined_files_dict = {}
            for k, v in named_context_templates_dict.items():
                comb_file_content = ''
                all_replace_words_list = re.findall(r'\{(\w+)\}', v)
                remain_repl_words_list = copy.deepcopy(all_replace_words_list)
                remain_repl_words_list.remove('chunk_text')
                skip_llm_call = False
                for idx, match in enumerate(top_k_matches_list[:reader_input_list[0]['top_k']]):
                    if "message" in match:
                        skip_llm_call = True
                        continue
                    meta_data = match.get('meta_data')
                    f_file = match.get("content")
                    # template = re.sub(
                    #     '{chunk_text}', re.escape(f_file), v)
                    template = v.replace('{chunk_text}', f_file)
                    if not remain_repl_words_list:
                        comb_file_content = comb_file_content + template
                    else:
                        for replace_word in remain_repl_words_list:
                            relevant_metadata_value = str(
                                meta_data.get(replace_word))
                            template = template.replace(
                                f'{{{replace_word}}}', repr(relevant_metadata_value))
                        comb_file_content = comb_file_content + template

                    if idx == len(top_k_matches_list[:reader_input_list[0]['top_k']])-1:
                        combined_files_dict[k] = comb_file_content

            for input in reader_input_list:
                if input['attribute_key'] == qr_attr_key:
                    if skip_llm_call:
                        output_list.append({
                            "attribute_key": qr_attr_key,
                            "message": "No Records found.",
                            "retriever_output": '',
                            "model_name": '',
                            "total_attempts": 0,
                            "model_input": '',
                            "model_output": '',
                            "moderation_input": '',
                            "moderation_output": '',
                            "retriver_confidence_pct": '',
                            "source_metadata": '',
                            "used_cache": ''})
                        continue
                    templ_prompt_list = named_propt_temp_dict[input['prompt_template']].get(
                        'content', [])
                    context_template_name = named_propt_temp_dict[input['prompt_template']].get(
                        'context_template', '')
                    combined_text = combined_files_dict[context_template_name]
                    if len(templ_prompt_list) < 1:
                        file_path = named_propt_temp_dict[input['prompt_template']].get(
                            'file_path', None)
                        if file_path:
                            template_str = self.__file_sys_handler.read_file(
                                file_path)
                    else:
                        template_str = ''.join(templ_prompt_list)
                    response_validation = named_propt_temp_dict[input['prompt_template']].get(
                        'response_validation', {})

                    # Step 2 - Prepare data
                    CONTEXT = combined_text
                    PROMPT_TEMPLATE = template_str
                    request_data_dict = {
                        "prompt_template": PROMPT_TEMPLATE,
                        "template_var_to_value_dict": {
                            'context': CONTEXT,
                            'question': QUESTION
                        }
                    }
                    llm_request_data = infy_gen_ai_sdk.llm.provider.OpenAILlmRequestData(
                        **request_data_dict
                    )
                    # CACHE HANDLING#
                    if get_llm == 'openai':
                        cache_rel_root_path = __processor_config_data.get('llm').get(
                            'openai').get('cache').get('cache_root_path')
                        cache_root_path = cache_rel_root_path
                        config_params = {
                            "cache_enabled": cache_enabled,
                            "cache_path_root": cache_root_path
                        }
                        __cache_manager = CacheManager(config_params)
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
                        combined_query += f'  \n Temperature : {get_llm_config.get("temperature")}'
                        self.__file_sys_handler.write_file(
                            combined_query_temp_file_path, combined_query)
                        cache_file_path = __cache_manager.get(
                            combined_query_temp_file_path, __bucket_name)
                        if cache_enabled:
                            if cache_file_path:
                                for cache_file in self.__file_sys_handler.list_files(cache_file_path, "*"):
                                    if os.path.basename(cache_file) == 'llm_response.txt':
                                        llm_response_txt = self.__file_sys_handler.read_file(
                                            cache_file)
                                        used_cache = True
                            else:
                                cache_enabled = False
                    if not cache_enabled:
                        if moderation_enabled:
                            moderator = Moderator()
                            prompt = self.__build_prompt(llm_request_data)
                            moderation_payload['Prompt'] = prompt
                            moderation_results = moderator.perform_moderation_checks(
                                moderation_config, moderation_payload)
                            moderation_status = moderation_results.get(
                                'summary').get('status')
                        if moderation_status == "PASSED":
                            # Step 3 - Fire query to LLM
                            if response_validation.get('enabled', False):
                                max_attempts = response_validation.get(
                                    'total_attempts', 1)
                                llm_attempts = 1
                                while llm_attempts <= max_attempts:
                                    llm_response_data: infy_gen_ai_sdk.llm.provider.OpenAILlmResponseData = llm_provider.get_llm_response(
                                        llm_request_data)
                                    llm_response_txt = llm_response_data.llm_response_txt
                                    llm_response_json = llm_response_txt
                                    expected_type = response_validation.get(
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
                                llm_response_data: infy_gen_ai_sdk.llm.provider.OpenAILlmResponseData = llm_provider.get_llm_response(
                                    llm_request_data)
                                llm_response_txt = llm_response_data.llm_response_txt
                                llm_response_json = llm_response_txt

                            if moderation_enabled:
                                moderation_payload['Prompt'] = llm_response_txt
                                moderation_results = moderator.perform_moderation_checks(
                                    moderation_config, moderation_payload)
                                moderation_status = moderation_results.get(
                                    'summary').get('status')
                            if moderation_status != "PASSED":
                                llm_response_txt = "ANSWER FAILED MODERATION CHECKS"
                            # Save response to cache only if get_llm == 'openai'
                            if get_llm == 'openai':
                                result_temp_file_path = f'{temp_uuid_folder_path}/llm_response.txt'
                                self.__file_sys_handler.write_file(
                                    result_temp_file_path, llm_response_txt)
                                __cache_manager.add(combined_query_temp_file_path, [
                                    result_temp_file_path], __bucket_name)
                                for temp_files in self.__file_sys_handler.list_files(temp_uuid_folder_path, "*"):
                                    self.__file_sys_handler.delete_file(
                                        temp_files)
                        else:
                            llm_response_txt = "FAILED MODERATION CHECKS"
                            self.__logger.debug("Moderation Results :%s",
                                                json.dumps(moderation_results, indent=4))
                    answer = llm_response_json
                    retriever_output = {"top_k": reader_input_list[0]['top_k']}
                    source_metadata = []
                    retriver_confidence_pct = -1
                    try:
                        # try:
                        #     answer = json.loads(answer)
                        # except ValueError:
                        #     answer = json.loads(answer.replace("'", "\""))
                        retriver_confidence_pct = self.__calculate_conf_pct(
                            answer)
                        chunk_id = str(answer.get('sources', {})
                                       [0].get('chunk_id'))
                        for match in top_k_matches_list:
                            meta_data = match.get("meta_data")
                            if chunk_id == str(meta_data.get('chunk_id')):
                                source_metadata = [{
                                    "chunk_id": chunk_id,
                                    "bbox_format": meta_data.get('bbox_format'),
                                    "bbox": meta_data.get('bbox'),
                                    "doc_name": meta_data.get('doc_name')
                                }]
                                break
                    except:
                        pass
                    output_list.append({
                        "attribute_key": qr_attr_key,
                        "retriever_output": retriever_output,
                        "model_name": model_name,
                        "total_attempts": min(llm_attempts, max_attempts),
                        "model_input": request_data_dict,
                        "model_output": answer,
                        "moderation_input": moderation_payload.copy(),
                        "moderation_output": moderation_results,
                        "retriver_confidence_pct": retriver_confidence_pct,
                        "source_metadata": source_metadata,
                        "used_cache": used_cache
                    })
        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {'output': output_list}

        # Populate response data
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data

    def __calculate_conf_pct(self, answer):
        score = answer.get('score', -1)
        # here we are considering maximum score to 10
        max_score = 10
        if score > 0:
            confidence = 1-score
        elif score > 1:
            # max the score more is the distance b/w texts and
            normalized_score = 1-float(score)/(max_score+score)
            confidence = 1-normalized_score
        elif score == -1:
            confidence_pct = -1
        else:
            self.__logger.error(f'score is {score}')
            raise ValueError('score should not be negative')
        if score != -1:
            confidence_pct = round(confidence*100, 2)
        return confidence_pct

    def __get_uuid(self):
        return str(uuid.uuid4())

    def __create_uuid_dir(self, work_input_location, uuid=None):
        if not uuid:
            uuid = self.__get_uuid()
        work_input_location = self.__create_dirs_if_absent(
            work_input_location + "/" + uuid)
        return work_input_location, uuid

    def __create_dirs_if_absent(self, dir_path):
        if not self.__file_sys_handler.exists(dir_path):
            self.__file_sys_handler.create_folders(dir_path)
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
