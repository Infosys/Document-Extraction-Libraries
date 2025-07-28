# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
from typing import List
from elasticsearch import Elasticsearch
import infy_dpp_sdk
import infy_gen_ai_sdk
from infy_dpp_sdk.data import MessageData, ProcessorResponseData


class QueryVectordb():
    def __init__(self, file_sys_handler, logger, app_config):
        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = file_sys_handler

    def query_vectordb(self, PROCESSOR_CONTEXT_DATA_NAME, processor_response_data, processor_config_data, context_data, document_data,  document_id):

        vector_enabled, use_mde_schema = False, False
        mde_schema = {}
        mde_response_list = context_data.get(
            'metadata_extractor_custom_query', {})
        for key, value in processor_config_data.items():
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

        if vector_enabled:
            if mde_response_list and len(mde_response_list[0].get('custom_metadata'))>0:
                use_mde_schema = True
                metadata_schema = mde_response_list[0].get(
                    'custom_metadata')
                if isinstance(metadata_schema, dict):
                    for key, value in metadata_schema.items():
                        if isinstance(value, list):  
                            filtered_values = [v for v in value if v]
                            if filtered_values:  
                                modified_key = f'custom_metadata.{key}'
                                mde_schema[modified_key] = filtered_values
                else:
                    metadata_schema = {}
                    use_mde_schema = False
            else:
                metadata_schema = {}
                use_mde_schema = False
                    
            if vector_storage == 'faiss':
                if not db_name:
                    doc_work_folder_abs_path_list = self.__file_sys_handler.list_files(
                        encoded_files_root_path, f'/*/{document_id}')
                    # VALIDATION 1 #
                    if len(doc_work_folder_abs_path_list) == 0:
                        message_data = infy_dpp_sdk.data.MessageData()
                        message_item_data = infy_dpp_sdk.data.MessageItemData(
                        message_code=infy_dpp_sdk.data.MessageCodeEnum.SERVER_ERR_UNHANDLED_EXCEPTION,
                        message_type=infy_dpp_sdk.data.MessageTypeEnum.ERROR,
                        message_text= f"ERROR: Document work folder for {document_id} not found.")
                        message_data.messages.append(message_item_data)
                        
                        processor_response_data.message_data = message_data
                        context_data[PROCESSOR_CONTEXT_DATA_NAME] = {
                            'error': f"ERROR: Document work folder for {document_id} not found."}
                        processor_response_data.document_data = document_data
                        processor_response_data.context_data = context_data
                        return processor_response_data
                    # VALIDATION 1 END#
                    sub_folder_name = os.path.basename(
                        os.path.dirname(f'{doc_work_folder_abs_path_list[0]}'))
                for key, value in processor_config_data.items():
                    if key == 'embedding':
                        for e_key, e_val in value.items():
                            if db_name:
                                if e_val.get('enabled'):
                                    get_embedding = e_key
                                    get_emb_config = e_val.get('configuration')
                                    model_name = get_emb_config.get(
                                        "model_name")
                                    sub_folder_name = f'{get_embedding}-{model_name}'
                            elif f'{e_key}-{e_val.get("configuration").get("model_name")}' == sub_folder_name:
                                if e_val.get('enabled'):
                                    get_embedding = e_key
                                    get_emb_config = e_val.get('configuration')
                                    model_name = get_emb_config.get(
                                        "model_name")
                if not db_name:
                    server_chunked_files_list = [
                        f'{chunked_files_root_path}/{document_id}']

                    def __get_files(request_file_path_list):
                        path_list = []
                        for request_file_path in request_file_path_list:
                            files_list = self.__file_sys_handler.list_files(
                                request_file_path)
                            for file in files_list:
                                path_list.append(file)
                                path_list = list(set(path_list))
                        return path_list
                    chunked_files_path_list = __get_files(
                        server_chunked_files_list)
                # VALIDATION 2  #
                    if len(chunked_files_path_list) == 0:
                        message_data = infy_dpp_sdk.data.MessageData()
                        message_item_data = infy_dpp_sdk.data.MessageItemData(
                        message_code=infy_dpp_sdk.data.MessageCodeEnum.SERVER_ERR_UNHANDLED_EXCEPTION,
                        message_type=infy_dpp_sdk.data.MessageTypeEnum.ERROR,
                        message_text= f"ERROR: Chunk files don't exist for doc_work_folder_id {document_id}.")
                        message_data.messages.append(message_item_data)
                        processor_response_data.message_data = message_data
                        context_data[PROCESSOR_CONTEXT_DATA_NAME] = {
                            'error': f"ERROR: Chunk files don't exist for doc_work_folder_id {document_id}."}
                        processor_response_data.document_data = document_data
                        processor_response_data.context_data = context_data
                        return processor_response_data
                # VALIDATION 2 END#
                # Step 1 - Choose embedding provider
                embedding_provider_config_data_dict = get_emb_config if get_emb_config else {}
                if sub_folder_name == f'sentence_transformer-{model_name}' and get_embedding == 'sentence_transformer' and vector_storage == 'faiss':
                    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.StEmbeddingProviderConfigData(
                        **embedding_provider_config_data_dict)

                    embedding_provider = infy_gen_ai_sdk.embedding.provider.StEmbeddingProvider(
                        embedding_provider_config_data)
                if sub_folder_name == f'openai-{model_name}' and get_embedding == 'openai' and vector_storage == 'faiss':
                    os.environ["TIKTOKEN_CACHE_DIR"] = embedding_provider_config_data_dict['tiktoken_cache_dir']
                    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProviderConfigData(
                        **embedding_provider_config_data_dict)

                    embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProvider(
                        embedding_provider_config_data)
                if sub_folder_name == f'custom-{model_name}' and get_embedding == 'custom' and vector_storage == 'faiss':
                    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProviderConfigData(
                        **embedding_provider_config_data_dict)

                    embedding_provider = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProvider(
                        embedding_provider_config_data)

                if db_name:
                    server_faiss_write_path = f'{encoded_files_root_path}/{get_embedding}-{model_name}/{db_name}'
                else:
                    server_faiss_write_path = f'{encoded_files_root_path}/{get_embedding}-{model_name}/{document_id}'

                if index_id:
                    server_faiss_write_path = f'{server_faiss_write_path}/{index_id}'
            elif vector_storage == 'elasticsearch':
                if 'ca_certs_path' in vector_storage_config:
                    os.environ["CA_CERTS_PATH"] = vector_storage_config['ca_certs_path']
                # check if index exists, if so get the model name
                es_util = self.ElasticsearchUtility(
                    vector_storage_config, index_id)
                index_exists = es_util.check_index_exists()
                if index_exists:
                    model_name = es_util.get_model_name()
                    for key, value in processor_config_data.items():
                        if key == 'embedding':
                            for e_key, e_val in value.items():
                                if model_name == e_val.get('configuration').get('model_name'):
                                    e_val['enabled'] = True
                                    get_embedding = e_key
                                    get_emb_config = e_val.get('configuration')
                                    sub_folder_name = f'{get_embedding}-{model_name}'
                                else:
                                    e_val['enabled'] = False

                    embedding_provider_config_data_dict = get_emb_config if get_emb_config else {}
                    if 'tiktoken_cache_dir' in embedding_provider_config_data_dict:
                        os.environ["TIKTOKEN_CACHE_DIR"] = embedding_provider_config_data_dict['tiktoken_cache_dir']
                    # select the embedding provider
                    if sub_folder_name == f'sentence_transformer-{model_name}' and get_embedding == 'sentence_transformer' and vector_storage == 'elasticsearch':
                        embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.StEmbeddingProviderConfigData(
                            **embedding_provider_config_data_dict)
                        embedding_provider = infy_gen_ai_sdk.embedding.provider.StEmbeddingProvider(
                            embedding_provider_config_data)
                    if sub_folder_name == f'openai-{model_name}' and get_embedding == 'openai' and vector_storage == 'elasticsearch':
                        embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProviderConfigData(
                            **embedding_provider_config_data_dict)
                        embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProvider(
                            embedding_provider_config_data)
                    if sub_folder_name == f'custom-{model_name}' and get_embedding == 'custom' and vector_storage == 'elasticsearch':
                        embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProviderConfigData(
                            **embedding_provider_config_data_dict)
                        embedding_provider = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProvider(
                            embedding_provider_config_data)

                else:
                    message_data = infy_dpp_sdk.data.MessageData()
                    message_item_data = infy_dpp_sdk.data.MessageItemData(
                    message_code=infy_dpp_sdk.data.MessageCodeEnum.SERVER_ERR_UNHANDLED_EXCEPTION,
                    message_type=infy_dpp_sdk.data.MessageTypeEnum.ERROR,
                    message_text= f"ERROR: Index {index_id} not found.")
                    message_data.messages.append(message_item_data)
                    processor_response_data.message_data = message_data
                    context_data[PROCESSOR_CONTEXT_DATA_NAME] = {
                        'error': f"ERROR: Index {index_id} not found."}
                    processor_response_data.document_data = document_data
                    processor_response_data.context_data = context_data
                    return processor_response_data

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
                        model_name = vector_storage_config.get(
                            'model_name', '')
                        vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.online.OnlineVectorDbProviderConfigData(
                            **{
                                'db_service_url': vector_storage_config.get('db_service_url', ''),
                                'model_name': model_name,
                                'index_id': index_id,
                                "collection_name": collection.get('collection_name', ''),
                                "collection_secret_key": collection.get('collection_secret_key', '')
                            })
                        vector_db_provider = infy_gen_ai_sdk.vectordb.provider.online.OnlineVectorDbProvider(
                            vector_db_provider_config_data)

                    queries_list = []
                    request_creator_context = context_data.get(
                        'request_creator', {})
                    question_config_request_file = request_creator_context.get(
                        'question_config_request_file')
                    if question_config_request_file:
                        # queries_request = FileUtil.load_json(
                        #     self.__file_sys_handler.read_file(question_config_request_file))
                        queries_request = json.loads(self.__file_sys_handler.read_file(
                            question_config_request_file))
                    else:
                        queries_request = processor_config_data['queries']

                    for query_dict in queries_request:
                        query = query_dict['question']
                        attribute_key = query_dict.get('attribute_key')
                        top_result = query_dict['top_k']
                        min_distance = query_dict.get('min_distance', 0)
                        max_distance = query_dict.get('max_distance', None)
                        message = ''
                        
                        # use revised query if its available
                        if use_mde_schema:
                            for mde_response in mde_response_list:
                                if mde_response.get('attribute_key') == attribute_key and mde_response.get('revised_question'):
                                    query = mde_response['revised_question']
                                    break
                        # Step 3 - Run query to get best matches
                        if vector_storage == 'faiss':
                            query_params_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbQueryParamsData(
                                **{
                                    'query': query,
                                    'top_k': top_result,
                                    'pre_filter_fetch_k': query_dict['pre_filter_fetch_k'],
                                    'filter_metadata': mde_schema if use_mde_schema else query_dict['filter_metadata']
                                })
                        elif vector_storage == 'infy_db_service':
                            query_params_data = infy_gen_ai_sdk.vectordb.provider.online.VectorDbQueryParamsData(
                                **{
                                    "query": query,
                                    "top_k": top_result,
                                    "pre_filter_fetch_k": query_dict['pre_filter_fetch_k'],
                                    "filter_metadata": mde_schema if use_mde_schema else query_dict['filter_metadata'],
                                    "min_distance": min_distance,
                                    "max_distance": max_distance
                                })
                        try:
                            if vector_storage == 'faiss':
                                records: List[infy_gen_ai_sdk.vectordb.provider.faiss.MatchingVectorDbRecordData] = vector_db_provider.get_matches(
                                    query_params_data)
                            elif vector_storage == 'infy_db_service':
                                records = vector_db_provider.get_matches(
                                    query_params_data)
                                records = [infy_gen_ai_sdk.vectordb.provider.faiss.MatchingVectorDbRecordData(
                                    **record) for record in records]
                        except Exception as e:
                            print(f"Exception occurred: {e}")
                            self.__logger.error(f"Exception occurred: {e}")
                            if "File doesn't exist" in str(e):
                                message = "No records found. Vector database is empty."
                            else:
                                message = str(e)
                            records = []

                        top_k_matches_list = {"vectordb": []}
                        if not records:
                            top_k_matches_list["vectordb"].append(
                                {"file_path": '',
                                 "score": '',
                                 "min_distance": min_distance,
                                 "max_distance": max_distance,
                                 "content": '',
                                 "meta_data": '',
                                 "message": message})
                        else:
                            for record in records:
                                if (max_distance is None or record.score <= max_distance) and record.score >= min_distance:
                                    top_k_matches_list["vectordb"].append({"file_path": record.db_folder_path,
                                                                           "score": record.score,
                                                                           "min_distance": min_distance,
                                                                           "max_distance": max_distance,
                                                                           "content": record.content,
                                                                           "meta_data": record.metadata
                                                                           })
                            if not top_k_matches_list["vectordb"]:
                                top_k_matches_list["vectordb"].append(
                                    {"file_path": '',
                                     "score": '',
                                     "min_distance": min_distance,
                                     "max_distance": max_distance,
                                     "content": '',
                                     "meta_data": '',
                                     "message": "No records found. Score value not within the range of min_distance and max_distance configured."
                                     })
                        queries_list.append({"attribute_key": query_dict["attribute_key"],
                                            "question": query,
                                             "embedding_model": model_name,
                                             "distance_metric": distance_metric,
                                             "top_k": top_result,
                                             "top_k_matches": top_k_matches_list
                                             })
            else:
                if vector_storage == 'elasticsearch':
                    vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.elasticsearch.VectorDbProviderConfigData(
                        **{
                            "db_server_url": vector_storage_config.get("db_server_url"),
                            "authenticate": vector_storage_config.get("authenticate"),
                            "username": vector_storage_config.get("username"),
                            "password": vector_storage_config.get("password"),
                            "verify_certs": vector_storage_config.get("verify_certs"),
                            "cert_fingerprint": vector_storage_config.get("cert_fingerprint"),
                            "index_id": index_id
                        })
                    vector_db_provider = infy_gen_ai_sdk.vectordb.provider.elasticsearch.ESVectorDbProvider(
                        vector_db_provider_config_data, embedding_provider)
                    queries_list = []
                    request_creator_context = context_data.get(
                        'request_creator', {})
                    question_config_request_file = request_creator_context.get(
                        'question_config_request_file')
                    if question_config_request_file:
                        # queries_request = FileUtil.load_json(
                        #     self.__file_sys_handler.read_file(question_config_request_file))
                        queries_request = json.loads(self.__file_sys_handler.read_file(
                            question_config_request_file))
                    else:
                        queries_request = processor_config_data['queries']

                    for query_dict in queries_request:
                        query = query_dict['question']
                        attribute_key = query_dict.get('attribute_key')
                        top_result = query_dict['top_k']
                        min_distance = query_dict.get('min_distance', 0)
                        max_distance = query_dict.get('max_distance', None)
                        message = ''
                        
                        if use_mde_schema:
                            for mde_response in mde_response_list:
                                if mde_response.get('attribute_key') == attribute_key and mde_response.get('revised_question'):
                                    query = mde_response['revised_question']
                                    break
                        # Step 3 - Run query to get best matches
                        if vector_storage == 'elasticsearch':
                            query_params_data = infy_gen_ai_sdk.vectordb.provider.elasticsearch.VectorDbQueryParamsData(
                                **{
                                    "query": query,
                                    "top_k": top_result,
                                    'pre_filter_fetch_k': query_dict['pre_filter_fetch_k'],
                                    'filter_metadata': mde_schema if use_mde_schema else query_dict['filter_metadata']
                                })
                        try:
                            if vector_storage == 'elasticsearch':
                                records = vector_db_provider.get_matches(
                                    query_params_data)
                        except Exception as e:
                            print(f"Exception occurred: {e}")
                            self.__logger.error(f"Exception occurred: {e}")
                            if "File doesn't exist" in str(e):
                                message = "No records found. Vector database is empty."
                            else:
                                message = str(e)
                            records = []

                        top_k_matches_list = {"vectordb": []}
                        if not records:
                            top_k_matches_list["vectordb"].append(
                                {"file_path": '',
                                 "score": '',
                                 "min_distance": min_distance,
                                 "max_distance": max_distance,
                                 "content": '',
                                 "meta_data": '',
                                 "message": message})
                        else:
                            for record in records:
                                if (max_distance is None or record.score <= max_distance) and record.score >= min_distance:
                                    top_k_matches_list["vectordb"].append({"file_path": record.db_folder_path,
                                                                           "score": record.score,
                                                                           "min_distance": min_distance,
                                                                           "max_distance": max_distance,
                                                                           "content": record.content,
                                                                           "meta_data": record.metadata
                                                                           })
                            if not top_k_matches_list["vectordb"]:
                                top_k_matches_list["vectordb"].append(
                                    {"file_path": '',
                                     "score": '',
                                     "min_distance": min_distance,
                                     "max_distance": max_distance,
                                     "content": '',
                                     "meta_data": '',
                                     "message": "No records found. Score value not within the range of min_distance and max_distance configured."
                                     })
                        queries_list.append({"attribute_key": query_dict["attribute_key"],
                                            "question": query,
                                             "embedding_model": model_name,
                                             "distance_metric": distance_metric,
                                             "top_k": top_result,
                                             "top_k_matches": top_k_matches_list
                                             })

            return queries_list
        else:
            return None

    class ElasticsearchUtility:
        def __init__(self, vector_storage_config, index_id):
            self.__db_server_url = vector_storage_config.get("db_server_url")
            self.__username = vector_storage_config.get("username")
            self.__password = vector_storage_config.get("password")
            self.__verify_certs = vector_storage_config.get("verify_certs")
            self.__cert_fingerprint = vector_storage_config.get(
                "cert_fingerprint")
            self.__ca_certs_path = os.environ.get("CA_CERTS_PATH")
            self.__es_index = "idx-del-"+index_id
            if vector_storage_config.get("authenticate") is True:
                self.es_client = Elasticsearch(
                    [self.__db_server_url],
                    http_auth=(self.__username, self.__password),
                    verify_certs=self.__verify_certs,
                    ca_certs=self.__ca_certs_path,
                    ssl_show_warn=False,
                    ssl_assert_fingerprint=self.__cert_fingerprint
                )
            else:
                self.es_client = Elasticsearch(
                    [self.__db_server_url]
                )

        def check_index_exists(self):
            return self.es_client.indices.exists(index=self.__es_index)

        def get_model_name(self):
            query = {
                "_source": ["p_model_name"],
                "query": {
                    "match_all": {}
                }
            }
            response = self.es_client.search(index=self.__es_index, body=query)
            hits = response.get('hits', {}).get('hits', [])
            if hits:
                return hits[0].get('_source', {}).get('p_model_name', None)
            return None
