# ===============================================================================================================#
# Copyright 2023 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
import infy_dpp_sdk
from infy_dpp_sdk.data import *
import infy_gen_ai_sdk
import infy_fs_utils

PROCESSEOR_CONTEXT_DATA_NAME = "data_encoder"


class DataEncoder(infy_dpp_sdk.interface.IProcessor):
    def __init__(self):
        self.__logger = self.get_logger()
        self.__file_sys_handler: infy_fs_utils.interface.IFileSystemHandler = self.get_fs_handler()
        client_config_data_dict = infy_dpp_sdk.ClientConfigManager().get().dict()

        if not infy_fs_utils.manager.FileSystemManager().has_fs_handler(infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK):
            infy_fs_utils.manager.FileSystemManager().add_fs_handler(
                infy_fs_utils.provider.FileSystemHandler(
                    self.__file_sys_handler.get_storage_config_data()),
                infy_gen_ai_sdk.common.Constants.FSH_GEN_AI_SDK)
        client_config_data = infy_gen_ai_sdk.ClientConfigData(
            **client_config_data_dict)
        infy_gen_ai_sdk.ClientConfigManager().load(client_config_data)

    def do_execute(self, document_data: DocumentData, context_data: dict, config_data: dict) -> ProcessorResponseData:
        processor_response_data = infy_dpp_sdk.data.ProcessorResponseData()
        context_data = context_data if context_data else {}
        __processor_config_data = config_data.get('DataEncoder', {})
        encoded_path_list = []
        document_id = document_data.document_id

        for key, value in __processor_config_data.items():
            if key == 'embedding':
                for e_key, e_val in value.items():
                    if e_val.get('enabled'):
                        get_llm = e_key
                        get_llm_config = e_val.get('configuration')
                        model_name = get_llm_config.get("model_name")
            if key == 'storage':
                for e_key, e_val in value.items():
                    if e_val.get('enabled'):
                        get_storage = e_key
                        get_storage_config = e_val.get('configuration')
                        encoded_files_root_path = get_storage_config.get(
                            "encoded_files_root_path")
                        db_name = get_storage_config.get("db_name")
                        distance_metric = get_storage_config.get(
                            "distance_metric")
                        if distance_metric is not None:
                            for key, value in distance_metric.items():
                                if value is True:
                                    distance_metric = key
                                    break

        # Step 1 - Choose embedding provider
        embedding_provider_config_data_dict = get_llm_config
        if get_llm == 'sentence_transformer' and get_storage == 'faiss':
            embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.StEmbeddingProviderConfigData(
                **embedding_provider_config_data_dict)

            embedding_provider = infy_gen_ai_sdk.embedding.provider.StEmbeddingProvider(
                embedding_provider_config_data)
        if get_llm == 'openai' and get_storage == 'faiss':
            os.environ["TIKTOKEN_CACHE_DIR"] = embedding_provider_config_data_dict['tiktoken_cache_dir']
            embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProviderConfigData(
                **embedding_provider_config_data_dict)

            embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProvider(
                embedding_provider_config_data)
        if get_llm == 'custom' and get_storage == 'faiss':
            embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProviderConfigData(
                **embedding_provider_config_data_dict)

            embedding_provider = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProvider(
                embedding_provider_config_data)

        if db_name:
            server_faiss_write_path = f'{encoded_files_root_path}/{get_llm}-{model_name}/{db_name}'
        else:
            server_faiss_write_path = f'{encoded_files_root_path}/{get_llm}-{model_name}/{document_id}'
        # Step 2 - Choose vector db provider
        vector_db_provider_config_data_dict = {
            'db_folder_path': server_faiss_write_path,
            'db_index_name': 'document'
        }
        vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbProviderConfigData(
            **vector_db_provider_config_data_dict)
        vector_db_provider = infy_gen_ai_sdk.vectordb.provider.faiss.FaissVectorDbProvider(
            vector_db_provider_config_data, embedding_provider)

        chunk_data = context_data.get('chunk_generator')
        for text_file_path in chunk_data.get('chunked_data_list'):
            #
            if f'{text_file_path}_metadata.json' in chunk_data.get('chunked_file_meta_data_list'):
                metadata_file_path = f'{text_file_path}_metadata.json'
                metadata = json.loads(
                    self.__file_sys_handler.read_file(metadata_file_path))
                # print(f'* {metadata} *')
            else:
                metadata = {}
            # Step 3 - Add record(s) to vector db
            db_record_data_dict = {
                'content_file_path': text_file_path,
                'metadata': metadata
            }
            db_record_data = infy_gen_ai_sdk.vectordb.provider.faiss.InsertVectorDbRecordData(
                **db_record_data_dict)
            vector_db_provider.save_record(db_record_data)

        encoded_path_list.append(server_faiss_write_path)
        context_data[PROCESSEOR_CONTEXT_DATA_NAME] = {
            'encoded_path_list': encoded_path_list,
            'embedding_model': model_name,
            'distance_metric': distance_metric
        }

        # Populate response data
        processor_response_data.document_data = document_data
        processor_response_data.context_data = context_data

        return processor_response_data
