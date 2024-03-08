# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                   #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
from typing import List
import infy_dpp_sdk
from infy_dpp_sdk.data import *
import infy_gen_ai_sdk
import infy_fs_utils

PROCESSEOR_CONTEXT_DATA_NAME = "query_retriever"


class QueryRetriever(infy_dpp_sdk.interface.IProcessor):
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
        self.__processor_config_data = config_data.get('QueryRetriever', {})
        context_data = context_data if context_data else {}
        document_id = document_data.document_id
        for key, value in self.__processor_config_data.items():
            if key == 'storage':
                for e_key, e_val in value.items():
                    if e_val.get('enabled'):
                        get_storage = e_key
                        get_storage_config = e_val.get('configuration')
                        encoded_files_root_path = get_storage_config.get(
                            "encoded_files_root_path")
                        chunked_files_root_path = get_storage_config.get(
                            "chunked_files_root_path")
                        db_name=get_storage_config.get("db_name")
        if not db_name:            
            doc_work_folder_abs_path_list = self.__file_sys_handler.list_files(
                encoded_files_root_path, f'/*/{document_id}')
            # VALIDATION 1 #
            if len(doc_work_folder_abs_path_list) == 0:
                processor_response_data.message_data = [MessageData(type="ERROR",
                                                                        message=f"ERROR: Document work folder for {document_id} not found.")]
                context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
                    'error': f"ERROR: Document work folder for {document_id} not found."}
                processor_response_data.document_data = document_data
                processor_response_data.context_data = context_data
                return processor_response_data
            # VALIDATION 1 END#
            sub_folder_name = os.path.basename(
                os.path.dirname(f'{doc_work_folder_abs_path_list[0]}'))
        for key, value in self.__processor_config_data.items():
            if key == 'embedding':
                for e_key, e_val in value.items():
                    if db_name:
                        if e_val.get('enabled'):
                            get_embedding = e_key
                            get_emb_config = e_val.get('configuration')
                            sub_folder_name=get_embedding
                    elif e_key == sub_folder_name:
                        if e_val.get('enabled'):
                            get_embedding = e_key
                            get_emb_config = e_val.get('configuration')

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
        chunked_files_path_list = __get_files(server_chunked_files_list)
        # VALIDATION 2  #
        if len(chunked_files_path_list) == 0:
            processor_response_data.message_data = [MessageData(type="ERROR",
                                                                message=f"ERROR: Chunk files don't exist for doc_work_folder_id {document_id}.")]
            context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
                'error': f"ERROR: Chunk files don't exist for doc_work_folder_id {document_id}."}
            processor_response_data.document_data = document_data
            processor_response_data.context_data = context_data
            return processor_response_data
        # VALIDATION 2 END#
        # Step 1 - Choose embedding provider
        embedding_provider_config_data_dict = get_emb_config if get_emb_config else {}
        if sub_folder_name == 'sentence_transformer' and get_embedding == 'sentence_transformer' and get_storage == 'faiss':
            embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.StEmbeddingProviderConfigData(
                **embedding_provider_config_data_dict)

            embedding_provider = infy_gen_ai_sdk.embedding.provider.StEmbeddingProvider(
                embedding_provider_config_data)
        if sub_folder_name == 'openai-text-davinci-003' and get_embedding == 'openai-text-davinci-003' and get_storage == 'faiss':
            os.environ["TIKTOKEN_CACHE_DIR"] = embedding_provider_config_data_dict['tiktoken_cache_dir']
            embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProviderConfigData(
                **embedding_provider_config_data_dict)

            embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProvider(
                embedding_provider_config_data)
        if db_name:
           server_faiss_write_path = f'{encoded_files_root_path}/{get_embedding}/{db_name}'
        else:
            server_faiss_write_path = f'{encoded_files_root_path}/{get_embedding}/{document_id}'
        # Step 2 - Choose vector db provider
        vector_db_provider_config_data_dict = {
            'db_folder_path': server_faiss_write_path,
            'db_index_name': 'document'
        }
        vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbProviderConfigData(
            **vector_db_provider_config_data_dict)
        vector_db_provider = infy_gen_ai_sdk.vectordb.provider.faiss.FaissVectorDbProvider(
            vector_db_provider_config_data, embedding_provider)
        queries_list = []
        for query_dict in self.__processor_config_data['queries']:
            query = query_dict['question']
            top_result = query_dict['top_k']
            # Step 3 - Run query to get best matches
            query_params_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbQueryParamsData(
                **{
                    'query': query,
                    'top_k': top_result,
                    'pre_filter_fetch_k': query_dict['pre_filter_fetch_k'],
                    'filter_metadata': query_dict['filter_metadata']
                })
            records: List[infy_gen_ai_sdk.vectordb.provider.faiss.MatchingVectorDbRecordData] = vector_db_provider.get_matches(
                query_params_data)
            top_k_matches_list = []
            for record in records:
                top_k_matches_list.append({"file_path": record.db_folder_path,
                                           "score": record.score,
                                           "content": record.content,
                                           "meta_data": record.metadata
                                           })
            queries_list.append({"attribute_key": query_dict["attribute_key"],
                                "question": query,
                                 "top_k": top_result,
                                 "top_k_matches": top_k_matches_list
                                 })

        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {'queries': queries_list}

        # Populate response data
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data
