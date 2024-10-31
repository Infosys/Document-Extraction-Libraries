# ===============================================================================================================#
# Copyright 2024 Infosys Ltd.                                                                                    #
# Use of this source code is governed by Apache License Version 2.0 that can be found in the LICENSE file or at  #
# http://www.apache.org/licenses/                                                                                #
# ===============================================================================================================#

import os
import json
import infy_fs_utils
import infy_dpp_sdk
import infy_gen_ai_sdk


class VectorIndexer:
    """VectorIndexer class is used to index data to vector database.
    """

    def __init__(self, vector_storage, vector_storage_config, get_llm, get_llm_config,  model_name, chunk_data, document_id, index_id) -> None:
        self.vector_storage = vector_storage
        self.vector_db_name = vector_storage_config.get(
            "db_name", '')
        self.encoded_files_root_path = vector_storage_config.get(
            "encoded_files_root_path", '')
        self.vector_collections = vector_storage_config.get(
            "collections", [])
        self.get_llm = get_llm
        self.get_llm_config = get_llm_config
        self.model_name = model_name
        self.chunk_data = chunk_data
        self.document_id = document_id
        self.db_service_url = vector_storage_config.get(
            "db_service_url", '')
        self.index_id = index_id

        self.__file_sys_handler = infy_fs_utils.manager.FileSystemManager(
        ).get_fs_handler(infy_dpp_sdk.common.Constants.FSH_DPP)

    def create_index(self):
        encoded_path_list = []
        encoded_path = ''
        if self.vector_storage == 'faiss':
            # Step 1 - Choose embedding provider
            embedding_provider_config_data_dict = self.get_llm_config
            if self.get_llm == 'sentence_transformer' and self.vector_storage == 'faiss':
                os.environ["TIKTOKEN_CACHE_DIR"] = embedding_provider_config_data_dict['tiktoken_cache_dir']
                embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.StEmbeddingProviderConfigData(
                    **embedding_provider_config_data_dict)

                embedding_provider = infy_gen_ai_sdk.embedding.provider.StEmbeddingProvider(
                    embedding_provider_config_data)
            if self.get_llm == 'openai' and self.vector_storage == 'faiss':
                os.environ["TIKTOKEN_CACHE_DIR"] = embedding_provider_config_data_dict['tiktoken_cache_dir']
                embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProviderConfigData(
                    **embedding_provider_config_data_dict)

                embedding_provider = infy_gen_ai_sdk.embedding.provider.OpenAIEmbeddingProvider(
                    embedding_provider_config_data)
            if self.get_llm == 'custom' and self.vector_storage == 'faiss':
                embedding_provider_config_data = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProviderConfigData(
                    **embedding_provider_config_data_dict)

                embedding_provider = infy_gen_ai_sdk.embedding.provider.CustomEmbeddingProvider(
                    embedding_provider_config_data)

            if self.vector_db_name:
                server_faiss_write_path = f'{self.encoded_files_root_path}/{self.get_llm}-{self.model_name}/{self.vector_db_name}'
            else:
                server_faiss_write_path = f'{self.encoded_files_root_path}/{self.get_llm}-{self.model_name}/{self.document_id}'
            # index-id
            if self.index_id:
                server_faiss_write_path = f'{server_faiss_write_path}/{self.index_id}'
            # index-id

        if self.vector_collections:
            for collection in self.vector_collections:
                if self.vector_storage == 'faiss':
                    # Step 2 - Choose vector db provider
                    vector_db_provider_config_data_dict = {
                        'db_folder_path': server_faiss_write_path,
                        'db_index_name': collection.get('collection_name', self.vector_db_name) or self.document_id,
                        'db_index_secret_key': collection.get('collection_secret_key', '')
                    }
                    vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbProviderConfigData(
                        **vector_db_provider_config_data_dict)
                    vector_db_provider = infy_gen_ai_sdk.vectordb.provider.faiss.FaissVectorDbProvider(
                        vector_db_provider_config_data, embedding_provider)
                elif self.vector_storage == 'infy_db_service':
                    vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.online.OnlineVectorDbProviderConfigData(
                        **{
                            'db_service_url': self.db_service_url,
                            'model_name': self.model_name,
                            'index_id': self.index_id,
                            "collection_name": collection.get("collection_name"),
                            "collection_secret_key": collection.get("collection_secret_key")
                        })

                    vector_db_provider = infy_gen_ai_sdk.vectordb.provider.online.OnlineVectorDbProvider(
                        vector_db_provider_config_data)

                for _key, chunked_method in self.chunk_data.items():
                    for text_file_path in chunked_method.get('chunked_data_list'):
                        if f'{text_file_path}_metadata.json' in chunked_method.get('chunked_file_meta_data_list'):
                            metadata_file_path = f'{text_file_path}_metadata.json'
                            if metadata_file_path in chunked_method.get('chunked_file_meta_data_list', []):
                                metadata = json.loads(
                                    self.__file_sys_handler.read_file(metadata_file_path))
                            else:
                                metadata = {}

                            chunk_type = collection.get('chunk_type')
                            if chunk_type:
                                if chunk_type == metadata.get('chunking_method'):
                                    # Add record(s) to vector db
                                    if self.vector_storage == 'faiss':
                                        db_record_data_dict = {
                                            'content_file_path': text_file_path,
                                            'metadata': metadata
                                        }
                                        db_record_data = infy_gen_ai_sdk.vectordb.provider.faiss.InsertVectorDbRecordData(
                                            **db_record_data_dict)
                                        vector_db_provider.save_record(
                                            db_record_data)
                                    elif self.vector_storage == 'infy_db_service':
                                        content = self.__file_sys_handler.read_file(
                                            text_file_path)
                                        request_body = infy_gen_ai_sdk.vectordb.provider.online.InsertVectorDbRecordData(
                                            **{
                                                "content": content,
                                                "metadata": metadata
                                            })
                                        # fmt: off
                                        encoded_path = vector_db_provider.save_record(request_body) # pylint: disable=E1111
                                        # fmt: on

                            elif chunk_type is None or chunk_type == '':
                                # Add record(s) to vector db
                                if self.vector_storage == 'faiss':
                                    db_record_data_dict = {
                                        'content_file_path': text_file_path,
                                        'metadata': metadata
                                    }
                                    db_record_data = infy_gen_ai_sdk.vectordb.provider.faiss.InsertVectorDbRecordData(
                                        **db_record_data_dict)
                                    vector_db_provider.save_record(
                                        db_record_data)
                                elif self.vector_storage == 'infy_db_service':
                                    content = self.__file_sys_handler.read_file(
                                        text_file_path)
                                    request_body = infy_gen_ai_sdk.vectordb.provider.online.InsertVectorDbRecordData(
                                        **{
                                            "content": content,
                                            "metadata": metadata
                                        })
                                    # fmt: off
                                    encoded_path = vector_db_provider.save_record(request_body) # pylint: disable=E1111
                                    # fmt: on
                if encoded_path:
                    encoded_path_list.append(encoded_path)
                else:
                    encoded_path_list.append(server_faiss_write_path)
        elif not self.vector_collections:
            # Step 2 - Choose vector db provider
            vector_db_provider_config_data_dict = {
                'db_folder_path': server_faiss_write_path,
                'db_index_name': self.vector_db_name if self.vector_db_name else self.document_id,
            }
            vector_db_provider_config_data = infy_gen_ai_sdk.vectordb.provider.faiss.VectorDbProviderConfigData(
                **vector_db_provider_config_data_dict)
            vector_db_provider = infy_gen_ai_sdk.vectordb.provider.faiss.FaissVectorDbProvider(
                vector_db_provider_config_data, embedding_provider)

            for _key, chunked_method in self.chunk_data.items():
                for text_file_path in chunked_method.get('chunked_data_list'):
                    if f'{text_file_path}_metadata.json' in chunked_method.get('chunked_file_meta_data_list'):
                        metadata_file_path = f'{text_file_path}_metadata.json'
                        if metadata_file_path in chunked_method.get('chunked_file_meta_data_list', []):
                            metadata = json.loads(
                                self.__file_sys_handler.read_file(metadata_file_path))
                        else:
                            metadata = {}

                        # Add record(s) to vector db
                        db_record_data_dict = {
                            'content_file_path': text_file_path,
                            'metadata': metadata
                        }
                    db_record_data = infy_gen_ai_sdk.vectordb.provider.faiss.InsertVectorDbRecordData(
                        **db_record_data_dict)
                    vector_db_provider.save_record(db_record_data)

            encoded_path_list.append(server_faiss_write_path)

        return encoded_path_list
