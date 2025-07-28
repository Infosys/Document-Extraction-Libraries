# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import json
import os
import re
import copy
import infy_dpp_sdk
from infy_dpp_sdk.data import *
import infy_gen_ai_sdk

from .llm_sequence_request_handler import LLMSequenceRequestHandler
from .llm_batch_request_handler import LLMBatchRequestHandler
from ..service.provider.custom_llm_provider import CustomLlmProvider, CustomLlmProviderConfigData
from ..service.provider.llama_3_1_llm_provider import LlamaLlmProvider, LlamaLlmProviderConfigData

PROCESSEOR_CONTEXT_DATA_NAME = "reader"


class Reader(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self.__file_sys_handler = self.get_fs_handler()
        self.__app_config = self.get_app_config()
        self.__logger = self.get_logger()

        client_config_data_dict = infy_dpp_sdk.ClientConfigManager().get().dict()
        client_config_data = infy_gen_ai_sdk.ClientConfigData(
            **client_config_data_dict)
        infy_gen_ai_sdk.ClientConfigManager().load(client_config_data)

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        processor_response_data = infy_dpp_sdk.data.ProcessorResponseData()
        __processor_config_data = config_data.get('Reader', {})
        document_id = document_data.document_id
        vector_storage, sparse_storage = "", ""
        batch_size = ""
        get_llm = ""
        get_llm_config = {}
        used_cache = False
        moderation_config = {}
        moderation_payload = {}
        moderation_results = {}
        moderation_status = "PASSED"
        moderation_enabled = False
        vector_enabled, sparse_enabled, rrf_enabled = False, False, False

        for key, value in __processor_config_data.items():
            if key == 'llm':
                for e_key, e_val in value.items():
                    if e_key == 'openai':
                        if e_val.get('enabled'):
                            get_llm = e_key
                            get_llm_config = e_val.get('configuration')
                            break
                    elif e_key == 'llama-3-1':
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
                    elif e_key == 'models':
                        for model in e_val:
                            if model.get('enabled'):
                                get_llm = e_key
                                get_llm_config = model.get('configuration')
                                batch_size = model.get('batch').get('size')
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
        deployment_name = ''
        vector_types = ['faiss', 'elasticsearch']
        sparse_types = ['bm25s', 'infy_db_service']
        if get_llm == 'openai' and (vector_storage in vector_types or sparse_storage in sparse_types):
            os.environ["TIKTOKEN_CACHE_DIR"] = get_llm_config['tiktoken_cache_dir']
            llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAILlmProviderConfigData(
                **get_llm_config)
            llm_provider = infy_gen_ai_sdk.llm.provider.OpenAILlmProvider(
                llm_provider_config_data)
            cache_enabled = __processor_config_data.get('llm').get('openai'
                                                                   ).get('cache').get('enabled')
            model_name = llm_provider_config_data.model_name
            deployment_name = llm_provider_config_data.deployment_name
        if get_llm == 'custom' and (vector_storage in vector_types or sparse_storage in sparse_types):
            llm_provider_config_data = CustomLlmProviderConfigData(
                **get_llm_config)
            llm_provider = CustomLlmProvider(
                llm_provider_config_data, json_payload_dict, custom_llm_name, self.__file_sys_handler, self.__logger, self.__app_config)
            cache_enabled = False
            model_name = custom_llm_name
        if get_llm == 'llama-3-1' and (vector_storage in vector_types or sparse_storage in sparse_types):
            llm_provider_config_data = LlamaLlmProviderConfigData(
                **get_llm_config)
            llm_provider = LlamaLlmProvider(
                llm_provider_config_data, self.__file_sys_handler, self.__logger, self.__app_config)
            cache_enabled = False
            model_name = llm_provider_config_data.model_name
            deployment_name = llm_provider_config_data.deployment_name
        if get_llm == 'models' and (vector_storage in vector_types or sparse_storage in sparse_types):
            # os.environ["TIKTOKEN_CACHE_DIR"] = get_llm_config['tiktoken_cache_dir']
            llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
                **get_llm_config)
            llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
                llm_provider_config_data)
            cache_enabled = False
            model_name = llm_provider_config_data.model_name
            deployment_name = llm_provider_config_data.deployment_name

        context_data = context_data if context_data else {}
        # QUERY RETRIEVER VALIDATION  HANDLED#
        if context_data.get('query_retriever').get('error'):
            message_data = infy_dpp_sdk.data.MessageData()
            message_item_data = infy_dpp_sdk.data.MessageItemData(
            message_code=infy_dpp_sdk.data.MessageCodeEnum.SERVER_ERR_UNHANDLED_EXCEPTION,
            message_type=infy_dpp_sdk.data.MessageTypeEnum.ERROR,
            message_text= context_data.get('query_retriever').get('error'))
            message_data.messages.append(message_item_data)
            
            processor_response_data.message_data = message_data
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
        model_based_prompt_list = __processor_config_data.get('model_based_prompts', [])
        output_list = []
        request_data_list = []
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
            key_occurrences = {}
            for match in top_k_matches_list[:reader_input_list[0]['top_k']]:
                custom_metadata = match.get('meta_data', {}).get('custom_metadata', {})
                for key in custom_metadata.keys():
                    if key in key_occurrences:
                        key_occurrences[key] += 1
                    else:
                        key_occurrences[key] = 1

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
                    custom_metadata = meta_data.get('custom_metadata',{})
                    f_file = match.get("content")
                    # template = re.sub(
                    #     '{chunk_text}', re.escape(f_file), v)
                    template = v.replace('{chunk_text}', f_file)
                    unique_custom_metadata = {key: value for key, value in custom_metadata.items() if key_occurrences[key] < len(top_k_matches_list[:reader_input_list[0]['top_k']])}
                    unique_custom_metadata_str = ";".join([f"{key}:{value}" for key, value in unique_custom_metadata.items()])
                    if not unique_custom_metadata_str:
                        unique_custom_metadata_str = ""
                    if not remain_repl_words_list:
                        comb_file_content = comb_file_content + template
                    else:
                        for replace_word in remain_repl_words_list:
                            if replace_word == 'custom_metadata':
                                template = template.replace(f'{{{replace_word}}}', unique_custom_metadata_str)
                            else:
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
                    if input.get('use_model_based_prompts', False):  
                        selected_prompt_template = None
                        for model_prompt in model_based_prompt_list:
                            if model_name in model_prompt['model_name']:
                                selected_prompt_template = model_prompt['prompt_template']
                                break

                        if not selected_prompt_template or selected_prompt_template not in named_propt_temp_dict:
                            selected_prompt_template = input['prompt_template']
                            self.__logger.debug(f'Prompt template not found for model {model_name}, selecting default prompt template {selected_prompt_template}')
                            

                        templ_prompt_list = named_propt_temp_dict[selected_prompt_template].get(
                            'content', [])
                        context_template_name = named_propt_temp_dict[selected_prompt_template].get(
                            'context_template', '')
                        combined_text = combined_files_dict[context_template_name]

                        if len(templ_prompt_list) < 1:
                            file_path = named_propt_temp_dict[selected_prompt_template].get(
                                'file_path', None)
                            if file_path:
                                template_str = self.__file_sys_handler.read_file(file_path)
                            else:
                                template_str = ''.join(templ_prompt_list)
                        else:
                            template_str = ''.join(templ_prompt_list)

                        response_validation = named_propt_temp_dict[selected_prompt_template].get(
                            'response_validation', {})
                    else:
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
                        "qr_attr_key": qr_attr_key,
                        "prompt_template": PROMPT_TEMPLATE,
                        "template_var_to_value_dict": {
                            'context': CONTEXT,
                            'question': QUESTION
                        }
                    }

                    request_data_list.append(request_data_dict)

        if get_llm == 'models' and batch_size > 1 and len(request_data_list) > 1:
            request_handler_obj = LLMBatchRequestHandler(
                self.__file_sys_handler, self.__app_config, self.__logger, llm_provider, get_llm, get_llm_config, __processor_config_data, cache_enabled, moderation_enabled, moderation_config, moderation_payload, response_validation, batch_size)
        else:
            request_handler_obj = LLMSequenceRequestHandler(
                self.__file_sys_handler, self.__app_config, self.__logger, llm_provider, get_llm, get_llm_config, __processor_config_data, cache_enabled, moderation_enabled, moderation_config, moderation_payload, response_validation)

        llm_response_list = request_handler_obj.get_response(
            request_data_list)

        for llm_response_json in llm_response_list:
            answer = llm_response_json.get('llm_response')
            llm_attempts = llm_response_json.get('llm_attempts')
            max_attempts = llm_response_json.get('max_attempts')
            retriever_output = {"top_k": reader_input_list[0]['top_k']}
            ques_attr_key = llm_response_json.get('qr_attr_key')
            request_dict = llm_response_json.get('request_data_dict')
            moderation_results = llm_response_json.get('moderation_results')
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
            except Exception:
                pass
            output_list.append({
                "attribute_key": ques_attr_key,
                "retriever_output": retriever_output,
                "model_name": deployment_name,
                "total_attempts": min(llm_attempts, max_attempts),
                "model_input": request_dict,
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
