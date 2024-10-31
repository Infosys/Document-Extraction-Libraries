# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import re
import json
import time
import uuid
from typing import List
from datetime import datetime, timezone
import fastapi
import infy_fs_utils
import infy_dpp_sdk
import infy_gen_ai_sdk
from schema.vector_res_data import SaveRecordsRequestData, SaveRecordsResponseData, GetRecordsRequestData, GetMatchesRequestData, DeleteRecordsRequestData
from schema.base_req_res_data import (ResponseCode, ResponseMessage)
from .b_controller import BController
from common.app_config_manager import AppConfigManager
from common.ainauto_logger_factory import AinautoLoggerFactory


class VectordbController(BController):
    """Vector DB Controller Class"""

    __CONTROLLER_PATH = "/vectordb"

    def __init__(self, context_root_path: str = ''):
        super().__init__(context_root_path=context_root_path,
                         controller_path=self.__CONTROLLER_PATH)
        self.get_router().add_api_route(
            "/saverecords", self.saveRecords, methods=["POST"], summary="Save records to a vector database",
            tags=["Vector Database"],
            response_model=SaveRecordsResponseData)
        self.get_router().add_api_route(
            "/getrecords", self.getRecords, methods=["POST"], summary="Get records from a vector database",
            tags=["Vector Database"],
            response_model=SaveRecordsResponseData)
        self.get_router().add_api_route(
            "/getmatches", self.getMatches, methods=["POST"], summary="Get matches from a vector database",
            tags=["Vector Database"],
            response_model=SaveRecordsResponseData)
        self.get_router().add_api_route(
            "/deleterecords", self.deleteRecords, methods=["POST"], summary="Delete records from a vector database",
            tags=["Vector Database"],
            response_model=SaveRecordsResponseData)

    def saveRecords(self, save_records_data: SaveRecordsRequestData,
                    request: fastapi.Request
                    ):
        app_config = AppConfigManager().get_app_config()
        logger = AinautoLoggerFactory().get_logger()

        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK)

        container_root_path = app_config['CONTAINER']["container_root_path"]
        client_config_data = infy_gen_ai_sdk.ClientConfigData(
            **{
                "container_data": {
                    "container_root_path": f"{container_root_path}",
                }
            })
        infy_gen_ai_sdk.ClientConfigManager().load(client_config_data)

        config_file_path = app_config['STORAGE']["model_details_path"]
        model_details_data = json.loads(
            file_sys_handler.read_file(config_file_path))

        start_time = time.time()
        date = datetime.now(timezone.utc)
        date_time_stamp = date.strftime("%Y-%m-%d %I:%M:%S %p")

        input_data = save_records_data.dict()

        model_name = input_data.get("model_name", '')
        index_id = input_data.get("index_id", '')
        db_index_name = input_data.get(
            "collection_name", '')
        db_index_secret_key = input_data.get(
            "collection_secret_key", '')
        record_data_dict = input_data.get("record_data_dict", {})
        if not model_name:
            response_data = SaveRecordsResponseData(
                response={},
                responseCde=ResponseCode.FAILURE,
                responseMsg="ERROR: Required configuration data is missing.",
                timestamp=datetime.now(timezone.utc),
            )
        elif not db_index_name:
            response_data = SaveRecordsResponseData(
                response={},
                responseCde=ResponseCode.FAILURE,
                responseMsg="ERROR: Required configuration data is missing.",
                timestamp=datetime.now(timezone.utc),
            )
        elif not record_data_dict:
            response_data = SaveRecordsResponseData(
                response={},
                responseCde=ResponseCode.FAILURE,
                responseMsg="ERROR: Required configuration data is missing.",
                timestamp=datetime.now(timezone.utc),
            )
        else:

            try:
                # ---------------------LOGIC STARTS------------------------------ #
                if model_name == 'all-MiniLM-L6-v2':
                    embedding_provider_config_data_dict = model_details_data.get(
                        'embedding').get('sentence_transformer').get('configuration')
                    os.environ["TIKTOKEN_CACHE_DIR"] = embedding_provider_config_data_dict['tiktoken_cache_dir']
                    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.StEmbeddingProviderConfigData(
                        **embedding_provider_config_data_dict)
                    embedding_provider = infy_gen_ai_sdk.embedding.provider.StEmbeddingProvider(
                        embedding_provider_config_data)
                    get_llm = 'sentence_transformer'
                elif model_name == 'text-embedding-ada-002':
                    embedding_provider_config_data_dict = model_details_data.get(
                        'embedding').get('openai').get('configuration')
                    os.environ["TIKTOKEN_CACHE_DIR"] = embedding_provider_config_data_dict['tiktoken_cache_dir']
                    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProviderConfigData(
                        **embedding_provider_config_data_dict)
                    embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProvider(
                        embedding_provider_config_data)
                    get_llm = 'openai'
                elif model_name == 'mistral-embd':
                    embedding_provider_config_data_dict = model_details_data.get(
                        'embedding').get('custom').get('configuration')
                    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProviderConfigData(
                        **embedding_provider_config_data_dict)
                    embedding_provider = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProvider(
                        embedding_provider_config_data)
                    get_llm = 'custom'
                else:
                    raise Exception(
                        f"Model '{model_name}' not supported.")

                faiss_config_data = model_details_data.get('storage').get(
                    'vectordb').get('faiss').get('configuration')
                encoded_files_root_path = faiss_config_data.get(
                    'encoded_files_root_path')
                vector_db_name = faiss_config_data.get('db_name')
                if index_id:
                    server_faiss_write_path = f'{encoded_files_root_path}/{get_llm}-{model_name}/{vector_db_name}/{index_id}'
                else:
                    server_faiss_write_path = f'{encoded_files_root_path}/{get_llm}-{model_name}/{vector_db_name}'

                vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbProviderConfigData(
                    **{
                        'db_folder_path': server_faiss_write_path,
                        'db_index_name': db_index_name,
                        "db_index_secret_key": db_index_secret_key if db_index_secret_key else None
                    })
                vector_db_provider = infy_gen_ai_sdk.vectordb.provider.faiss.FaissVectorDbProvider(
                    vector_db_provider_config_data, embedding_provider)

                unique_filename = f"{uuid.uuid4()}.txt"
                temp_path = f"/data/temp/{unique_filename}"
                file_sys_handler.write_file(
                    file_path=temp_path, data=record_data_dict.get('content'))
                # Step 3 - Add record(s) to vector db
                db_record_data = infy_gen_ai_sdk.vectordb.provider.faiss.InsertVectorDbRecordData(
                    **{
                        'content_file_path': temp_path,
                        'metadata': record_data_dict.get('metadata', {})
                    })
                vector_db_provider.save_record(db_record_data)
                file_sys_handler.delete_file(
                    file_path=temp_path)

                response_data = {
                    'encoded_path_list': server_faiss_write_path,
                    'model_name': model_name
                }
                response_cde = ResponseCode.SUCCESS
                response_msg = ResponseMessage.SUCCESS

                # ---------------------LOGIC ENDS------------------------------ #

            except Exception as e:
                response_data = {}
                response_cde = ResponseCode.FAILURE
                response_msg = e

        elapsed_time = round(time.time() - start_time, 3)

        response = SaveRecordsResponseData(response=response_data, responseCde=response_cde,
                                           responseMsg=str(response_msg), timestamp=date_time_stamp,
                                           responseTimeInSecs=(elapsed_time))
        return response

    def getRecords(self, get_records_data: GetRecordsRequestData,
                   request: fastapi.Request
                   ):
        app_config = AppConfigManager().get_app_config()
        logger = AinautoLoggerFactory().get_logger()

        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK)

        container_root_path = app_config['CONTAINER']["container_root_path"]
        client_config_data = infy_gen_ai_sdk.ClientConfigData(
            **{
                "container_data": {
                    "container_root_path": f"{container_root_path}",
                }
            })
        infy_gen_ai_sdk.ClientConfigManager().load(client_config_data)

        config_file_path = app_config['STORAGE']["model_details_path"]
        model_details_data = json.loads(
            file_sys_handler.read_file(config_file_path))

        start_time = time.time()
        date = datetime.now(timezone.utc)
        date_time_stamp = date.strftime("%Y-%m-%d %I:%M:%S %p")

        input_data = get_records_data.dict()

        model_name = input_data.get("model_name", '')
        index_id = input_data.get("index_id", '')
        db_index_name = input_data.get(
            "collection_name", '')
        db_index_secret_key = input_data.get(
            "collection_secret_key", '')
        if not index_id and (not model_name or not db_index_name):
            response_data = SaveRecordsResponseData(
                response={},
                responseCde=ResponseCode.FAILURE,
                responseMsg="ERROR: Either 'index_id' must be provided or both 'model_name' and 'collection_name' must be provided.",
                timestamp=datetime.now(timezone.utc),
            )
        else:
            try:

                # ---------------------LOGIC STARTS------------------------------ #
                if not model_name:
                    if index_id:
                        vector_root_path = model_details_data.get(
                            'common').get('base_vector_encoded_rooth_path')
                        base_file_list = file_sys_handler.list_files(
                            vector_root_path)
                        index_file_list = [
                            item for item in base_file_list if index_id in item]
                        if len(index_file_list) >= 3:
                            pattern = re.compile(
                                rf"{index_id}/[^/]+\.metadata\.json$")
                            secret_key_path = ''
                            for item in index_file_list:
                                if pattern.search(item):
                                    secret_key_path = item
                                    db_index_secret_key = (json.loads(
                                        file_sys_handler.read_file(secret_key_path))).get('secret_key')
                                    break
                            if secret_key_path:
                                index_file_list = [
                                    item for item in index_file_list if item != secret_key_path]
                            rel_path = (
                                f'/{index_file_list[0]}').split(vector_root_path, 1)[1]
                            path_parts = rel_path.strip(
                                '/').split('/')
                            model_name = '-'.join(
                                path_parts[0].split('-')[1:])
                            db_index_name = path_parts[3].split('.')[0]
                        else:
                            raise Exception(
                                f"Index '{index_id}' not found.")

                if model_name == 'all-MiniLM-L6-v2':
                    embedding_provider_config_data_dict = model_details_data.get(
                        'embedding').get('sentence_transformer').get('configuration')
                    os.environ["TIKTOKEN_CACHE_DIR"] = embedding_provider_config_data_dict['tiktoken_cache_dir']
                    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.StEmbeddingProviderConfigData(
                        **embedding_provider_config_data_dict)
                    embedding_provider = infy_gen_ai_sdk.embedding.provider.StEmbeddingProvider(
                        embedding_provider_config_data)
                    get_llm = 'sentence_transformer'
                elif model_name == 'text-embedding-ada-002':
                    embedding_provider_config_data_dict = model_details_data.get(
                        'embedding').get('openai').get('configuration')
                    os.environ["TIKTOKEN_CACHE_DIR"] = embedding_provider_config_data_dict['tiktoken_cache_dir']
                    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProviderConfigData(
                        **embedding_provider_config_data_dict)
                    embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProvider(
                        embedding_provider_config_data)
                    get_llm = 'openai'
                elif model_name == 'mistral-embd':
                    embedding_provider_config_data_dict = model_details_data.get(
                        'embedding').get('custom').get('configuration')
                    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProviderConfigData(
                        **embedding_provider_config_data_dict)
                    embedding_provider = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProvider(
                        embedding_provider_config_data)
                    get_llm = 'custom'
                else:
                    raise Exception(
                        f"Model '{model_name}' not supported.")

                faiss_config_data = model_details_data.get('storage').get(
                    'vectordb').get('faiss').get('configuration')
                encoded_files_root_path = faiss_config_data.get(
                    'encoded_files_root_path')
                vector_db_name = faiss_config_data.get('db_name')
                if index_id:
                    server_faiss_write_path = f'{encoded_files_root_path}/{get_llm}-{model_name}/{vector_db_name}/{index_id}'
                else:
                    server_faiss_write_path = f'{encoded_files_root_path}/{get_llm}-{model_name}/{vector_db_name}'

                vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbProviderConfigData(
                    **{
                        'db_folder_path': server_faiss_write_path,
                        'db_index_name': db_index_name,
                        "db_index_secret_key": db_index_secret_key if db_index_secret_key else None
                    })
                vector_db_provider = infy_gen_ai_sdk.vectordb.provider.faiss.FaissVectorDbProvider(
                    vector_db_provider_config_data, embedding_provider)

                records: List[infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbRecordData] = vector_db_provider.get_records()

                response_data = {
                    'records': records,
                }
                response_cde = ResponseCode.SUCCESS
                response_msg = ResponseMessage.SUCCESS

                # ---------------------LOGIC ENDS------------------------------ #

            except Exception as e:
                response_data = {}
                response_cde = ResponseCode.FAILURE
                response_msg = e

        elapsed_time = round(time.time() - start_time, 3)

        response = SaveRecordsResponseData(response=response_data, responseCde=response_cde,
                                           responseMsg=str(response_msg), timestamp=date_time_stamp,
                                           responseTimeInSecs=(elapsed_time))
        return response

    def getMatches(self, get_matches_data: GetMatchesRequestData,
                   request: fastapi.Request
                   ):
        app_config = AppConfigManager().get_app_config()
        logger = AinautoLoggerFactory().get_logger()

        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK)

        container_root_path = app_config['CONTAINER']["container_root_path"]
        client_config_data = infy_gen_ai_sdk.ClientConfigData(
            **{
                "container_data": {
                    "container_root_path": f"{container_root_path}",
                }
            })
        infy_gen_ai_sdk.ClientConfigManager().load(client_config_data)

        config_file_path = app_config['STORAGE']["model_details_path"]
        model_details_data = json.loads(
            file_sys_handler.read_file(config_file_path))

        start_time = time.time()
        date = datetime.now(timezone.utc)
        date_time_stamp = date.strftime("%Y-%m-%d %I:%M:%S %p")

        input_data = get_matches_data.dict()

        model_name = input_data.get("model_name", '')
        index_id = input_data.get("index_id", '')
        db_index_name = input_data.get(
            "collection_name", '')
        db_index_secret_key = input_data.get(
            "collection_secret_key", '')
        query_dict = input_data.get("query_dict", {})
        if not index_id and (not model_name or not db_index_name):
            response_data = SaveRecordsResponseData(
                response={},
                responseCde=ResponseCode.FAILURE,
                responseMsg="ERROR: Either 'index_id' must be provided or both 'model_name' and 'collection_name' must be provided.",
                timestamp=datetime.now(timezone.utc),
            )
        elif not query_dict:
            response_data = SaveRecordsResponseData(
                response={},
                responseCde=ResponseCode.FAILURE,
                responseMsg="ERROR: query_dict is required.",
                timestamp=datetime.now(timezone.utc),
            )
        else:
            try:

                # ---------------------LOGIC STARTS------------------------------ #
                if not model_name:
                    if index_id:
                        vector_root_path = model_details_data.get(
                            'common').get('base_vector_encoded_rooth_path')
                        base_file_list = file_sys_handler.list_files(
                            vector_root_path)
                        index_file_list = [
                            item for item in base_file_list if index_id in item]
                        if len(index_file_list) >= 3:
                            pattern = re.compile(
                                rf"{index_id}/[^/]+\.metadata\.json$")
                            secret_key_path = ''
                            for item in index_file_list:
                                if pattern.search(item):
                                    secret_key_path = item
                                    db_index_secret_key = (json.loads(
                                        file_sys_handler.read_file(secret_key_path))).get('secret_key')
                                    break
                            if secret_key_path:
                                index_file_list = [
                                    item for item in index_file_list if item != secret_key_path]
                            rel_path = (
                                f'/{index_file_list[0]}').split(vector_root_path, 1)[1]
                            path_parts = rel_path.strip(
                                '/').split('/')
                            model_name = '-'.join(
                                path_parts[0].split('-')[1:])
                            db_index_name = path_parts[3].split('.')[0]
                        else:
                            raise Exception(
                                f"Index '{index_id}' not found.")

                if model_name == 'all-MiniLM-L6-v2':
                    embedding_provider_config_data_dict = model_details_data.get(
                        'embedding').get('sentence_transformer').get('configuration')
                    os.environ["TIKTOKEN_CACHE_DIR"] = embedding_provider_config_data_dict['tiktoken_cache_dir']
                    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.StEmbeddingProviderConfigData(
                        **embedding_provider_config_data_dict)
                    embedding_provider = infy_gen_ai_sdk.embedding.provider.StEmbeddingProvider(
                        embedding_provider_config_data)
                    get_llm = 'sentence_transformer'
                elif model_name == 'text-embedding-ada-002':
                    embedding_provider_config_data_dict = model_details_data.get(
                        'embedding').get('openai').get('configuration')
                    os.environ["TIKTOKEN_CACHE_DIR"] = embedding_provider_config_data_dict['tiktoken_cache_dir']
                    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProviderConfigData(
                        **embedding_provider_config_data_dict)
                    embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProvider(
                        embedding_provider_config_data)
                    get_llm = 'openai'
                elif model_name == 'mistral-embd':
                    embedding_provider_config_data_dict = model_details_data.get(
                        'embedding').get('custom').get('configuration')
                    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProviderConfigData(
                        **embedding_provider_config_data_dict)
                    embedding_provider = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProvider(
                        embedding_provider_config_data)
                    get_llm = 'custom'
                else:
                    raise Exception(
                        f"Model '{model_name}' not supported.")

                faiss_config_data = model_details_data.get('storage').get(
                    'vectordb').get('faiss').get('configuration')
                encoded_files_root_path = faiss_config_data.get(
                    'encoded_files_root_path')
                vector_db_name = faiss_config_data.get('db_name')
                if index_id:
                    server_faiss_write_path = f'{encoded_files_root_path}/{get_llm}-{model_name}/{vector_db_name}/{index_id}'
                else:
                    server_faiss_write_path = f'{encoded_files_root_path}/{get_llm}-{model_name}/{vector_db_name}'

                vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbProviderConfigData(
                    **{
                        'db_folder_path': server_faiss_write_path,
                        'db_index_name': db_index_name,
                        "db_index_secret_key": db_index_secret_key if db_index_secret_key else None
                    })
                vector_db_provider = infy_gen_ai_sdk.vectordb.provider.faiss.FaissVectorDbProvider(
                    vector_db_provider_config_data, embedding_provider)

                query_params_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbQueryParamsData(
                    **{
                        'query': query_dict.get('query'),
                        'top_k': query_dict.get('top_k'),
                        'pre_filter_fetch_k': query_dict.get('pre_filter_fetch_k'),
                        'filter_metadata': query_dict.get('filter_metadata')
                    })
                records: List[infy_gen_ai_sdk.vectordb.provider.faiss.MatchingVectorDbRecordData] = vector_db_provider.get_matches(
                    query_params_data)

                response_data = {
                    'records': records
                }
                response_cde = ResponseCode.SUCCESS
                response_msg = ResponseMessage.SUCCESS

                # ---------------------LOGIC ENDS------------------------------ #

            except Exception as e:
                response_data = {}
                response_cde = ResponseCode.FAILURE
                response_msg = e

        elapsed_time = round(time.time() - start_time, 3)

        response = SaveRecordsResponseData(response=response_data, responseCde=response_cde,
                                           responseMsg=str(response_msg), timestamp=date_time_stamp,
                                           responseTimeInSecs=(elapsed_time))
        return response

    def deleteRecords(self, delete_records_data: DeleteRecordsRequestData,
                      request: fastapi.Request
                      ):
        app_config = AppConfigManager().get_app_config()
        logger = AinautoLoggerFactory().get_logger()

        file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK)

        container_root_path = app_config['CONTAINER']["container_root_path"]
        client_config_data = infy_gen_ai_sdk.ClientConfigData(
            **{
                "container_data": {
                    "container_root_path": f"{container_root_path}",
                }
            })
        infy_gen_ai_sdk.ClientConfigManager().load(client_config_data)

        config_file_path = app_config['STORAGE']["model_details_path"]
        model_details_data = json.loads(
            file_sys_handler.read_file(config_file_path))

        start_time = time.time()
        date = datetime.now(timezone.utc)
        date_time_stamp = date.strftime("%Y-%m-%d %I:%M:%S %p")

        input_data = delete_records_data.dict()

        model_name = input_data.get("model_name", '')
        index_id = input_data.get("index_id", '')
        db_index_name = input_data.get(
            "collection_name", '')
        db_index_secret_key = input_data.get(
            "collection_secret_key", '')
        if not model_name:
            response_data = SaveRecordsResponseData(
                response={},
                responseCde=ResponseCode.FAILURE,
                responseMsg="ERROR: Required configuration data is missing.",
                timestamp=datetime.now(timezone.utc),
            )
        elif not db_index_name:
            response_data = SaveRecordsResponseData(
                response={},
                responseCde=ResponseCode.FAILURE,
                responseMsg="ERROR: Required configuration data is missing.",
                timestamp=datetime.now(timezone.utc),
            )
        else:
            try:

                # ---------------------LOGIC STARTS------------------------------ #
                if not model_name:
                    if index_id:
                        vector_root_path = model_details_data.get(
                            'common').get('base_vector_encoded_rooth_path')
                        base_file_list = file_sys_handler.list_files(
                            vector_root_path)
                        index_file_list = [
                            item for item in base_file_list if index_id in item]
                        if len(index_file_list) >= 3:
                            pattern = re.compile(
                                rf"{index_id}/[^/]+\.metadata\.json$")
                            secret_key_path = ''
                            for item in index_file_list:
                                if pattern.search(item):
                                    secret_key_path = item
                                    db_index_secret_key = (json.loads(
                                        file_sys_handler.read_file(secret_key_path))).get('secret_key')
                                    break
                            if secret_key_path:
                                index_file_list = [
                                    item for item in index_file_list if item != secret_key_path]
                            rel_path = (
                                f'/{index_file_list[0]}').split(vector_root_path, 1)[1]
                            path_parts = rel_path.strip(
                                '/').split('/')
                            model_name = '-'.join(
                                path_parts[0].split('-')[1:])
                            db_index_name = path_parts[3].split('.')[0]
                        else:
                            raise Exception(
                                f"Index '{index_id}' not found.")

                if model_name == 'all-MiniLM-L6-v2':
                    embedding_provider_config_data_dict = model_details_data.get(
                        'embedding').get('sentence_transformer').get('configuration')
                    os.environ["TIKTOKEN_CACHE_DIR"] = embedding_provider_config_data_dict['tiktoken_cache_dir']
                    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.StEmbeddingProviderConfigData(
                        **embedding_provider_config_data_dict)
                    embedding_provider = infy_gen_ai_sdk.embedding.provider.StEmbeddingProvider(
                        embedding_provider_config_data)
                    get_llm = 'sentence_transformer'
                elif model_name == 'text-embedding-ada-002':
                    embedding_provider_config_data_dict = model_details_data.get(
                        'embedding').get('openai').get('configuration')
                    os.environ["TIKTOKEN_CACHE_DIR"] = embedding_provider_config_data_dict['tiktoken_cache_dir']
                    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProviderConfigData(
                        **embedding_provider_config_data_dict)
                    embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProvider(
                        embedding_provider_config_data)
                    get_llm = 'openai'
                elif model_name == 'mistral-embd':
                    embedding_provider_config_data_dict = model_details_data.get(
                        'embedding').get('custom').get('configuration')
                    embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProviderConfigData(
                        **embedding_provider_config_data_dict)
                    embedding_provider = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProvider(
                        embedding_provider_config_data)
                    get_llm = 'custom'
                else:
                    raise Exception(
                        f"Model '{model_name}' not supported.")

                faiss_config_data = model_details_data.get('storage').get(
                    'vectordb').get('faiss').get('configuration')
                encoded_files_root_path = faiss_config_data.get(
                    'encoded_files_root_path')
                vector_db_name = faiss_config_data.get('db_name')
                if index_id:
                    server_faiss_write_path = f'{encoded_files_root_path}/{get_llm}-{model_name}/{vector_db_name}/{index_id}'
                else:
                    server_faiss_write_path = f'{encoded_files_root_path}/{get_llm}-{model_name}/{vector_db_name}'

                vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbProviderConfigData(
                    **{
                        'db_folder_path': server_faiss_write_path,
                        'db_index_name': db_index_name,
                        "db_index_secret_key": db_index_secret_key if db_index_secret_key else None
                    })
                vector_db_provider = infy_gen_ai_sdk.vectordb.provider.faiss.FaissVectorDbProvider(
                    vector_db_provider_config_data, embedding_provider)

                vector_db_provider.delete_records()

                response_data = {
                    "response": f"All records under collection:'{db_index_name}' deleted successfully"
                }
                response_cde = ResponseCode.SUCCESS
                response_msg = ResponseMessage.SUCCESS

                # ---------------------LOGIC ENDS------------------------------ #

            except Exception as e:
                response_data = {}
                response_cde = ResponseCode.FAILURE
                response_msg = e

        elapsed_time = round(time.time() - start_time, 3)

        response = SaveRecordsResponseData(response=response_data, responseCde=response_cde,
                                           responseMsg=str(response_msg), timestamp=date_time_stamp,
                                           responseTimeInSecs=(elapsed_time))
        return response
