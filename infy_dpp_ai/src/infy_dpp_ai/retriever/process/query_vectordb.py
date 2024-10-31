# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
from typing import List
import infy_gen_ai_sdk
from infy_dpp_sdk.data import MessageData, ProcessorResponseData


class QueryVectordb():
    def __init__(self, file_sys_handler, logger):
        self.__file_sys_handler = file_sys_handler
        self.__logger = logger

    def query_vectordb(self, PROCESSOR_CONTEXT_DATA_NAME, processor_response_data, processor_config_data, context_data, document_data,  document_id):

        vector_enabled = False
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
            if vector_storage == 'faiss':
                if not db_name:
                    doc_work_folder_abs_path_list = self.__file_sys_handler.list_files(
                        encoded_files_root_path, f'/*/{document_id}')
                    # VALIDATION 1 #
                    if len(doc_work_folder_abs_path_list) == 0:
                        processor_response_data.message_data = [MessageData(type="ERROR",
                                                                            message=f"ERROR: Document work folder for {document_id} not found.")]
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
                        processor_response_data.message_data = [MessageData(type="ERROR",
                                                                            message=f"ERROR: Chunk files don't exist for doc_work_folder_id {document_id}.")]
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
                    model_name = vector_storage_config.get('model_name', '')
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
                    top_result = query_dict['top_k']
                    min_distance = query_dict.get('min_distance', 0)
                    max_distance = query_dict.get('max_distance', None)
                    message = ''
                    # Step 3 - Run query to get best matches
                    if vector_storage == 'faiss':
                        query_params_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbQueryParamsData(
                            **{
                                'query': query,
                                'top_k': top_result,
                                'pre_filter_fetch_k': query_dict['pre_filter_fetch_k'],
                                'filter_metadata': query_dict['filter_metadata']
                            })
                    elif vector_storage == 'infy_db_service':
                        query_params_data = infy_gen_ai_sdk.vectordb.provider.online.VectorDbQueryParamsData(
                            **{
                                "query": query,
                                "top_k": top_result,
                                "pre_filter_fetch_k": query_dict['pre_filter_fetch_k'],
                                "filter_metadata": query_dict['filter_metadata'],
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

            return queries_list
        else:
            return None
