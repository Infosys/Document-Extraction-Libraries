# ===============================================================================================================#
# Copyright 2025 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
from collections import Counter
import infy_dpp_sdk
from infy_dpp_sdk.data.message_data import MessageData
from infy_dpp_sdk.data.document_data import DocumentData
from infy_dpp_sdk.data.processor_response_data import ProcessorResponseData
import infy_gen_ai_sdk
from ...common.string_util import StringUtil


class MetadataExtractorCustom(infy_dpp_sdk.interface.IProcessor):

    def __init__(self) -> None:
        self.__file_sys_handler = self.get_fs_handler()
        self.__app_config = self.get_app_config()
        self.__logger = self.get_logger()

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        processor_response_data = infy_dpp_sdk.data.ProcessorResponseData()
        PROCESSEOR_CONTEXT_DATA_NAME = ""
        __processor_config_data = config_data.get(
            'MetadataExtractorCustom', {})
        retriever_config = config_data.get(
            'QueryRetriever', {})
        chunk_generator_data = context_data.get('chunk_generator', {})
        document_id = document_data.document_id
        page_st, page_end = 1, 1
        batch_size, get_llm, final_answer, decider_prompt_path, mde_technique, db_name, query_prompt_path, question_technique, header_prefix, footer_prefix = "", "", "", "", "", "", "", "", "", ""
        vector_db_provider, get_llm_config = {}, {}
        llm_request_data_list, llm_response_data_list, answers_list, model_based_prompt_list = [], [], [], []
        segment_list, header_list, footer_list = [], [], []
        custom_metadata, embedding_provider, mde_technique_config = {}, {}, {}
        used_cache = False
        optimize_llm = False
        use_header_footer = False

        # parse config
        for mde_type, mde_config in __processor_config_data.items():
            if mde_type == 'document' and mde_config.get('enabled'):
                mde_technique = 'document'
                mde_technique_config = mde_config
                for key, value in mde_config.items():
                    if key == 'page':
                        page_value = value
                        if ':' in page_value:
                            page_st, page_end = map(
                                int, page_value.split(':'))
                        else:
                            page_st = page_end = int(page_value)

                    if key == 'llm':
                        for e_key, e_val in value.items():
                            if e_key == 'models':
                                for model in e_val:
                                    if model.get('enabled'):
                                        get_llm = e_key
                                        get_llm_config = model.get(
                                            'configuration')
                                        batch_size = model.get(
                                            'batch').get('size')
                                        break

                    if key == 'decider_prompt_path':
                        decider_prompt_path = value

                    if key == 'optimize_llm':
                        optimize_llm = value.get('enabled', False)
                        optimized_llm_prompt_path = value.get(
                            'prompt_path', '')

                    if key == 'header_footer':
                        for e_key, e_val in value.items():
                            if e_key == 'enabled' and e_val is True:
                                use_header_footer = True
                                header_prefix = value.get('header_prefix', 'Header:')
                                footer_prefix = value.get('footer_prefix', 'Footer:')
                                segment_list = context_data.get('segment_classifier').get(
                                    'segment_data')[0].get('segments')
                                header_list = [segment for segment in segment_list if segment.get(
                                    'content_type') == 'header']
                                footer_list = [segment for segment in segment_list if segment.get(
                                    'content_type') == 'footer']

                    if key == 'model_based_prompts':
                        model_based_prompt_list = value
            
            elif mde_type == 'query' and mde_config.get('enabled'):
                mde_technique = 'query'
                mde_technique_config = mde_config
                for key, value in mde_config.items():
                    if key == 'llm':
                        for e_key, e_val in value.items():
                            if e_key == 'models':
                                for model in e_val:
                                    if model.get('enabled'):
                                        get_llm = e_key
                                        get_llm_config = model.get(
                                            'configuration')
                                        batch_size = model.get(
                                            'batch').get('size')
                                        break

                    if key == 'storage':
                        for storage_key, storage_value in value.items():
                            if storage_key == 'vectordb':
                                for e_key, e_val in storage_value.items():
                                    if e_val.get('enabled'):
                                        vector_enabled = True
                                        vector_storage = e_key
                                        vector_storage_config = e_val.get(
                                            'configuration', {})
                                        encoded_files_root_path = vector_storage_config.get(
                                            "encoded_files_root_path", '')
                                        chunked_files_root_path = vector_storage_config.get(
                                            "chunked_files_root_path", '')
                                        db_name = vector_storage_config.get(
                                            "db_name", '')
                                        vector_collections = vector_storage_config.get(
                                            "collections", [])
                                        distance_metric = vector_storage_config.get(
                                            "distance_metric", {})
                                        index_id = vector_storage_config.get(
                                            "index_id", '')
                                        if distance_metric is not None:
                                            for key, value in distance_metric.items():
                                                if value is True:
                                                    distance_metric = key
                                                    break

                    if key == 'query_prompt':
                        query_rewriting = value.get('query_rewriting', {})
                        if query_rewriting.get('enabled', False):
                            query_prompt_path = query_rewriting.get('prompt_path', '')
                        else:
                            query_prompt_path = value.get('prompt_path', '')
                        use_model_based_prompts = query_rewriting.get('use_model_based_prompts', False)
                        model_based_prompt_list = value.get('model_based_prompts', [])

                    if key == 'embedding':
                        for e_key, e_val in value.items():
                            if e_val.get('enabled'):
                                get_embedding = e_key
                                get_emb_config = e_val.get('configuration')
                                embed_model_name = get_emb_config.get(
                                    "model_name")
                                sub_folder_name = f'{get_embedding}-{embed_model_name}'

        # set llm provider
        if get_llm == 'models':
            llm_provider_config_data = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProviderConfigData(
                **get_llm_config)
            llm_provider = infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmProvider(
                llm_provider_config_data)
            cache_enabled = False
            model_name = llm_provider_config_data.model_name
            deployment_name = llm_provider_config_data.deployment_name

        # Document Mode: Extract metadata from from context based on questions and add them as custom_metadata field
        if mde_technique == 'document':
            self.__logger.debug(f"MetadataExtractorCustom Type: Document")
            self.__logger.debug(f"MetadataExtractorCustom LLM: {model_name}")
            PROCESSEOR_CONTEXT_DATA_NAME = "metadata_extractor_custom_document"
            chunk_data, chunked_data, chunk_generator_data_technique = {}, {}, {}
            if 'page' in chunk_generator_data:
                chunk_generator_data_technique = chunk_generator_data['page']
                chunked_data = chunk_generator_data_technique.get(
                    'chunked_data', {})
            elif 'page_character' in chunk_generator_data:
                chunk_generator_data_technique = chunk_generator_data['page_character']
                chunked_data = chunk_generator_data_technique.get(
                    'chunked_data', {})
            elif 'segment' in chunk_generator_data:
                chunk_generator_data_technique = chunk_generator_data['segment']
                chunked_data = chunk_generator_data_technique.get(
                    'chunked_data', {})
            page_keys = list(chunked_data.keys())
            for i, page_num in enumerate(range(page_st, page_end + 1)):
                if i < len(page_keys):
                    chunk_data[f'page_{page_num}'] = chunked_data[page_keys[i]]
                    
            if use_header_footer:
                for page_num in range(page_st, page_end + 1):
                    page_key = f'page_{page_num}'
                    if page_key in chunk_data:
                        content = chunk_data[page_key]
                        # Add headers
                        headers = [header['content'] for header in header_list if header['page'] == page_num]
                        if headers:
                            content = header_prefix + " " + " ".join(headers) + " " + content
                        # Add footers
                        footers = [footer['content'] for footer in footer_list if footer['page'] == page_num]
                        if footers:
                            content = content + " " + footer_prefix + " " + " ".join(footers)
                            
                        chunk_data[page_key] = content

            query_list = mde_technique_config['query_list']
            if optimize_llm:
                self.__logger.debug(f"MetadataExtractorCustom: Optimized LLM")
                all_questions = ""
                all_questions_keys = []
                for query in query_list:
                    llm_request_data_list, llm_response_data_list, context_list, answers_list = [], [], [], []
                    question = query.get('query')
                    question_key = query.get('query_key')
                    question_technique = query.get('technique')
                    prompt_path = query.get('prompt_path')
                    if question:
                        all_questions += question + " "
                        all_questions_keys.append(question_key)

                for page_key, context in chunk_data.items():
                    CONTEXT = context
                    context_list.append(CONTEXT)
                    PROMPT_TEMPLATE = self.__file_sys_handler.read_file(
                        optimized_llm_prompt_path)
                    request_data_dict = {
                        "prompt_template": PROMPT_TEMPLATE,
                        "template_var_to_value_dict": {
                            'context': CONTEXT,
                            'question': all_questions
                        }
                    }
                    llm_request_data = infy_gen_ai_sdk.llm.provider.OpenAILlmRequestData(
                        **request_data_dict)
                    llm_request_data_list.append(llm_request_data)

                try:
                    llm_response_data_list: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = llm_provider.get_llm_response_batch(
                        llm_request_data_list)
                except Exception as e:
                    llm_response_data = None
                    self.__logger.error(
                        f"MetadataExtractorCustom: Error in LLM response: {e}")
                    
                    message_data = infy_dpp_sdk.data.MessageData()
                    message_item_data = infy_dpp_sdk.data.MessageItemData(
                    message_code=infy_dpp_sdk.data.MessageCodeEnum.SERVER_ERR_UNHANDLED_EXCEPTION,
                    message_type=infy_dpp_sdk.data.MessageTypeEnum.ERROR,
                    message_text= f"Error in LLM response: {e}")
                    message_data.messages.append(message_item_data)
                    
                    processor_response_data.message_data = message_data
                    processor_response_data.document_data = document_data
                    processor_response_data.context_data = context_data
                    return processor_response_data

                if question_technique == "metadata_extraction_technique_1":
                    for llm_response_data in llm_response_data_list:
                        llm_response_txt = llm_response_data.llm_response_txt
                        llm_response_json = StringUtil.parse_string_to_json(llm_response_txt)
                        if isinstance(llm_response_json, dict):
                            call_answers = {}
                            for i, (key, value) in enumerate(llm_response_json.items()):
                                if i < len(all_questions_keys):
                                    call_answers[all_questions_keys[i]] = value
                            answers_list.append(call_answers)

                    if answers_list:
                        key_value_counts = {}
                        for call_answers in answers_list:
                            for key, value in call_answers.items():
                                if key not in key_value_counts:
                                    key_value_counts[key] = {}
                                if value not in key_value_counts[key]:
                                    key_value_counts[key][value] = 0
                                key_value_counts[key][value] += 1
                        for key, value_counts in key_value_counts.items():
                            total_count = sum(value_counts.values())
                            found = False
                            for value, count in value_counts.items():
                                if count >= total_count / 2:
                                    custom_metadata[key] = value
                                    found = True
                                    break
                        if not found:
                            self.__logger.debug(f"MetadataExtractorCustom: No answers found")
                    else:
                        self.__logger.debug(f"MetadataExtractorCustom: No answers found")

            elif not optimize_llm:
                self.__logger.debug(f"MetadataExtractorCustom: Regular LLM")
                for query in query_list:
                    llm_request_data_list, llm_response_data_list, context_list, answers_list = [], [], [], []
                    question = query.get('query')
                    question_key = query.get('query_key')
                    question_technique = query.get('technique')
                    prompt_path = query.get('prompt_path')
                    use_model_based_prompts = query.get('use_model_based_prompts', False)

                    if use_model_based_prompts:
                        selected_prompt_template = None
                        for model_prompt in model_based_prompt_list:
                            if model_name in model_prompt['model_name']:
                                selected_prompt_template = model_prompt['prompt_template']
                                break

                        if not selected_prompt_template:
                            self.__logger.debug(f"No matching prompt found for model: {model_name}. Falling back to default prompt.")
                            selected_prompt_template = prompt_path
                    else:
                        selected_prompt_template = prompt_path

                    PROMPT_TEMPLATE = self.__file_sys_handler.read_file(selected_prompt_template)
                    
                    for page_key, context in chunk_data.items():
                        CONTEXT = context
                        context_list.append(CONTEXT)
                        request_data_dict = {
                            "prompt_template": PROMPT_TEMPLATE,
                            "template_var_to_value_dict": {
                                'context': CONTEXT,
                                'question': question
                            }
                        }
                        llm_request_data = infy_gen_ai_sdk.llm.provider.OpenAILlmRequestData(
                            **request_data_dict)
                        llm_request_data_list.append(llm_request_data)

                    try:
                        llm_response_data_list: infy_gen_ai_sdk.llm.provider.OpenAIFormatLlmResponseData = llm_provider.get_llm_response_batch(
                            llm_request_data_list)
                    except Exception as e:
                        llm_response_data = None
                        self.__logger.error(
                            f"MetadataExtractorCustom: Error in LLM response: {e}")
                        
                        message_data = infy_dpp_sdk.data.MessageData()
                        message_item_data = infy_dpp_sdk.data.MessageItemData(
                        message_code=infy_dpp_sdk.data.MessageCodeEnum.SERVER_ERR_UNHANDLED_EXCEPTION,
                        message_type=infy_dpp_sdk.data.MessageTypeEnum.ERROR,
                        message_text= f"Error in LLM response: {e}")
                        message_data.messages.append(message_item_data)
                        
                        processor_response_data.message_data = message_data
                        processor_response_data.document_data = document_data
                        processor_response_data.context_data = context_data
                        return processor_response_data

                    if question_technique == "metadata_extraction_technique_1":
                        for llm_response_data in llm_response_data_list:
                            llm_response_txt = llm_response_data.llm_response_txt
                            llm_response_json = StringUtil.parse_string_to_json(llm_response_txt)
                            if isinstance(llm_response_json, dict):
                                answer = llm_response_json['answer']
                                if answer not in [None, '', 'null']:
                                    answers_list.append(answer)
                            else:
                                self.__logger.debug(f"MetadataExtractorCustom: No answers found")
                                answers_list = []

                        if answers_list:
                            answer_counts = Counter(answers_list)
                            most_common_answer, count = answer_counts.most_common(1)[
                                0]
                            if count > 1 and count >= len(answers_list) // 2:
                                final_answer = most_common_answer
                            else:
                                self.__logger.debug(
                                    f"MetadataExtractorCustom: Decider Prompt")
                                # Create a new prompt using prompt_2
                                PROMPT_TEMPLATE_DECIDER = self.__file_sys_handler.read_file(
                                    decider_prompt_path)
                                answers_str = "\n".join(answers_list)
                                prompt_template = PROMPT_TEMPLATE_DECIDER.replace(
                                    "{answers}", answers_str)

                                combined_context = " ".join(context_list)
                                request_data_dict_decider = {
                                    "prompt_template": prompt_template,
                                    "template_var_to_value_dict": {
                                        'context': combined_context,
                                        'question': question
                                    }
                                }
                                decider_llm_request_data = infy_gen_ai_sdk.llm.provider.OpenAILlmRequestData(
                                    **request_data_dict_decider)
                                decider_llm_response_data = llm_provider.get_llm_response(
                                    decider_llm_request_data)
                                decider_llm_response_txt = decider_llm_response_data.llm_response_txt
                                decider_llm_response_json = StringUtil.parse_string_to_json(decider_llm_response_txt)

                                if isinstance(decider_llm_response_json, dict):
                                    if 'answer' in decider_llm_response_json:
                                        final_answer = decider_llm_response_json['answer']
                                    else:
                                        final_answer = None
                                else:
                                    final_answer = None               
                        else:
                            self.__logger.debug(f"MetadataExtractorCustom: No answers found")
                            final_answer = None

                        custom_metadata[question_key] = final_answer

            # set metadata in chunk_datac
            self.__logger.debug(f"MetadataExtractorCustom: Extracted metadata={custom_metadata}")
            chunked_file_meta_data_list = chunk_generator_data_technique.get(
                'chunked_file_meta_data_list', [])
            output_obj = {'chunked_file_meta_data_list': []}
            for file_path in chunked_file_meta_data_list:
                curr_metadata = json.loads(
                    self.__file_sys_handler.read_file(file_path))
                curr_metadata['custom_metadata'] = custom_metadata
                updated_metadata = json.dumps(curr_metadata, indent=4)
                self.__file_sys_handler.write_file(file_path, updated_metadata)
                output_obj['chunked_file_meta_data_list'].append(file_path)
                output_obj['custom_metadata'] = custom_metadata
        
        # Query Mode: Extract metadata from questions and use that for filtering
        elif mde_technique == 'query':
            self.__logger.debug(f"MetadataExtractorCustom Type: Query")
            PROCESSEOR_CONTEXT_DATA_NAME = "metadata_extractor_custom_query"
            # set dummy embedding provider
            embedding_provider_config_data_dict = get_emb_config if get_emb_config else {}
            if sub_folder_name == f'sentence_transformer-{embed_model_name}' and get_embedding == 'sentence_transformer' and vector_storage == 'faiss':
                embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.StEmbeddingProviderConfigData(
                    **embedding_provider_config_data_dict)
                embedding_provider = infy_gen_ai_sdk.embedding.provider.StEmbeddingProvider(
                    embedding_provider_config_data)
            if sub_folder_name == f'openai-{embed_model_name}' and get_embedding == 'openai' and vector_storage == 'faiss':
                os.environ["TIKTOKEN_CACHE_DIR"] = embedding_provider_config_data_dict['tiktoken_cache_dir']
                embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProviderConfigData(
                    **embedding_provider_config_data_dict)
                embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProvider(
                    embedding_provider_config_data)
            if sub_folder_name == f'custom-{embed_model_name}' and get_embedding == 'custom' and vector_storage == 'faiss':
                embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProviderConfigData(
                    **embedding_provider_config_data_dict)
                embedding_provider = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProvider(
                    embedding_provider_config_data)

            if db_name:
                server_faiss_write_path = f'{encoded_files_root_path}/{get_embedding}-{embed_model_name}/{db_name}'
            else:
                server_faiss_write_path = f'{encoded_files_root_path}/{get_embedding}-{embed_model_name}/{document_id}'
            if index_id:
                server_faiss_write_path = f'{server_faiss_write_path}/{index_id}'

            if vector_collections:
                for collection in vector_collections:
                    # Step 2 - Choose vector db provider
                    if vector_storage == 'faiss':
                        vector_db_provider_config_data_dict = {
                            'db_folder_path': server_faiss_write_path,
                            'db_index_name': collection.get('collection_name', db_name) or document_id,
                            'db_index_secret_key': collection.get('collection_secret_key', '')
                        }
                        vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbProviderConfigData(
                            **vector_db_provider_config_data_dict)
                        vector_db_provider = infy_gen_ai_sdk.vectordb.provider.faiss.FaissVectorDbProvider(
                            vector_db_provider_config_data, embedding_provider)
                    elif vector_storage == 'infy_db_service':
                        model_name_embed = vector_storage_config.get(
                            'model_name', '')
                        vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.online.OnlineVectorDbProviderConfigData(
                            **{
                                'db_service_url': vector_storage_config.get('db_service_url', ''),
                                'model_name': model_name_embed,
                                'index_id': index_id,
                                "collection_name": collection.get('collection_name', ''),
                                "collection_secret_key": collection.get('collection_secret_key', '')
                            })
                        vector_db_provider = infy_gen_ai_sdk.vectordb.provider.online.OnlineVectorDbProvider(
                            vector_db_provider_config_data)
            custom_metadata_dict = vector_db_provider.get_custom_metadata()
            for key in custom_metadata_dict:
                if custom_metadata_dict[key] == "":
                    custom_metadata_dict[key] = []
            custom_metadata_schema = json.dumps(custom_metadata_dict)
            
            # send combined questions to llm to fill the custom_metadata schema
            all_questions = ""
            query_list = retriever_config['queries'] if retriever_config else []
            for query in query_list:
                llm_request_data_list, llm_response_data_list, context_list, answers_list = [], [], [], []
                question = query.get('question')
                if question:
                    all_questions += question + ";"
                    
            selected_prompt_template = None
            if use_model_based_prompts and model_based_prompt_list:
                for model_prompt in model_based_prompt_list:
                    if model_name in model_prompt['model_name']:
                        selected_prompt_template = model_prompt['prompt_template']
                        break
                if not selected_prompt_template:
                    self.__logger.debug(f"No matching prompt found for model: {model_name}. Falling back to default query prompt.")
                    selected_prompt_template = query_prompt_path
            else:
                selected_prompt_template = query_prompt_path

            # set llm request
            PROMPT_TEMPLATE = self.__file_sys_handler.read_file(
                selected_prompt_template)
            PROMPT_TEMPLATE = PROMPT_TEMPLATE.replace(
                '{questions}', all_questions)
            PROMPT_TEMPLATE = PROMPT_TEMPLATE.replace(
                '{custom_metadata}', custom_metadata_schema)
            request_data_dict = {
                "prompt_template": PROMPT_TEMPLATE,
                "template_var_to_value_dict": {
                    'context': None,
                    'question': None
                }
            }
            try:
                llm_request_data = infy_gen_ai_sdk.llm.provider.OpenAILlmRequestData(
                    **request_data_dict)
                llm_response_data = llm_provider.get_llm_response(
                    llm_request_data)
            except Exception as e:
                llm_response_data = None
                self.__logger.error(
                    f"MetadataExtractorCustom: Error in LLM response: {e}")
                
                message_data = infy_dpp_sdk.data.MessageData()
                message_item_data = infy_dpp_sdk.data.MessageItemData(
                message_code=infy_dpp_sdk.data.MessageCodeEnum.SERVER_ERR_UNHANDLED_EXCEPTION,
                message_type=infy_dpp_sdk.data.MessageTypeEnum.ERROR,
                message_text= f"Error in LLM response: {e}")
                message_data.messages.append(message_item_data)
                
                processor_response_data.message_data = message_data
                processor_response_data.document_data = document_data
                processor_response_data.context_data = context_data
                return processor_response_data
                
            llm_response_txt = llm_response_data.llm_response_txt
            llm_response_txt_json = StringUtil.parse_string_to_json(llm_response_txt)
                            
            output_obj = []
            if isinstance(llm_response_txt_json, dict):
                rewritten_questions = llm_response_txt_json.get('questions', [])
                custom_metadata = llm_response_txt_json.get('custom_metadata', llm_response_txt_json)
                self.__logger.debug(f"rewritten_questions: {rewritten_questions}")
                self.__logger.debug(f"custom_metadata: {custom_metadata}")
            else:
                rewritten_questions = []
                custom_metadata = {}
                self.__logger.error(
                    f"MetadataExtractorCustom: Metadata not extracted in proper format, please try again")
                
                message_data = infy_dpp_sdk.data.MessageData()
                message_item_data = infy_dpp_sdk.data.MessageItemData(
                message_code=infy_dpp_sdk.data.MessageCodeEnum.SERVER_ERR_UNHANDLED_EXCEPTION,
                message_type=infy_dpp_sdk.data.MessageTypeEnum.ERROR,
                message_text= f"Metadata not extracted in proper format, please try again")
                message_data.messages.append(message_item_data)
                
                processor_response_data.message_data = message_data
                processor_response_data.document_data = document_data
                processor_response_data.context_data = context_data
                return processor_response_data


            for i, query in enumerate(query_list):
                question = query.get('question')
                attribute_key = query.get('attribute_key')
                revised_question = rewritten_questions[i] if (rewritten_questions) else question
                output_obj.append({
                    'attribute_key': attribute_key,
                    'question': question,
                    'revised_question': revised_question,
                    'custom_metadata': custom_metadata
                })

        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = output_obj
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data
        return processor_response_data
