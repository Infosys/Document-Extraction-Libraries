# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
from typing import List
import infy_gen_ai_sdk


class QuerySparseIndex():
    def __init__(self, file_sys_handler, logger, app_config):
        self.__logger = logger
        self.__app_config = app_config
        self.__file_sys_handler = file_sys_handler

    def query_sparsedb(self, PROCESSOR_CONTEXT_DATA_NAME, processor_response_data, processor_config_data, context_data, document_data,  document_id):
        sparse_enabled = False
        queries_list = []
        mde_schema = {}
        mde_response_list = context_data.get(
            'metadata_extractor_custom_query', {})
        for key, value in processor_config_data.items():
            if key == 'storage':
                for storage_key, storage_value in value.items():
                    if storage_key == 'sparseindex':
                        sparse_index_root_path = None
                        sparse_storage = None
                        for e_key, e_val in storage_value.items():
                            if e_key and e_val.get('enabled'):
                                sparse_enabled = True
                                sparse_storage = e_key
                                sparse_storage_config = e_val.get(
                                    "configuration", '')
                                sparse_index_root_path = sparse_storage_config.get(
                                    "sparse_index_root_path", '')
                                sparse_db_name = sparse_storage_config.get(
                                    "db_name", '')
                                nltk_data_dir = sparse_storage_config.get(
                                    "nltk_data_dir", '')
                                sparse_collections = sparse_storage_config.get(
                                    "collections", [])
                                db_service_url = sparse_storage_config.get(
                                    "db_service_url", '')
                                method_name = sparse_storage_config.get(
                                    "method_name", '')
                                index_id = sparse_storage_config.get(
                                    "index_id", '')
                                break
        if sparse_enabled:
            if mde_response_list and len(mde_response_list[0].get('custom_metadata'))>0:
                use_mde_schema = True
                metadata_schema = mde_response_list[0].get(
                    'custom_metadata')
                if isinstance(metadata_schema, dict):
                    for key, value in metadata_schema.items():
                        if value:
                            modified_key = f'custom_metadata.{key}'
                            mde_schema[modified_key] = value
                else:
                    metadata_schema = {}
                    use_mde_schema = False
            else:
                metadata_schema = {}
                use_mde_schema = False
            
            if sparse_storage == 'bm25s':
                os.environ["NLTK_DATA_DIR"] = nltk_data_dir
                if sparse_db_name:
                    server_faiss_write_path = f'{sparse_index_root_path}/{sparse_storage}/{sparse_db_name}'
                else:
                    server_faiss_write_path = f'{sparse_index_root_path}/{sparse_storage}/{document_id}'

                if index_id:
                    server_faiss_write_path = f'{server_faiss_write_path}/{index_id}'

                top_k_matches_list = {"sparseindex": []}

                if sparse_collections:
                    for collection in sparse_collections:
                        sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbProviderConfigData(
                            **{
                                'db_folder_path': server_faiss_write_path,
                                'db_index_name': collection.get('collection_name', sparse_db_name) or document_id,
                                'db_index_secret_key': collection.get('collection_secret_key', '')
                            })
                        sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.bm25s.Bm25sSparseDbProvider(
                            sparse_db_provider_config_data)

                        request_creator_context = context_data.get(
                            'request_creator', {})
                        question_config_request_file = request_creator_context.get(
                            'question_config_request_file', '')
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
                            
                            if use_mde_schema:
                                for mde_response in mde_response_list:
                                    if mde_response.get('attribute_key') == attribute_key and mde_response.get('revised_question'):
                                        query = mde_response['revised_question']
                                        break                            
                            
                            query_params_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbQueryParamsData(
                                **{
                                    'query': query,
                                    'top_k': top_result,
                                    'pre_filter_fetch_k': query_dict['pre_filter_fetch_k'],
                                    'filter_metadata': mde_schema if use_mde_schema else query_dict['filter_metadata']
                                })
                            try:
                                records: List[infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbMatchesRecordData] = sparse_db_provider.get_matches(
                                    query_params_data)
                            except Exception as e:
                                print(f"Exception occurred: {e}")
                                self.__logger.error(f"Exception occurred: {e}")
                                records = []

                            if not records:
                                top_k_matches_list["sparseindex"].append(
                                    {"file_path": '',
                                        "score": '',
                                        "min_distance": min_distance,
                                        "max_distance": max_distance,
                                        "content": '',
                                        "meta_data": '',
                                        "message": "No records found. Sparse database is empty."})
                            else:
                                for record in records:
                                    record = record.dict()
                                    if record.get('score', 0) >= min_distance:
                                        record_metadata = record.get(
                                            'metadata', {})
                                        top_k_matches_list["sparseindex"].append({
                                            "file_path": server_faiss_write_path,
                                            "score": record.get('score'),
                                            "min_distance": min_distance,
                                            "max_distance": max_distance,
                                            "content": record.get('content'),
                                            "meta_data": record_metadata
                                        })
                                if not top_k_matches_list["sparseindex"]:
                                    top_k_matches_list["sparseindex"].append(
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
                                                 "embedding_model": '',
                                                 "distance_metric": '',
                                                 "top_k": top_result,
                                                 "top_k_matches": top_k_matches_list
                                                 })
                elif not sparse_collections:
                    sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbProviderConfigData(
                        **{
                            'db_folder_path': server_faiss_write_path,
                            'db_index_name': sparse_db_name if sparse_db_name else document_id,
                            'db_index_secret_key': ''
                        })
                    sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.bm25s.Bm25sSparseDbProvider(
                        sparse_db_provider_config_data)

                    request_creator_context = context_data.get(
                        'request_creator', {})
                    question_config_request_file = request_creator_context.get(
                        'question_config_request_file', '')
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
                        if use_mde_schema:
                            for mde_response in mde_response_list:
                                if mde_response.get('attribute_key') == attribute_key and mde_response.get('revised_question'):
                                    query = mde_response['revised_question']
                                    break
                        query_params_data = infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbQueryParamsData(
                            **{
                                'query': query,
                                'top_k': top_result,
                                'pre_filter_fetch_k': query_dict['pre_filter_fetch_k'],
                                'filter_metadata': mde_schema if use_mde_schema else query_dict['filter_metadata']
                            })
                        try:
                            records: List[infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbMatchesRecordData] = sparse_db_provider.get_matches(
                                query_params_data)
                        except Exception as e:
                            print(f"Exception occurred: {e}")
                            self.__logger.error(f"Exception occurred: {e}")
                            records = []

                        top_k_matches_list = {"sparseindex": []}
                        if not records:
                            top_k_matches_list["sparseindex"].append(
                                {"file_path": '',
                                    "score": '',
                                    "min_distance": min_distance,
                                    "max_distance": max_distance,
                                    "content": '',
                                    "meta_data": '',
                                    "message": "No records found. Sparse database is empty."})
                        else:
                            for record in records:
                                record = record.dict()
                                if record.get('score', 0) >= min_distance:
                                    record_metadata = record.get(
                                        'metadata', {})
                                    top_k_matches_list["sparseindex"].append({
                                        "file_path": server_faiss_write_path,
                                        "score": record.get('score'),
                                        "min_distance": min_distance,
                                        "max_distance": max_distance,
                                        "content": record.get('content'),
                                        "meta_data": record_metadata
                                    })
                            if not top_k_matches_list["sparseindex"]:
                                top_k_matches_list["sparseindex"].append(
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
                                             "embedding_model": '',
                                             "distance_metric": '',
                                             "top_k": top_result,
                                             "top_k_matches": top_k_matches_list
                                             })
            elif sparse_storage == 'infy_db_service':
                if sparse_collections:
                    for collection in sparse_collections:
                        sparse_db_provider_config_data = infy_gen_ai_sdk.sparsedb.provider.online.OnlineSparseDbProviderConfigData(
                            **{
                                'db_service_url': db_service_url,
                                'method_name': method_name,
                                'index_id': index_id,
                                "collection_name": collection.get('collection_name', sparse_db_name) or document_id,
                                "collection_secret_key": collection.get('collection_secret_key', '')
                            })
                        sparse_db_provider = infy_gen_ai_sdk.sparsedb.provider.online.OnlineSparseDbProvider(
                            sparse_db_provider_config_data)

                        request_creator_context = context_data.get(
                            'request_creator', {})
                        question_config_request_file = request_creator_context.get(
                            'question_config_request_file', '')
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
                            if use_mde_schema:
                                for mde_response in mde_response_list:
                                    if mde_response.get('attribute_key') == attribute_key and mde_response.get('revised_question'):
                                        query = mde_response['revised_question']
                                        break
                            query_params_data = infy_gen_ai_sdk.sparsedb.provider.online.SparseDbQueryParamsData(
                                **{
                                    "query": query,
                                    "top_k": top_result,
                                    'pre_filter_fetch_k': query_dict.get('pre_filter_fetch_k'),
                                    'filter_metadata':mde_schema if use_mde_schema else query_dict['filter_metadata'],
                                    "min_distance": min_distance,
                                    "max_distance": max_distance
                                })

                            try:
                                records: List[infy_gen_ai_sdk.sparsedb.provider.bm25s.SparseDbMatchesRecordData] = sparse_db_provider.get_matches(
                                    query_params_data)
                            except Exception as e:
                                print(f"Exception occurred: {e}")
                                self.__logger.error(f"Exception occurred: {e}")
                                records = []

                            top_k_matches_list = {"sparseindex": []}
                            if not records:
                                top_k_matches_list["sparseindex"].append(
                                    {"file_path": db_service_url,
                                        "score": '',
                                        "min_distance": min_distance,
                                        "max_distance": max_distance,
                                        "content": '',
                                        "meta_data": '',
                                        "message": "No records found. Sparse database is empty."})
                            else:
                                for record in records:
                                    if record.get('score', 0) >= min_distance:
                                        record_metadata = record.get(
                                            'metadata', {})
                                        top_k_matches_list["sparseindex"].append({
                                            "file_path": record.get('db_folder_path'),
                                            "score": record.get('score'),
                                            "min_distance": min_distance,
                                            "max_distance": max_distance,
                                            "content": record.get('content'),
                                            "meta_data": record_metadata
                                        })
                                if not top_k_matches_list["sparseindex"]:
                                    top_k_matches_list["sparseindex"].append(
                                        {"file_path": record.get('db_folder_path'),
                                            "score": '',
                                            "min_distance": min_distance,
                                            "max_distance": max_distance,
                                            "content": '',
                                            "meta_data": '',
                                            "message": "No records found. Score value not within the range of min_distance and max_distance configured."
                                         })
                            queries_list.append({"attribute_key": query_dict["attribute_key"],
                                                "question": query,
                                                 "embedding_model": '',
                                                 "distance_metric": '',
                                                 "top_k": top_result,
                                                 "top_k_matches": top_k_matches_list
                                                 })
                elif not sparse_collections:
                    raise ValueError(
                        "Sparse collections not provided for infy_db_service storage")
            else:
                raise ValueError(
                    f"Sparse storage type: {sparse_storage} not supported.")
            return queries_list
        else:
            return None
